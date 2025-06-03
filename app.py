import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import difflib

# Conectar a Google Sheets con credenciales desde st.secrets
def conectar_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_url(st.secrets["spreadsheet_url"])

# Cargar preguntas frecuentes desde la hoja "FAQ"
def cargar_faq():
    hoja_faq = conectar_sheets().worksheet("FAQ")
    data = hoja_faq.get_all_records()
    faq = {}
    for item in data:
        pregunta = item.get("pregunta", "").strip().lower()
        respuesta = item.get("respuesta", "").strip()
        if pregunta and respuesta:
            faq[pregunta] = respuesta
    return faq

# Interfaz del chatbot
def chatbot():
    st.title("🤖 Chatbot Curso DIAP")

    nombre = st.text_input("¿Cuál es tu nombre completo?")
    correo = st.text_input("¿Cuál es tu correo con el que te registraste?")
    pregunta = st.text_input("¿Qué te gustaría saber sobre el curso?")

    if st.button("Preguntar"):
        if not nombre or not correo or not pregunta:
            st.warning("Por favor, completa todos los campos antes de preguntar.")
            return

        faq_dict = cargar_faq()
        pregunta_normalizada = pregunta.strip().lower()
        posibles = list(faq_dict.keys())
        coincidencias = difflib.get_close_matches(pregunta_normalizada, posibles, n=1, cutoff=0.6)

        if coincidencias:
            mejor_pregunta = coincidencias[0]
            respuesta = faq_dict[mejor_pregunta]
        else:
            respuesta = "No entiendo la pregunta. ¿Podrías reformularla?"

        st.markdown(f"**Respuesta:** {respuesta}")

        # Guardar interacción en la hoja "Usuarios"
        hoja_usuarios = conectar_sheets().worksheet("Usuarios")
        hoja_usuarios.append_row([nombre, correo, pregunta, respuesta])

# Ejecutar la app
if __name__ == "__main__":
    chatbot()
