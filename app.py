import streamlit as st
import gspread
import PyPDF2
import os
from oauth2client.service_account import ServiceAccountCredentials
import google.generativeai as genai
from datetime import datetime

# Configuración inicial
st.set_page_config(page_title="Chatbot del Curso DIAP", page_icon="🤖")

# Configurar Gemini
genai.configure(api_key=st.secrets["gemini_api_key"])
model = genai.GenerativeModel('gemini-pro')

# Ruta fija al PDF (ajusta esta ruta)
PDF_PATH = "./material_curso.pdf"  # O usa una ruta absoluta como "/home/usuario/documentos/curso.pdf"

# Conexión a Google Sheets
def conectar_sheets():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open_by_url(st.secrets["google_sheet_url"])

# Extraer texto de PDF
def extraer_texto_pdf(pdf_path):
    texto = ""
    try:
        with open(pdf_path, "rb") as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                texto += page.extract_text() + "\n"
        return texto
    except Exception as e:
        st.error(f"Error al leer el PDF: {str(e)}")
        return None

# Generar respuesta con Gemini
def generar_respuesta(pregunta, contexto_pdf):
    prompt = f"""
    Eres un asistente del Curso DIAP. Responde la pregunta del estudiante basándote en la siguiente información del curso:
    
    Contexto del curso:
    {contexto_pdf}
    
    Pregunta del estudiante: {pregunta}
    
    Proporciona una respuesta clara, concisa y útil. Si la pregunta no está relacionada con el curso, indícalo amablemente.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error al generar la respuesta: {str(e)}"

# Cargar el PDF al iniciar la app
@st.cache_resource
def cargar_contexto():
    if os.path.exists(PDF_PATH):
        return extraer_texto_pdf(PDF_PATH)
    else:
        st.error(f"No se encontró el PDF en la ubicación: {PDF_PATH}")
        return None

# Interfaz principal
def main():
    st.title("🤖 Chatbot del Curso DIAP")
    st.markdown("""
    Bienvenido al asistente virtual del curso. Haz tus preguntas sobre el material del curso.
    """)
    
    # Cargar contexto del PDF
    if 'contexto_pdf' not in st.session_state:
        contexto = cargar_contexto()
        if contexto:
            st.session_state['contexto_pdf'] = contexto
            st.success("Documento del curso cargado correctamente")
        else:
            st.stop()  # Detener la ejecución si no hay PDF
    
    # Formulario de preguntas
    with st.form("pregunta_form"):
        nombre = st.text_input("Nombre completo")
        correo = st.text_input("Correo electrónico")
        pregunta = st.text_area("Tu pregunta sobre el curso")
        
        submitted = st.form_submit_button("Enviar pregunta")
        
        if submitted:
            if not pregunta:
                st.warning("Por favor ingresa tu pregunta")
            else:
                with st.spinner("Buscando la mejor respuesta..."):
                    respuesta = generar_respuesta(pregunta, st.session_state['contexto_pdf'])
                    
                    # Mostrar respuesta
                    st.subheader("Respuesta")
                    st.markdown(respuesta)
                    
                    # Guardar en Google Sheets
                    if nombre and correo:
                        try:
                            doc = conectar_sheets()
                            hoja = doc.worksheet("Interacciones")
                            hoja.append_row([
                                nombre, 
                                correo, 
                                pregunta, 
                                respuesta,
                                str(datetime.now())
                            ])
                            st.success("Tu consulta ha sido registrada")
                        except Exception as e:
                            st.error(f"Error al guardar: {str(e)}")

if __name__ == "__main__":
    main()
