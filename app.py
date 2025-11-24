"""
Main application file for ORION Enterprise.
Streamlit-based dashboard for interacting with the assistant.
"""
import streamlit as st  # Third-party
import pandas as pd  # Third-party
from dotenv import load_dotenv  # Third-party

# Local imports
import database
from context import ContextManager
from conversation import ConversationManager
from registry import get_available_functions
# pylint: disable=unused-import
from functions import data_ops, file_ops, system_ops, email_ops

# Load environment variables
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="ORION Enterprise",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Styles
st.markdown("""
    <style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #f0f2f6;
        border-left: 5px solid #4a90e2;
    }
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #e8f0fe;
        border-left: 5px solid #50c878;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "context" not in st.session_state:
    st.session_state.context = ContextManager()
if "conversation" not in st.session_state:
    st.session_state.conversation = ConversationManager(st.session_state.context)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🌌 ORION Enterprise")
    st.markdown("---")

    # Metrics
    history = database.get_history(100)
    total_cmds = len(history)
    SUCCESS_RATE = "100%"  # Placeholder

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Comandos", total_cmds)
    with col2:
        st.metric("Éxito", SUCCESS_RATE)

    st.markdown("---")

    # Active Context
    st.subheader("🧠 Memoria Activa")
    ctx = st.session_state.context.context
    if ctx.get("last_folder"):
        st.info(f"📂 Carpeta: `{ctx['last_folder']}`")
    else:
        st.warning("📂 Sin carpeta activa")

    st.markdown("---")
    with st.expander("🛠️ Funciones Disponibles"):
        functions = get_available_functions()
        for name, info in functions.items():
            st.markdown(f"**{name}**")
            st.caption(info['description'])

# --- MAIN AREA ---
tab1, tab2, tab3 = st.tabs(["💬 Chat & Ejecución", "📜 Historial", "⚙️ Cerebro"])

# TAB 1: CHAT
with tab1:
    st.header("Centro de Comando")
    st.info(
        "💡 **Tip:** Escribe 'Ayuda' para ver una lista de comandos "
        "o 'Creá proyecto web' para empezar."
    )

    # Show chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "result" in message:
                result_val = message["result"]
                if isinstance(result_val, list):  # Plan
                    with st.expander("✅ Ver Detalles del Plan"):
                        for res in result_val:
                            st.text(res)
                elif isinstance(result_val, str) and result_val.startswith("[OK]"):
                    st.success(result_val)
                elif isinstance(result_val, str) and result_val.startswith("[ERROR]"):
                    st.error(result_val)
                else:
                    st.code(result_val)

    # User Input
    if prompt := st.chat_input("Escribe una instrucción o saluda..."):
        # 1. Show User Msg
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Process with ConversationManager
        with st.chat_message("assistant"):
            with st.spinner("🧠 Procesando..."):
                response = st.session_state.conversation.process(prompt)

            # A. Simple Message
            if response["type"] == "message":
                st.markdown(response["response"])
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["response"]
                })

            # B. Complex Plan
            elif response["type"] == "plan":
                st.info("📋 **Plan Maestro Detectado**")

                with st.expander("🚀 Resultados de Ejecución", expanded=True):
                    for res in response["result"]:
                        if str(res).startswith("[OK]"):
                            st.success(res)
                        elif str(res).startswith("[ERROR]"):
                            st.error(res)
                        else:
                            st.write(res)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["response"],
                    "result": response["result"]
                })
                st.rerun()

            # C. Simple Action
            elif response["type"] == "action":
                st.markdown("🎯 Acción Ejecutada")
                result_val = response["result"]

                if str(result_val).startswith("[OK]"):
                    st.success(result_val)
                elif str(result_val).startswith("[ERROR]"):
                    st.error(result_val)
                else:
                    st.markdown(result_val)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["response"],
                    "result": result_val
                })
                st.rerun()

            # D. Error
            else:
                st.warning(response["response"])
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["response"]
                })

# TAB 2: HISTORY
with tab2:
    st.header("📜 Historial de Operaciones")
    history_data = database.get_history(50)
    if history_data:
        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay historial aún.")

# TAB 3: BRAIN
with tab3:
    st.header("⚙️ Estado del Sistema")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Variables de Contexto")
        st.json(st.session_state.context.context)

    with col2:
        st.subheader("Preferencias Guardadas")
        st.info("Las preferencias se cargan bajo demanda.")
