import streamlit as st
import gspread
import difflib
from oauth2client.service_account import ServiceAccountCredentials

def conectar_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(st.secrets["spreadsheet_url"])
    return sheet

def cargar_faq():
    hoja = conectar_sheets().worksheet("FAQ")
    data = hoja.get_all_records()
    faq_dict = {
        fila["Pregunta"].strip().lower(): fila["Respuesta"].strip()
        for fila in data if fila.get("Pregunta") and fila.get("Respuesta")
    }
    return faq_dict

def encontrar_respuesta(pregunta_usuario, faq_dict):
    pregunta_usuario = pregunta_usuario.strip().lower()
    coincidencias = difflib.get_close_matches(pregunta_usuario, list(faq_dict.keys()), n=1, cutoff=0.6)
    if coincidencias:
        return faq_dict[coincidencias[0]]
    else:
        return "No entiendo la pregunta. ¿Podrías reformularla?"

def chatbot():
    st.title("🤖 Chatbot FAQ IIDEAC")

    st.markdown("Escribe tu duda exactamente como está en la hoja de cálculo.")
    pregunta_usuario = st.text_input("Haz tu pregunta:")

    if pregunta_usuario:
        faq_dict = cargar_faq()
        st.write("🛠️ Debug - Preguntas cargadas:", list(faq_dict.keys()))  # Puedes quitarlo luego
        respuesta = encontrar_respuesta(pregunta_usuario, faq_dict)
        st.write("**Respuesta:**", respuesta)

if __name__ == "__main__":
    chatbot()
