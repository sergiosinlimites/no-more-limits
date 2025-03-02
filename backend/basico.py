import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

# 🛠️ Cargar modelo optimizado
print("Cargando modelo...")
model = WhisperModel("tiny", device="cpu", compute_type="int8", cpu_threads=4)
print("Modelo cargado correctamente")

# 📝 Variable global para almacenar el historial de contexto (máximo 50 palabras)
previous_text = []

# 🎙️ Función callback para capturar audio y transcribirlo en tiempo real
def callback(indata, frames, time, status):
    global previous_text
    if status:
        print("Error de audio:", status)
    
    print("Recibiendo audio...")

    # Convertir los datos de audio a un formato legible
    audio_data = np.frombuffer(indata, dtype=np.float32)

    # Generar el contexto limitado de las últimas 50 palabras
    initial_prompt = " ".join(previous_text[-50:])  # 👈 Mantiene contexto sin crecer indefinidamente

    print("Audio", audio_data)
    print("Shape", audio_data.shape)

    # 🚀 Transcripción con contexto dinámico
    segments, _ = model.transcribe(
        audio_data, 
        beam_size=10,  
        vad_filter=True,  
        language="es",  
        condition_on_previous_text=True,
        temperature=0,
        initial_prompt=initial_prompt  # 👈 Usa solo las últimas 50 palabras como referencia
    )

    # 📝 Construir transcripción uniendo fragmentos sin cortar palabras
    for segment in segments:
        text = segment.text

        # Evitar que se repitan palabras al unir segmentos
        if previous_text and text.startswith(previous_text[-1]):
            text = text[len(previous_text[-1]):]

        # Agregar nuevas palabras al historial y limitar a 50 palabras
        previous_text.extend(text.split())
        previous_text = previous_text[-50:]  # 👈 Mantiene solo las últimas 50 palabras

        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, " ".join(previous_text)))

# 🎤 Iniciar la grabación de audio con un tamaño de bloque optimizado
with sd.InputStream(callback=callback, samplerate=16000, channels=1, dtype='float32', blocksize=4096*32):
    print("Grabando... Presiona ENTER para detener.")
    input()  # Mantiene el programa en ejecución hasta que el usuario presione ENTER

print("Grabación detenida.")