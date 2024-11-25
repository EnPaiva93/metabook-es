import os
import streamlit as st

from src.talker import Talker
from src.tts import TTS

import ffmpeg
from io import BytesIO

from datetime import timedelta
from datetime import datetime

import uuid


# ======================================================================================================================================
# Main Config Zone
# ======================================================================================================================================

st.set_page_config(layout="wide", initial_sidebar_state ="collapsed", page_title="Metabook")

hide_streamlit_style = """
            <style>
                .stMainBlockContainer {padding-top: 2rem; padding-bottom: 2rem;}
            </style>
            """

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Global constant
MAX_PODCAST = 5

# ======================================================================================================================================
# Aux Functions Zone
# ======================================================================================================================================


# ======================================================================================================================================
# Load Zone
# ======================================================================================================================================


# ======================================================================================================================================
# Prompt Zone
# ======================================================================================================================================

generation_prompt = """Usted es un escritor hispanohablante de podcast educativo de clase mundial, especializado en crear conversaciones atractivas y educativas sobre diversos temas. Su tarea es generar un diálogo de podcast entre dos oradores sobre el siguiente tema:


<tema>

{topic}

</tema>


Antes de comenzar el diálogo, planifique la estructura de la conversación dentro de las etiquetas <planificacion_podcast>. En esta sección:


1. Divida el tema en 3-5 subtemas principales para cubrir durante la conversación.

2. Para cada subtema, anote:

   - Una pregunta clave que el Orador 2 podría hacer.

   - Un punto principal que el Orador 1 debería explicar.

   - Una posible anécdota o analogía que el Orador 1 podría usar para ilustrar el punto.

   - 1-2 potenciales tangentes interesantes o preguntas inusuales que el Orador 2 podría plantear.

3. Planifique una introducción atractiva y una conclusión que resuma los puntos clave.

4. Sugiera 2-3 lugares donde el Orador 2 podría expresar confusión o pedir aclaraciones.

5. Planifique transiciones específicas entre cada subtema para mantener un flujo natural de la conversación.


Es aceptable que esta sección sea bastante larga para asegurar una planificación detallada.


Después de planificar la estructura, genere el diálogo siguiendo estas instrucciones:


1. Formato del diálogo:

   - Use "Orador 1:" y "Orador 2:" para indicar quién está hablando.

   - Incluya interrupciones naturales, como "ahh", "esss", "correcto", etc.

   - No incluya títulos de episodios o capítulos separados o los nombres de oradores.


2. Roles de los oradores:

   - Orador 1: Experto que dirige la conversación. Debe ser un profesor cautivador que ofrece explicaciones claras, anécdotas interesantes y analogías efectivas.

   - Orador 2: Aprendiz curioso que mantiene el hilo de la conversación haciendo preguntas de seguimiento. Debe mostrar entusiasmo y ocasionalmente confusión, haciendo preguntas de confirmación interesantes.


3. Estructura de la conversación:

   - Comience con una bienvenida atractiva y un resumen del tema por parte del Orador 1.

   - El Orador 2 debe hacer preguntas relevantes y ocasionalmente ir por tangentes interesantes o inusuales.

   - El Orador 1 debe responder con explicaciones claras, utilizando anécdotas y analogías para ilustrar los puntos.

   - Mantenga un equilibrio entre la información educativa y el entretenimiento.


4. Contenido:

   - Asegúrese de que la conversación se mantenga centrada en el tema principal, aunque se permiten breves desvíos.

   - Incluya datos precisos y actualizados sobre el tema.

   - Use ejemplos del mundo real para hacer el contenido más relatable y comprensible.


5. Tono:

   - Mantenga un tono educativo pero accesible y amigable.

   - La conversación debe ser informativa pero también entretenida y atractiva para el oyente.

   - Las oradoras son mujeres, pero el público es general.


Presente su respuesta en el siguiente formato:


<resultado>

[Escriba aquí el resultado del tema de forma estructurada como wikipedia]

</resultado>

<dialogo>

Orador 1: [Inserte aquí el diálogo del orador 1 en el podcast, comenzando directamente con el Orador 1 dando la bienvenida a los oyentes]

Orador 2: [Inserte aquí el diálogo del orador 2 en el podcast]

... [Continúe el diálogo completo del podcast con el mismo formato]

</dialogo>


Asegúrese de que el diálogo refleje la estructura planificada y cumpla con todas las instrucciones proporcionadas."""


# ======================================================================================================================================
# Session State Zone
# ======================================================================================================================================

if "books" not in st.session_state:
    st.session_state.books = []

if "messages" not in st.session_state:
    st.session_state.messages = {}

# ======================================================================================================================================
# Class Zone
# ======================================================================================================================================

class Process:
    
    def __init__(self, _id):

        self.idx = _id
        self.talker = Talker(prompt=generation_prompt)
        self.tts = TTS()

        if self.idx not in st.session_state:
            st.session_state.messages[self.idx] = {
                    "timestamp": datetime.now(),
                    "sound": {"path": None},
                    "user": {"content": None, "hidden": None}, 
                    "assistant": {"content": None, "hidden": None},
                } 

    def render(self):

        message = st.session_state.messages[self.idx]

        index = list(st.session_state.messages).index(self.idx)

        if not message["user"]["hidden"]:

            col_book, col_rem = st.columns([0.8, 0.1])

            with col_book:

                st.markdown(f"**Cuaderno {index+1}**")

            with col_rem:

                if st.button("X", key=f"new-init-{self.idx}",use_container_width=True):

                    del st.session_state.messages[self.idx]

                    st.session_state.books.remove(st.session_state.books[index])

                    st.rerun()
          
            col_user, col_sub = st.columns([0.8, 0.2])

            with col_user:
                
                user_input = st.text_input(
                    f"Books {index+1}",
                    placeholder="Ingresa tu tema:",
                    key=f"input-{self.idx}",
                    label_visibility="collapsed"
                )

            with col_sub:

                submit_button = st.button(f"Generar", key=f"submit-{self.idx}", use_container_width=True)

            if submit_button and user_input:
                
                st.session_state.messages[self.idx]["user"]["content"] = user_input

                max_retries = 3  # Número máximo de intentos
                
                retries = 0

                if not st.session_state.messages[self.idx]["assistant"]["content"]:
                
                    resultado, orador1_dialogos, orador2_dialogos, response = self.talker.response(user_input)
                    
                    while not (resultado and orador1_dialogos and orador2_dialogos):
                        retries += 1
                        if retries >= max_retries:
                            print("Error: Se alcanzó el límite máximo de reintentos.")
                            break
                        resultado, orador1_dialogos, orador2_dialogos, response = self.talker.response(user_input)                  

                    st.session_state.messages[self.idx]["assistant"]["content"] = [resultado, orador1_dialogos, orador2_dialogos, response]


            if isinstance(st.session_state.messages[self.idx]["assistant"]["content"], list):

                with st.expander("Ver Resultado"):

                    resultado = st.session_state.messages[self.idx]["assistant"]["content"][0] 
    
                    orador1_dialogos = st.session_state.messages[self.idx]["assistant"]["content"][1]
    
                    orador2_dialogos = st.session_state.messages[self.idx]["assistant"]["content"][2]

                    if not st.session_state.messages[self.idx]["sound"]["path"]:
    
                        sound_path = self.tts.generar_conversacion(self.idx, orador1_dialogos=orador1_dialogos, orador2_dialogos=orador2_dialogos, velocidad=1.2)
    
                        st.session_state.messages[self.idx]["sound"]["path"] = sound_path

                    else:

                        sound_path = st.session_state.messages[self.idx]["sound"]["path"]

                    st.audio(sound_path, format="audio/mpeg", autoplay=True)

                    st.markdown(resultado)                   
                    
                    st.session_state.messages[self.idx]["assistant"]["hidden"] = False
            
            st.divider()

# ======================================================================================================================================
# Web Zone
# ======================================================================================================================================

st.title("Metabook")

col_empty, col_exit = st.columns([0.8, 0.2])

with col_empty:

    st.write("Plataforma educativa de generación de conocimientos")

with col_exit:

    if st.button("Cerrar Sesión", key="button-end", use_container_width=True):

        st.switch_page("Main.py")    

st.divider()

if len(list(st.session_state.messages)) == 0:

    st.session_state.books.append(Process(str(uuid.uuid4())))

for book in st.session_state.books:

    book.render()

if len(list(st.session_state.messages)) < MAX_PODCAST:

    if st.button("Agregar cuaderno", key=f"add-cuad"):

        st.session_state.books.append(Process(str(uuid.uuid4())))
        
        st.rerun()
