import streamlit as st
import gspread
import difflib
from oauth2client.service\_account import ServiceAccountCredentials

# Conexión a Google Sheets usando credenciales desde secrets.toml

def conectar\_sheets():
scope = \['[https://spreadsheets.google.com/feeds](https://spreadsheets.google.com/feeds)', '[https://www.googleapis.com/auth/drive](https://www.googleapis.com/auth/drive)']
creds\_dict = st.secrets\["gcp\_service\_account"]
creds = ServiceAccountCredentials.from\_json\_keyfile\_dict(creds\_dict, scope)
client = gspread.authorize(creds)
return client.open\_by\_url("[https://docs.google.com/spreadsheets/d/17Ku7gM-a3yVj41BiW8qUB44\_AG-qPO9i7CgOdadZ3GQ/edit](https://docs.google.com/spreadsheets/d/17Ku7gM-a3yVj41BiW8qUB44_AG-qPO9i7CgOdadZ3GQ/edit)")

# Cargar preguntas frecuentes desde la hoja "FAQ"

def cargar\_faq():
documento = conectar\_sheets()
hoja\_faq = documento.worksheet("FAQ")
data = hoja\_faq.get\_all\_records()
faq = {}
for item in data:
if 'pregunta' in item and 'respuesta' in item:
pregunta = item\['pregunta']
respuesta = item\['respuesta']
if isinstance(pregunta, str) and isinstance(respuesta, str):
faq\[pregunta.strip().lower()] = respuesta
return faq

# Interfaz del chatbot

def chatbot():
st.title("Curso DIAP")

```
nombre = st.text_input("¿Cuál es tu nombre completo?")
correo = st.text_input("¿Cuál es tu correo con el que te registraste?")
pregunta = st.text_input("¿Qué te gustaría saber sobre el curso?")

if st.button('Preguntar'):
    faq_dict = cargar_faq()
    pregunta_lower = pregunta.strip().lower()

    # Buscar pregunta más similar usando difflib
    preguntas_faq = list(faq_dict.keys())
    pregunta_similar = difflib.get_close_matches(pregunta_lower, preguntas_faq, n=1, cutoff=0.6)

    if pregunta_similar:
        respuesta = faq_dict[pregunta_similar[0]]
    else:
        respuesta = "No entiendo la pregunta. ¿Podrías reformularla?"

    st.write(f"Respuesta: {respuesta}")

    # Guardar datos del usuario en la hoja "Usuarios"
    documento = conectar_sheets()
    hoja_usuarios = documento.worksheet("Usuarios")
    hoja_usuarios.append_row([nombre, correo, pregunta, respuesta])
```

# Ejecutar la app

if **name** == '**main**':
chatbot()
