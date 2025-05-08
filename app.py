Mi siguiente código está así, pero me arroja un mensaje de que no se encontró la respuesta: Respuesta: No entiendo la pregunta. ¿Podrías reformularla?

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
return client.open\_by\_url("[https://docs.google.com/spreadsheets/d/17Ku7gM-a3yVj41BiW8qUB44\_AG-qPO9i7CgOdadZ3GQ/edit](https://docs.google.com/spreadsheets/d/17Ku7gM-a3yVj41BiW8qUB44_AG-qPO9i7CgOdadZ3GQ/edit)") # Cambia aquí si el nombre del documento es diferente

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
    respuesta = faq_dict.get(pregunta_lower, "No entiendo la pregunta. ¿Podrías reformularla?")
    st.write(f"Respuesta: {respuesta}")

    # Guardar datos del usuario en la hoja "Usuarios"
    documento = conectar_sheets()
    hoja_usuarios = documento.worksheet("Usuarios")
    hoja_usuarios.append_row([nombre, correo, pregunta, respuesta])
```

# Ejecutar la app

if **name** == '**main**':
chatbot()
