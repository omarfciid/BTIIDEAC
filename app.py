import streamlit as st
import gspread
import difflib
from oauth2client.service_account import ServiceAccountCredentials

# Conexión a Google Sheets usando credenciales desde secrets.toml
def conectar_sheets():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open_by_url("https://docs.google.com/spreadsheets/d/17Ku7gM-a3yVj41BiW8qUB44_AG-qPO9i7CgOdadZ3GQ/edit")

# Cargar preguntas frecuentes desde la hoja "FAQ"
def cargar_faq():
    documento = conectar_sheets()
    hoja_faq = documento.worksheet("FAQ")
    data = hoja_faq.get_all_records()
    faq = {}
    for item in data:
        if 'Pregunta' in item and 'Respuesta' in item:
            pregunta = item['pregunta']
            respuesta = item['respuesta']
            if isinstance(pregunta, str) and isinstance(respuesta, str):
                faq[pregunta.strip().lower()] = respuesta
    return faq

# Interfaz del chatbot
def chatbot():
    st.title("Curso DIAP")

    nombre = st.text_input("¿Cuál es tu nombre completo?")
    correo = st.text_input("¿Cuál es tu correo con el que te registraste?")
    pregunta = st.text_input("¿Qué te gustaría saber sobre el curso?")

    if st.button('Preguntar'):
        faq_dict = cargar_faq()
        pregunta_lower = pregunta.strip().lower()
        respuesta = faq_dict.get(pregunta_lower, "No entiendo la pregunta. ¿Podrías reformularla?")
        st.write(f"respuesta: {respuesta}")

        # Guardar datos del usuario en la hoja "Usuarios"
        documento = conectar_sheets()
        hoja_usuarios = documento.worksheet("Usuarios")
        hoja_usuarios.append_row([nombre, correo, pregunta, respuesta])

# Ejecutar la app
if __name__ == '__main__':
    chatbot()
