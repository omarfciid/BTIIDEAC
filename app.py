import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
api_key = st.secrets["OPENAI_API_KEY"]

# Función para validar CURP (expresión regular)
def validar_curp(curp):
    patron = r"^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$"
    return re.match(patron, curp.upper()) is not None

# Conectar a Google Sheets usando las credenciales
def conectar_sheets():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict({
        "type": "service_account",
        "project_id": "botiideac",
        "private_key_id": "7726870f309a5183af0ebc0e132a717941f5a76c",
        "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC6j92F4B1ihkqjiUuvpr3rPZABIzczSoH83KtM/EV9PGeS93AqsvFWW6g9f6k/02MeF7iQVmMPGFODYkzSO+QFilmwnti2ZZk+HUlWKwr53LwNRRfjanxa0REvIV/QPbDROfCAwovhd0HUUHU3m/BhmshVbLLw2pFa5HQo7Zvf9fsZtpSEtNm/bpb+Lt2Ugyt66jGjZekNjIktDlLcj5EqO8PqWUuyJeLgpAvhaSf3bMMVwDx2zuGRn7ha57Vqz90Xem06MgTzj7c/wLJ7PbZcLXnFS4ioI49RxzPMnsaDwrt8W4LpadgLwdpO0Q+UBi/qONCJiYkOMOfnLkivVm+PAgMBAAECggEAAoMebgeTDbkWNzaJlN9vbkQBdOp2+1NVBcUo71v0SZfvIxz+3yxSsKGCVfWqn0fm7UhPfW4UXmcq9Ll1pF0XGHYA+C5jZ61dj2cQjj79Ilk1FQ6poC/WZdir3REbe6/g+ihIE0vLW2liMww0T9/jMEVHzlKs5C5lR66M2+I7N5xP9RWQ6PHYlJ49xMo7EpMAU9iv6qmgG7DIzsvM+tVq7z2HU0z6HXRLEfGFZodV4yPdwlDYLyzTzoiTRcmtGhYmMXZVjn6BIPUZs/hNBYi3dNwr4e5lXsiKXiQ0jONb0qtmDcdXmYdqdodu8z/uiuM7g1AoHMyqFe4s0vFiMvzybQKBgQDmCTY847G1j6aF2azxx2DY+PbhbWs11nZ6pXaLadE/O/+Cyryz+6hBRvjVg+58Rq//h5lgONaxxse6xf92wCMX16ak00UAd7Zu+jRskyhOlXgFhUm750qcx6OJpU9H4x8fRAt2FNYELoSGy275hHo1Z9PLRg7U6/YA6mNKzG38SwKBgQDPnn27tITNUQxFDwqXTFCejdb0JwcYXPkxm0mFajc1KpVvu0yy2xFsJ+3VBvckOk8kGcw1cAF5g6l89/xwDMu6e93uKbNBRIVmtc9JABdwT7yix2VbRy7EzGcNxUnG2bi4ve1Pu3sHFIfiU7LKQYG1mdegLoNLYrLHVX+saOKHTQKBgB1cfaTF90/SVxHsl8uAhFcNaA2b9rw3dIXxCrF+vyuQD+v0zqM2cuJqGaa/ITiRmTNHboc+mgC0+5dWYGYa3h/T8bxGDx+hKBMAMqLNIa7uGxSxT5kBS5+5R6FxDS6Cyd0mxUO8IxkDivzdiHumsiaQ6xKeDZSVzZ+OS0An2b4DAoGBAL1wKd1Za0tDxmREwy8l7PGfDiEcczbhrmZ7AGyBa/pQ7qVSSztu88ix7ipP/rTJl2ijOVcQ6eeMINvsEiPTKRjw6KDk37CP6wC6p3Y+ZSSPPNlyAqN0odHjh6xi9VxBUHEQqzXzJOBi9VGneR1fBBFFXB/GEPp6BhIniyUvVnKJAoGAT6nZ3imCaFj1aZ+uL5Rk8CXmxD52J2Lv4o3F6PUinuZ0tdVAe3QZ51mAYDAd7SiRsohW6uPQH8rupZqrsxgNq4D7VBihc1xObnPKS2ub6iEWmG+2wK+40d5bc2LlC/CFtRXujh+MtUfo4ofkRBcemYIsdUvk6lo7RNv3cqeZ8pE=-----END PRIVATE KEY-----"""
        "client_email": "botiideac@botiideac.iam.gserviceaccount.com",
        "client_id": "106818133155189707697",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/botiideac%40botiideac.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }, scope)
    
    client = gspread.authorize(creds)
    return client.open("FAQ")  # Cambia aquí si tu documento tiene otro nombre

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
    st.title("Chatbot")

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
            hoja_usuarios = documento.worksheet("Usuarios")  # Usar nombre de la pestaña
            hoja_usuarios.append_row([nombre, curp.upper(), pregunta, respuesta])

# Ejecutar el chatbot
if __name__ == '__main__':
    chatbot()
