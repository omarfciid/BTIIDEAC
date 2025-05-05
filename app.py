import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

# Función para validar CURP (expresión regular)
def validar_curp(curp):
    patron = r"^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$"
    return re.match(patron, curp.upper()) is not None

# Conectar a Google Sheets usando las credenciales
def conectar_sheets():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credenciales.json', scope)
    client = gspread.authorize(creds)
    return client.open("FAQS")  # Cambia aquí si tu documento tiene otro nombre

# Obtener las preguntas frecuentes (FAQ) desde la hoja "FAQ"
def cargar_faq():
    documento = conectar_sheets()
    hoja_faq = documento.worksheet("FAQ")  # Usar nombre de la pestaña
    data = hoja_faq.get_all_records()
    faq = {}
    for item in data:
        faq[item['pregunta'].strip().lower()] = item['respuesta']
    return faq

# Interfaz de usuario con Streamlit
def chatbot():
    st.title("Chatbot del Curso")

    nombre = st.text_input("¿Cuál es tu nombre?")
    curp = st.text_input("Introduce tu CURP:")
    pregunta = st.text_input("¿Qué te gustaría saber sobre el curso?")

    if st.button('Preguntar'):
        if not validar_curp(curp):
            st.error("El CURP proporcionado no es válido. Por favor, verifica.")
        else:
            # Cargar las preguntas frecuentes desde Google Sheets
            faq_dict_
