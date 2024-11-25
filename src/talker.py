import re, os
from pydantic import BaseModel, ConfigDict, Field
from . import utils
from openai import OpenAI

class Talker:
    
    def __init__(self, prompt: str = None, model: str = "Meta-Llama-3.1-70B-Instruct", api_key: str = None):
        """
        Inicializa la instancia del Talker.
        
        Args:
            prompt (str): El texto inicial o prompt para la generación.
            model (str): El modelo que se usará para generar respuestas.
            api_key (str): La clave API para autenticar con el cliente.
        """
        # Inicializar los atributos
        self.prompt = prompt
        self.model = model
        self.api_key = os.environ['SAMBANOVA_API_KEY']
        
        if not self.api_key:
            raise ValueError("API key no proporcionada y no encontrada en el entorno.")
        
        # Inicializar el cliente OpenAI
        self.client = OpenAI(
            base_url="https://api.sambanova.ai/v1/",
            api_key=self.api_key,
        )

    def response(self, query):
    
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user", 
                    "content": self.prompt.format(topic=query),
                }
            ],
            stream=False,
            temperature=0.5
        )
        
        response = completion.choices[0].message.content
        
        # Procesar el texto
        resultado = utils.extraer_contenido(response, "resultado")
        if resultado:
            resultado = resultado[0].strip()
            
        dialogo = utils.extraer_contenido(response, "dialogo")
        if dialogo:
            dialogo = dialogo[0].strip()        
        
        # Procesar diálogos
        if dialogo:
            
            orador1_dialogos, orador2_dialogos = utils.procesar_dialogos(dialogo)
        
            return resultado, orador1_dialogos, orador2_dialogos, response

        return None, None, None, None
