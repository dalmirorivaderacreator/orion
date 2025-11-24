import streamlit as st
import pandas as pd
import time
from dotenv import load_dotenv
from llm_client import ask_orion
from dispatcher import dispatch
from registry import get_available_functions
from context import ContextManager
from planner import HybridTaskPlanner
from runner import execute_plan
from logger import logger
import database

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="ORION Enterprise",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS
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

# ... imports ...
from conversation import ConversationManager

# ... setup ...

# Inicializar estado
if "messages" not in st.session_state:
    st.session_state.messages = []
if "context" not in st.session_state:
    st.session_state.context = ContextManager()
if "conversation" not in st.session_state:
    st.session_state.conversation = ConversationManager(st.session_state.context)

# ... sidebar ...

# --- MAIN AREA ---
tab1, tab2, tab3 = st.tabs(["💬 Chat & Ejecución", "📜 Historial", "⚙️ Cerebro"])

# TAB 1: CHAT
with tab1:
    st.header("Centro de Comando")
    st.info("💡 **Tip:** Escribe 'Ayuda' para ver una lista de comandos o 'Creá proyecto web' para empezar.")
    
    # Mostrar historial de chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "result" in message:
                result = message["result"]
                if isinstance(result, list): # Es un plan
                    with st.expander("✅ Ver Detalles del Plan"):
                        for res in result:
                            st.text(res)
                elif isinstance(result, str) and result.startswith("[OK]"):
                    st.success(result)
                elif isinstance(result, str) and result.startswith("[ERROR]"):
                    st.error(result)
                else:
                    st.code(result)

    # Input Usuario
    if prompt := st.chat_input("Escribe una instrucción o saluda..."):
        # 1. Mostrar User Msg
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Procesar con ConversationManager
        with st.chat_message("assistant"):
            with st.spinner("🧠 Procesando..."):
                response = st.session_state.conversation.process(prompt)
            
            # A. Mensaje simple (Greeting/Chat/Question)
            if response["type"] == "message":
                st.markdown(response["response"])
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["response"]
                })
                
            # B. Plan Complejo
            elif response["type"] == "plan":
                st.info(f"📋 **Plan Maestro Detectado**")
                
                # Visualización de Ejecución (Re-implementada para usar los resultados ya obtenidos o re-ejecutar si el manager no devuelve stream)
                # Nota: El manager actual ejecuta todo de una. Para visualización paso a paso en UI, 
                # idealmente el manager debería devolver el plan y dejar que la UI lo ejecute, 
                # O devolver los resultados. Aquí ya devuelve los resultados ejecutados.
                # Para mantener la animación bonita, podríamos simularla o refactorizar.
                # Por simplicidad ahora, mostramos los resultados.
                
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

            # C. Acción Simple
            elif response["type"] == "action":
                st.markdown(f"🎯 Acción Ejecutada")
                result = response["result"]
                
                if str(result).startswith("[OK]"):
                    st.success(result)
                elif str(result).startswith("[ERROR]"):
                    st.error(result)
                else:
                    st.markdown(result)
                    
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["response"],
                    "result": result
                })
                st.rerun()
                
            # D. Error
            else:
                st.warning(response["response"])
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["response"]
                })

# TAB 2: HISTORIAL
with tab2:
    st.header("📜 Historial de Operaciones")
    history_data = database.get_history(50)
    if history_data:
        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay historial aún.")

# TAB 3: CEREBRO
with tab3:
    st.header("⚙️ Estado del Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Variables de Contexto")
        st.json(st.session_state.context.context)
        
    with col2:
        st.subheader("Preferencias Guardadas")
        # TODO: Agregar get_all_preferences en database.py si se quiere mostrar todo
        st.info("Las preferencias se cargan bajo demanda.")
