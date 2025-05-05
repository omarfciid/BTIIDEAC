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
    return client.open("FAQS")  # Nombre del documento de Google Sheets

# Obtener las preguntas frecuentes (FAQ) desde la hoja de Google Sheets
def cargar_faq():
    documento = conectar_sheets()
    hoja_faq = documento.get_worksheet(0)  # Primera hoja
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
            faq_dict = cargar_faq()

            # Obtener la respuesta o un mensaje por defecto si no hay respuesta
            pregunta_lower = pregunta.strip().lower()
            respuesta = faq_dict.get(pregunta_lower, "No entiendo la pregunta. ¿Podrías reformularla?")

            # Mostrar la respuesta
            st.write(f"Respuesta: {respuesta}")

            # Guardar los datos del usuario en la hoja de Google Sheets
            documento = conectar_sheets()
            hoja_usuarios = documento.get_worksheet(1)  # Segunda hoja
            hoja_usuarios.append_row([nombre, curp.upper(), pregunta, respuesta])

# Ejecutar el chatbot
if __name__ == '__main__':
    chatbot()
