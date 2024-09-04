# Importaciones necesarias
import os
import tempfile
import streamlit as st
from streamlit_chat import message
from rag import ChatPDF

# Configuración de la página de Streamlit
st.set_page_config(page_title="ChatPDF")

# Función para mostrar los mensajes del chat
def display_messages():
    """
    Muestra los mensajes del chat.

    Esta función se encarga de mostrar en la pantalla los mensajes
    que se han ido escribiendo en el chat. Se utiliza para mantener
    una interfaz de usuario sencilla y fácil de usar.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    
    st.subheader("Chat")
    for i, (msg, is_user) in enumerate(st.session_state["messages"]):
        message(msg, is_user=is_user, key=str(i))
    st.session_state["thinking_spinner"] = st.empty()

# Función para procesar la entrada del usuario
def process_input():
    """
    Process the user's input.

    If the user has entered any text, this function will ask the agent for a response
    and update the chat history.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    if st.session_state["user_input"] and len(st.session_state["user_input"].strip()) > 0:
        user_text = st.session_state["user_input"].strip()
        with st.session_state["thinking_spinner"], st.spinner("Thinking..."):
            agent_text = st.session_state["assistant"].ask(user_text)

        st.session_state["messages"].append((user_text, True))
        st.session_state["messages"].append((agent_text, False))

# Función para leer y guardar el archivo PDF
def read_and_save_file():
    """
    Clears the chat history and ingests the uploaded PDF files.

    This function is called whenever the user uploads a new file.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    st.session_state["assistant"].clear()
    st.session_state["messages"] = []
    st.session_state["user_input"] = ""

    for file in st.session_state["file_uploader"]:
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(file.getbuffer())
            file_path = tf.name

        with st.session_state["ingestion_spinner"], \
                st.spinner(f"Ingesting {file.name}"):
            st.session_state["assistant"].ingest(file_path)
        os.remove(file_path)

# Función principal de la página
def page():
    """
    Main function for the Streamlit page.

    This function is called whenever the page is loaded or reloaded.

    It initializes the chat history and the assistant object if they don't exist,
    and then displays the header and the file uploader.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    if len(st.session_state) == 0:
        st.session_state["messages"] = []
        st.session_state["assistant"] = ChatPDF()

    st.header("ChatPDF")

    st.subheader("Upload a document")
    st.file_uploader(
        "Upload document",
        type=["pdf"],
        key="file_uploader",
        on_change=read_and_save_file,
        label_visibility="collapsed",
        accept_multiple_files=True,
    )

    st.session_state["ingestion_spinner"] = st.empty()

    display_messages()
    st.text_input("Message", key="user_input", on_change=process_input)

# Punto de entrada del script
if __name__ == "__main__":
    page()
