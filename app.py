import streamlit as st
import openai
import time

# Clave API desde secrets.toml (configurada en Streamlit Cloud)
openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_Gln1InMVBScTfNAyDAdWn6Dg"

# Título principal
st.markdown("<h1 style='text-align: center;'>🤖 ChatBali: Consulta tu Contrato Hospital Concesionario</h1>", unsafe_allow_html=True)

# Estilos CSS para mensajes de usuario y del asistente
st.markdown("""
    <style>
        .message-user {
            background-color: #DCF8C6;
            color: black;
            padding: 10px;
            border-radius: 10px;
            margin: 10px 0;
            max-width: 80%;
            align-self: flex-end;
        }
        .message-assistant {
            background-color: #F1F0F0;
            color: black;
            padding: 10px;
            border-radius: 10px;
            margin: 10px 0;
            max-width: 80%;
            align-self: flex-start;
        }
        .chat-container {
            display: flex;
            flex-direction: column;
        }
    </style>
""", unsafe_allow_html=True)

# Inicializa el thread una sola vez
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id

if "messages" not in st.session_state:
    st.session_state.messages = []

# Muestra el historial del chat
with st.container():
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        css_class = "message-user" if role == "user" else "message-assistant"
        st.markdown(f"<div class='{css_class}'>{content}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Entrada del usuario
user_input = st.chat_input("Escribe tu duda sobre el contrato...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Envía el mensaje al thread
    openai.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=user_input
    )

    # Ejecuta el Assistant con el vector store activado
    run = openai.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=ASSISTANT_ID,
        tool_resources={
            "file_search": {
                "vector_store_ids": ["vs_682f7eaf24881919751cfe9f20948"]
            }
        }
    )

    with st.spinner("Pensando..."):
        while True:
            status = openai.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
            if status.status == "completed":
                break
            elif status.status == "failed":
                st.error("❌ Falló la ejecución del Assistant")
                st.error(f"Motivo: {status.last_error}")
                break
            time.sleep(1)

    # Muestra la respuesta del asistente
    messages = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
    for msg in messages.data:
        if msg.role == "assistant":
            reply = msg.content[0].text.value
            st.session_state.messages.append({"role": "assistant", "content": reply})
            break
