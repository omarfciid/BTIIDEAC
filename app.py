import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import PyPDF2
import google.generativeai as genai
import os

# ✅ Configuración de la página
st.set_page_config(page_title="Bot Hidalgo 🤖", page_icon="🤖")

# 🔐 Configuración de Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# 📄 Ruta al PDF con la información del curso
PDF_PATH = "Respuesta.pdf"

# 🔗 Conexión a Google Sheets
def conectar_sheets():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_url("https://docs.google.com/spreadsheets/d/17Ku7gM-a3yVj41BiW8qUB44_AG-qPO9i7CgOdadZ3GQ/edit")

# 🧠 Extraer texto del PDF
def extraer_texto_pdf(ruta_pdf):
    texto = ""
    with open(ruta_pdf, 'rb') as archivo:
        lector = PyPDF2.PdfReader(archivo)
        for pagina in lector.pages:
            texto += pagina.extract_text()
    return texto

# 🤖 Obtener respuesta de Gemini basada en el PDF
def obtener_respuesta_gemini(pregunta):
    contexto = extraer_texto_pdf(PDF_PATH)
    
    prompt = f"""
    Basado en el siguiente contexto sobr

