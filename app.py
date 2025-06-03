import streamlit as st
import gspread
import difflib
from oauth2client.service_account import ServiceAccountCredentials

# 🔐 Conexión a Google Sheets
def conectar_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open_by_url(st.secrets["spreadsheet_url"])

# 📄 Cargar preguntas/respuestas
def cargar_faq():
    hoja_faq = conectar_sheets().worksheet("FAQ")
    data = hoja_faq.get_all_records()
    return {fila["Pregunta"].strip(): fila["Respuesta"] for fila in data if "Pregunta" in fila and "Respuesta" in fila}

# 🤖 Buscar respuesta más cercana
def encontrar_respuesta(pregunta_usuario, faq_dict):
    preguntas = list(faq_dict.keys())
    coincidencias = difflib.get_close_matches(pregunta_usuario.strip(), preguntas, n=1, cutoff=0.5)
    if coincidencias:
        return faq_dict[coincidencias[0]]
    else:
        return "No entiendo la pregunta. ¿Podrías reformularla?"

# 🎛️ Interfaz del bot
def chatbot():
    st.title("🤖 Chatbot FAQ IIDEAC")

    pregunta_usuario = st.text_input("Haz tu pregunta:")
    if pregunta_usuario:
        faq_dict = cargar_faq()
        respuesta = encontrar_respuesta(pregunta_usuario, faq_dict)
        st.write("**Respuesta:**", respuesta)

# ▶️ Ejecutar
if __name__ == "__main__":
    chatbot()
