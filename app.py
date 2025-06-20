import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import PyPDF2
import google.generativeai as genai
import os

# ✅ Configuración de la página
st.set_page_config(page_title="Asistente 🤖", page_icon="🤖")

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
    Basado en el siguiente contexto sobre el Curso, responde la pregunta del usuario.
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

# 🗨️ Interfaz del chatbot
def chatbot():
    st.title("💬 Asistente del Curso Convierte a tus alumnos en Booktubers")

    # 🔔 Mensaje de advertencia e instrucciones
    st.info("""
    🔔 **Recomendaciones para usar el asistente correctamente**  

    Para obtener mejores resultados al interactuar con el asistente de respuestas, les pedimos tener en cuenta las siguientes recomendaciones:

    * Sean claros y específicos con la pregunta que formulan.  
    * Eviten enviar muchas preguntas al mismo tiempo. El sistema tiene un límite de consultas por minuto. Si realizan más de 10 preguntas en un minuto, a partir de la número 11 recibirán el mensaje automático: **"Error al generar respuesta"**

    🙏 ¡Gracias por su comprensión y por hacer un uso responsable de esta herramienta!
    """)

    nombre = st.text_input("🧑‍💼 ¿Cuál es tu nombre completo?")
    correo = st.text_input("📧 ¿Cuál es tu correo de registro?")
    pregunta = st.text_input("❓ ¿Qué te gustaría saber sobre el curso?")

    if st.button('💡 Preguntar'):
        if not pregunta:
            st.warning("⚠️ Por favor ingresa una pregunta")
            return
            
        respuesta = obtener_respuesta_gemini(pregunta)
        st.write(f"🧠 Respuesta: {respuesta}")

        try:
            documento = conectar_sheets()
            hoja_usuarios = documento.worksheet("Usuarios")
            hoja_usuarios.append_row([nombre, correo, pregunta, respuesta])
            st.success("✅ ¡Tu pregunta ha sido registrada!")
        except Exception as e:
            st.error(f"❌ Error al guardar en la hoja de cálculo: {str(e)}")

# ▶️ Ejecutar app
if __name__ == '__main__':
    chatbot()
