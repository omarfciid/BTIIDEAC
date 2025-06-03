import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import PyPDF2
import google.generativeai as genai
import os

# Configuración de Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

# Ruta del PDF con la información del curso (cambia esta ruta)
PDF_PATH = "Respuesta.pdf"

# Conexión a Google Sheets (igual que antes)
def conectar_sheets():
    scope = ['https://spreadsheets.google.com/feed','https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open_by_url("https://docs.google.com/spreadsheets/d/17Ku7gM-a3yVj41BiW8qUB44_AG-qPO9i7CgOdadZ3GQ/edit")

# Extraer texto del PDF
def extraer_texto_pdf(ruta_pdf):
    texto = ""
    with open(ruta_pdf, 'rb') as archivo:
        lector = PyPDF2.PdfReader(archivo)
        for pagina in lector.pages:
            texto += pagina.extract_text()
    return texto

# Obtener respuesta de Gemini basada en el PDF
def obtener_respuesta_gemini(pregunta):
    # Extraer texto del PDF
    contexto = extraer_texto_pdf(PDF_PATH)
    
    # Crear prompt para Gemini
    prompt = f"""
    Basado en el siguiente contexto sobre el Curso DIAP, responde la pregunta del usuario.
    Si la pregunta no puede responderse con el contexto, indica que no tienes información suficiente.

    Contexto:
    {contexto}

    Pregunta: {pregunta}
    Respuesta:"""
    
    try:
        respuesta = model.generate_content(prompt)
        return respuesta.text
    except Exception as e:
        return f"Error al generar respuesta: {str(e)}"

# Interfaz del chatbot
def chatbot():
    st.title("Curso DIAP - Chatbot con IA")

    nombre = st.text_input("¿Cuál es tu nombre completo?")
    correo = st.text_input("¿Cuál es tu correo con el que te registraste?")
    pregunta = st.text_input("¿Qué te gustaría saber sobre el curso?")

    if st.button('Preguntar'):
        if not pregunta:
            st.warning("Por favor ingresa una pregunta")
            return
            
        # Obtener respuesta de Gemini
        respuesta = obtener_respuesta_gemini(pregunta)
        
        # Mostrar respuesta
        st.write(f"Respuesta: {respuesta}")

        # Guardar datos del usuario en Google Sheets
        try:
            documento = conectar_sheets()
            hoja_usuarios = documento.worksheet("Usuarios")
            hoja_usuarios.append_row([nombre, correo, pregunta, respuesta])
            st.success("¡Tu pregunta ha sido registrada!")
        except Exception as e:
            st.error(f"Error al guardar en la hoja de cálculo: {str(e)}")

# Ejecutar la app
if __name__ == '__main__':
    chatbot()
