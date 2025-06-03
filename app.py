import streamlit as st
import gspread
import difflib
import unicodedata
from google.oauth2.service_account import Credentials

# Normaliza texto para comparación
def normalizar(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    return texto

# Conexión a Google Sheets con google-auth
def conectar_sheets():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_url(st.secrets["spreadsheet_url"])

# Cargar FAQ
def cargar_faq():
    hoja_faq = conectar_sheets().worksheet("FAQ")
    datos = hoja_faq.get_all_records()
    faq = {}
    for fila in datos:
        pregunta = fila.get("pregunta", "").strip()
        respuesta = fila.get("respuesta", "").strip()
        if pregunta and respuesta:
            faq[pregunta] = respuesta
    return faq

# Chatbot principal
def chatbot():
    st.title("🤖 Curso DIAP – Asistente Virtual")

    nombre = st.text_input("👤 ¿Cuál es tu nombre completo?")
    correo = st.text_input("📧 ¿Cuál es tu correo con el que te registraste?")
    pregunta = st.text_input("❓ ¿Qué te gustaría saber sobre el curso?")

    if st.button("Preguntar"):
        faq_dict = cargar_faq()
        pregunta_normalizada = normalizar(pregunta)
        claves_originales = list(faq_dict.keys())
        claves_normalizadas = [normalizar(k) for k in claves_originales]

        coincidencias = difflib.get_close_matches(pregunta_normalizada, claves_normalizadas, n=1, cutoff=0.6)

        if coincidencias:
            idx = claves_normalizadas.index(coincidencias[0])
            mejor_pregunta = claves_originales[idx]
            respuesta = faq_dict[mejor_pregunta]
        else:
            respuesta = "No entiendo la pregunta. ¿Podrías reformularla?"

        st.write(f"**💬 Respuesta:** {respuesta}")

        try:
            hoja_usuarios = conectar_sheets().worksheet("Usuarios")
            hoja_usuarios.append_row([nombre, correo, pregunta, respuesta])
        except Exception as e:
            st.error(f"❗ Error al guardar en hoja de usuarios: {e}")

if __name__ == "__main__":
    chatbot()
