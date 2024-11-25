import io, re
import uuid
import os, subprocess, ffmpeg

# Función para extraer contenido entre etiquetas específicas
def extraer_contenido(texto, etiqueta):
    """
    Extrae contenido encerrado dentro de etiquetas HTML/XML específicas en un texto.
    
    Args:
        texto (str): El texto fuente que contiene las etiquetas.
        etiqueta (str): La etiqueta de la que se quiere extraer el contenido.
        
    Returns:
        list: Lista con el contenido encontrado entre las etiquetas.
    """
    patron = fr"<{etiqueta}>(.*?)</{etiqueta}>"
    return re.findall(patron, texto, re.DOTALL)

# Función para procesar los diálogos de dos oradores
def procesar_dialogos(dialogo):
    """
    Procesa un bloque de texto para separar los diálogos de Orador 1 y Orador 2.
    
    Args:
        dialogo (str): Texto fuente que contiene los diálogos.
        
    Returns:
        tuple: Dos listas con los diálogos de Orador 1 y Orador 2, respectivamente.
    """
    # Patrones para extraer diálogos de Orador 1 y Orador 2
    orador1_patron = r"Orador 1: (.*?)(?=(Orador 2:|$))"
    orador2_patron = r"Orador 2: (.*?)(?=(Orador 1:|$))"

    # Encontrar diálogos y limpiar espacios
    orador1_dialogos = [d[0].strip() for d in re.findall(orador1_patron, dialogo, re.DOTALL)]
    orador2_dialogos = [d[0].strip() for d in re.findall(orador2_patron, dialogo, re.DOTALL)]

    return orador1_dialogos, orador2_dialogos
