import streamlit as st
import openai
import time

# Clave API desde secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = "asst_Gln1InMVBScTfNAyDAdWn6Dg"

# Título
st.markdown("<h1 style='text-align: center;'>🤖 ChatBali: Consulta tu contrato</h1>", unsafe_allow_html=True)

# Estilos CSS tipo chat moderno
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

# Inicializa thread
if "thread_id" not in st.session_state:
    thread = openai.beta.threads.create()
    st.session_state.thread_id = thread.id

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial de chat
with st.container():
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        css_class = "message-user" if role == "user" else "message-assistant"
        st.markdown(f"<div class='{css_class}'>{content}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Entrada sin filtro
user_input = st.chat_input("Escribe tu duda sobre el contrato...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    openai.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=user_input
    )

    # Incluye vector store (archivo cargado)
    run = openai.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=ASSISTANT_ID,
        tool_resources={
            "file_search": {
                "vector_store_ids": ["vs_6827fea4f24881919751c6f9f20948"]
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

    messages = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
    for msg in messages.data:
        if msg.role == "assistant":
            reply = msg.content[0].text.value
            st.session_state.messages.append({"role": "assistant", "content": reply})
            break
