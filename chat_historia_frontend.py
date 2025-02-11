#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Aplicación frontend en Streamlit para interactuar con el chat conversacional.
El usuario ingresa su nombre para iniciar la sesión, se obtiene su historial y
se permite enviar mensajes al chat. Además, se muestra el historial en orden
descendente y se dispone de un botón para salir del chat.
"""

import json

import requests
import streamlit as st

# URL base de la API Gateway donde se encuentra desplegada la función Lambda
API_URL = "https://xrpqa9btfi.execute-api.us-east-2.amazonaws.com/dev"
# API Key para la API Rest
API_KEY = "esytondutk1dl1aDODxwj1GUxuAGi4lo87rCJK5J"


def iniciar_chat(usuario, llm="OpenAI"):
    """
    Llama al endpoint /chat/iniciar para registrar o recuperar el usuario.

    Parámetros:
      usuario (str): Nombre del usuario.
      llm (str): Modelo LLM a utilizar ("OpenAI" o "DeepSeek").

    Retorna:
      thread_id (str) si la operación es exitosa, None en caso contrario.
    """
    url = f"{API_URL}/chat-historia/iniciar"
    payload = {"usuario": usuario, "llm": llm}
    headers = {"Content-Type": "application/json", "x-api-key": API_KEY}
    respuesta = requests.post(url, data=json.dumps(payload), headers=headers)
    if respuesta.status_code == 200:
        datos = respuesta.json()
        return datos.get("thread_id")
    else:
        st.error("Error al iniciar el chat: " + respuesta.text)
        return None


def enviar_mensaje(usuario, pregunta, llm="OpenAI"):
    """
    Llama al endpoint /chat/enviar-mensaje para enviar una pregunta y obtener la respuesta.

    Parámetros:
      usuario (str): Nombre del usuario.
      pregunta (str): Pregunta que se envía al chat.
      llm (str): Modelo LLM a utilizar.

    Retorna:
      respuesta (str): Respuesta generada por el modelo, o None en caso de error.
    """
    url = f"{API_URL}/chat-historia/enviar-mensaje"
    payload = {"usuario": usuario, "pregunta": pregunta, "llm": llm}
    headers = {"Content-Type": "application/json", "x-api-key": API_KEY}
    respuesta = requests.post(url, data=json.dumps(payload), headers=headers)
    if respuesta.status_code == 200:
        datos = respuesta.json()
        return datos.get("respuesta")
    else:
        st.error("Error al enviar el mensaje: " + respuesta.text)
        return None


def obtener_historial(usuario, llm="OpenAI"):
    """
    Llama al endpoint /chat/historial para obtener el historial de la conversación.

    Parámetros:
      usuario (str): Nombre del usuario.
      llm (str): Modelo LLM a utilizar.

    Retorna:
      historial (list): Lista de mensajes del historial, o lista vacía en caso de error.
    """
    url = f"{API_URL}/chat-historia/historial"
    payload = {"usuario": usuario, "llm": llm}
    headers = {"Content-Type": "application/json", "x-api-key": API_KEY}
    respuesta = requests.post(url, data=json.dumps(payload), headers=headers)
    if respuesta.status_code == 200:
        datos = respuesta.json()
        return datos.get("historial", [])
    else:
        st.error("Error al obtener el historial: " + respuesta.text)
        return []


# =============================================================================
# Interfaz de usuario con Streamlit
# =============================================================================

st.title("Chat Conversacional con Historial")

# Inicializar variables de sesión para mantener el estado del usuario y el historial
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = None
if "historial" not in st.session_state:
    st.session_state["historial"] = []

# Vista para iniciar sesión (ingresar nombre de usuario)
if st.session_state["usuario"] is None:
    st.header("Iniciar Sesión")
    usuario = st.text_input("Ingrese su nombre de usuario")
    if st.button("Iniciar chat"):
        if usuario.strip() == "":
            st.error("El nombre de usuario no puede estar vacío")
        else:
            thread_id = iniciar_chat(usuario)
            if thread_id:
                st.session_state["usuario"] = usuario
                st.session_state["thread_id"] = thread_id
                # Obtener historial inicial (si existe)
                st.session_state["historial"] = obtener_historial(usuario)
                st.rerun()
else:
    st.header(f"Chat - Usuario: {st.session_state['usuario']}")
    # Botón para salir del chat y volver a la ventana de inicio
    if st.button("Salir del chat"):
        st.session_state["usuario"] = None
        st.session_state["thread_id"] = None
        st.session_state["historial"] = []
        st.rerun()

    # Inicializar el estado temporal si no existe
    if "temp_input" not in st.session_state:
        st.session_state["temp_input"] = ""

    # Área para ingresar una nueva pregunta
    pregunta = st.text_input(
        "Escribe tu pregunta:",
        value=st.session_state["temp_input"],
        key="pregunta_input",
    )
    if st.button("Enviar mensaje"):
        if pregunta.strip() != "":
            respuesta = enviar_mensaje(st.session_state["usuario"], pregunta)
            if respuesta:
                # Actualizar el historial agregando la pregunta y la respuesta (orden descendente)
                st.session_state["historial"].insert(
                    0, {"rol": "usuario", "contenido": pregunta}
                )
                st.session_state["historial"].insert(
                    1, {"rol": "IA", "contenido": respuesta}
                )
                # Limpiar el campo de entrada
                # st.session_state["pregunta_input"] = ""
                st.session_state["temp_input"] = ""  # Guardar un valor temporal
                st.rerun()  # Reiniciar la aplicación para limpiar el campo

    # Mostrar el historial de la conversación (más reciente primero)
    st.subheader("Historial de Conversación")
    for mensaje in st.session_state["historial"]:
        if mensaje["rol"] == "usuario":
            st.markdown(f"**Tú:** {mensaje['contenido']}")
        else:
            st.markdown(f"**IA:** {mensaje['contenido']}")
