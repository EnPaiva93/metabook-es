from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from pydantic import BaseModel, ConfigDict, Field

class TTS(BaseModel):
  client: gTTS = Field(default=gTTS)

  class Config:
        arbitrary_types_allowed = True

  def generar_audio_text(self, text):
        """
        Reads text
        """
        tts = self.client(text, lang='es', tld='es')

        fp = io.BytesIO()
        tts.write_to_fp(fp)
        # fp.seek(0)

        return Audio(audio_bytes=fp, input_format="mp3")

  def generar_audio(self, texto, tld='com.mx', velocidad=1.0):

        """Genera un fragmento de audio a partir de texto."""
        tts = gTTS(text=texto, lang="es", tld=tld, slow=False)
        tts_file = "temp.mp3"
        tts.save(tts_file)
        audio = AudioSegment.from_file(tts_file)
        # Ajustar velocidad del audio
        return audio.speedup(playback_speed=velocidad)

  def generar_conversacion(self, id="x01", orador1_dialogos=[], orador2_dialogos=[], velocidad=1.0, pausa_ms=500, idioma='es'):
    """
    Genera un audio combinado de una conversación entre dos oradores.

    Args:
        orador1_dialogos (list): Lista de diálogos de Orador 1.
        orador2_dialogos (list): Lista de diálogos de Orador 2.
        velocidad (float): Velocidad del habla (1.0 es la velocidad normal, >1.0 más rápido, <1.0 más lento).
        pausa_ms (int): Tiempo de pausa entre los diálogos en milisegundos.
        idioma (str): Idioma para gTTS (por defecto 'es' para español).

    Returns:
        None: Genera un archivo de audio llamado 'conversacion_completa.mp3'.
    """

    path = "./audios/"+id+".mp3"

    if len(orador1_dialogos)>1 and len(orador2_dialogos)>1:

      # Crear audio final fusionado
      audio_final = AudioSegment.silent(duration=0)  # Inicializar audio vacío

      # Alternar entre los diálogos de ambos oradores
      for o1, o2 in zip(orador1_dialogos, orador2_dialogos):
          audio_final += self.generar_audio(o1, 'us', velocidad)
          audio_final += AudioSegment.silent(duration=pausa_ms)  # Pausa entre oradores
          audio_final += self.generar_audio(o2, 'es', velocidad)
          audio_final += AudioSegment.silent(duration=pausa_ms)  # Pausa entre oradores

      # Si Orador 1 tiene más diálogos, añadir los restantes
      for i in range(len(orador2_dialogos), len(orador1_dialogos)):
          audio_final += self.generar_audio(orador1_dialogos[i])
          audio_final += AudioSegment.silent(duration=pausa_ms)  # Pausa entre oradores

      # Guardar el audio combinado
      audio_final.export(path, format="mp3")

      return path
