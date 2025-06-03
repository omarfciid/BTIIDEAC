import streamlit as st
import gspread
import difflib
import unicodedata
from oauth2client.service_account import ServiceAccountCredentials

# ----------------------------
# FUNCIONES DE APOYO
# ----------------------------
st.write("🔍 Prueba: Spreadsheet URL =", st.secrets.get("spreadsheet_url", "NO DEFINIDO"))
st.write("🔍 Prueba: Client Email =", st.secrets["gcp_service_account"].get("client_email", "NO DEFINIDO"))
st.write("🔍 Prueba: Tiene clave privada =", "private_key" in st.secrets["gcp_service_account"])

def normalizar(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    return texto

# Conexión con Google Sheets
def conectar_sheets():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open_by_url(st.secrets["spreadsheet_url"])

# Cargar preguntas y respuestas
def cargar_faq():
    documento = conectar_sheets()
    hoja_faq = documento.worksheet("FAQ")
    data = hoja_faq.get_all_records()
    faq = {}
    for item in data:
        if 'pregunta' in item and 'respuesta' in item:
            pregunta = item['pregunta']
            respuesta = item['respuesta']
            if isinstance(pregunta, str) and isinstance(respuesta, str):
                faq[pregunta.strip()] = respuesta
    return faq

# ----------------------------
# INTERFAZ DEL CHATBOT
# ----------------------------

def chatbot():
    st.title("🤖 Curso DIAP – Asistente Virtual")

    nombre = st.text_input("👤 ¿Cuál es tu nombre completo?")
    correo = st.text_input("📧 ¿Cuál es tu correo con el que te registraste?")
    pregunta = st.text_input("❓ ¿Qué te gustaría saber sobre el curso?")

    if st.button('Preguntar'):
        faq_dict = cargar_faq()
        pregunta_usuario = pregunta.strip()
        pregunta_normalizada = normalizar(pregunta_usuario)

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

        # Guardar en hoja "Usuarios"
        try:
            documento = conectar_sheets()
            hoja_usuarios = documento.worksheet("Usuarios")
            hoja_usuarios.append_row([nombre, correo, pregunta_usuario, respuesta])
        except Exception as e:
            st.warning(f"No se pudo guardar la pregunta: {e}")

# ----------------------------
# INICIO
# ----------------------------

if __name__ == '__main__':
    chatbot()
