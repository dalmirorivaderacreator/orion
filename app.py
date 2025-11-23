import streamlit as st
# pylint: disable=unused-import
from dotenv import load_dotenv
from llm_client import ask_orion
from dispatcher import dispatch
from registry import get_available_functions
from functions import data_ops, file_ops, system_ops, email_ops
from context import ContextManager
from logger import logger

# Cargar variables de entorno
load_dotenv()


# Configuración de la página
st.set_page_config(
    page_title="ORION - AI Data Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #f0f2f6;
    }
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #e8f0fe;
    }
    </style>
""", unsafe_allow_html=True)

# Título y Descripción
st.title("🤖 ORION: AI Data Assistant")
st.markdown("### Tu traductor de Lenguaje Natural a Código Ejecutable")

# Sidebar con Funciones Disponibles
with st.sidebar:
    st.header("🛠️ Funciones Activas")
    functions = get_available_functions()
    for name, info in functions.items():
        with st.expander(f"🔹 {name}"):
            st.markdown(f"**Descripción:** {info['description']}")
            st.code(
                f"Args: {list(info['argument_types'].keys())}",
                language="json")

    st.divider()
    st.info("💡 ORION v2.0 - Running on LocalHost")

# Inicializar historial y contexto
if "messages" not in st.session_state:
    st.session_state.messages = []

if "context" not in st.session_state:
    st.session_state.context = ContextManager()

# Mostrar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "result" in message:
            result = message["result"]
            if isinstance(result, str):
                if result.startswith("✅"):
                    st.success(result)
                elif result.startswith("❌"):
                    st.error(result)
                else:
                    st.markdown(result)
            else:
                st.json(result)

# Input del usuario
if prompt := st.chat_input("¿Qué tarea querés ejecutar hoy?"):
    # 1. Mostrar mensaje usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Procesar con ORION
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🧠 *Pensando y analizando solicitud...*")

        try:
            # Llamada al LLM
            call_data = ask_orion(prompt, st.session_state.context)

            if call_data['CALL']:
                # Mostrar intención detectada
                st.success(f"🎯 Intención detectada: `{call_data['CALL']}`")
                with st.expander("🔍 Ver Argumentos Extraídos"):
                    st.json(call_data['ARGS'])

                # Ejecutar acción
                message_placeholder.markdown(
                    "⚙️ *Ejecutando acción segura...*")
                result = dispatch(
                    call_data['CALL'],
                    call_data['ARGS'],
                    st.session_state.context)

                # Mostrar resultado final
                message_placeholder.markdown("✅ **Ejecución Completada**")

                if isinstance(result, str):
                    if result.startswith("✅"):
                        st.success(result)
                    elif result.startswith("❌"):
                        st.error(result)
                    else:
                        st.markdown(result)
                else:
                    st.json(result)

                # Guardar en historial
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Ejecuté `{call_data['CALL']}` exitosamente.",
                    "result": result
                })

                logger.info(
                    "Interacción Web exitosa",
                    extra={"extra_data": {"prompt": prompt, "call": call_data}}
                )

            else:
                message_placeholder.error(
                    "❌ No pude interpretar esa instrucción.")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "No pude interpretar esa instrucción. Intenta ser más específico."
                })

        except Exception as e:
            message_placeholder.error(f"💥 Error crítico: {str(e)}")
            logger.error("Error en Web UI: %s", e, exc_info=True)
