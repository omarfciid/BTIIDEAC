import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import difflib

def conectar_sheets():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_url(st.secrets["spreadsheet_url"])

def cargar_faq():
    hoja_faq = conectar_sheets().worksheet("FAQ")
    data = hoja_faq.get_all_records()
    return {fila["Pregunta"]: fila["Respuesta"] for fila in data if "Pregunta" in fila and "Respuesta" in fila}

def encontrar_respuesta(pregunta_usuario, faq_dict):
    preguntas = list(faq_dict.keys())
    coincidencias = difflib.get_close_matches(pregunta_usuario, preguntas, n=1, cutoff=0.5)
    if coincidencias:
        return faq_dict[coincidencias[0]]
    else:
        return "No entiendo la pregunta. ¿Podrías reformularla?"

def chatbot():
    st.title("🤖 Chatbot FAQ IIDEAC")
    faq_dict = cargar_faq()
    pregunta_usuario = st.text_input("Haz tu pregunta:")
    if pregunta_usuario:
        respuesta = encontrar_respuesta(pregunta_usuario, faq_dict)
        st.write("**Respuesta:**", respuesta)

if __name__ == "__main__":
    chatbot()
