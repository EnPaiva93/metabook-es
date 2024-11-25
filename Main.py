import streamlit as st
import re, time
import subprocess

st.set_page_config(
    page_title="MetaBook",
    page_icon="+",
    layout="wide",
    initial_sidebar_state="collapsed"
)
            
st.markdown("<h1 style='text-align: center; color: white;'>MetaBook ( Página de Prueba )</h1>", unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center; color: white;'>Plataforms educativa de generación de conocimientos</h3>", unsafe_allow_html=True)

st.divider()

folder_path = "./audios"

# Use a shell command to remove all contents
try:
    subprocess.run(f"rm -rf {folder_path}/*", check=True, shell=True)
    print(f"All contents inside '{folder_path}' have been removed.")
except subprocess.CalledProcessError as e:
    print(f"Error while removing contents: {e}")

left_center, col1, col2 = st.columns([1,5,1]) 
with left_center:
    submit = st.button("Ingresar",use_container_width=True)
with col1:
    pass
with col2:
    pass

if submit:
    
    st.switch_page("pages/App.py")

st.divider()

st.write("")

advertencia = """
**Advertencia:** Debido a las limitaciones actuales de recursos, este chat puede experimentar intermitencias, tiempos de respuestas prolongados y posibles fallos en la disponibilidad del servicio. Agradecemos tu comprensión y paciencia mientras trabajamos para mejorar la experiencia.
"""

st.warning(advertencia, icon="⚠️")

st.write("")

# Texto en Markdown para el descargo de responsabilidad
descargo = """
Esta aplicación se proporciona con fines informativos/educativos.
"""

# Mostrar el descargo en la aplicación de Streamlit
with st.expander("Descargo de responsabilidad"):
    st.markdown(descargo, unsafe_allow_html=True)
