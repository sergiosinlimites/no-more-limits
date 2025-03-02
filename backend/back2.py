from faster_whisper import WhisperModel
import numpy as np
import sys
import asyncio
import websockets

# 📝 Variable para el historial de contexto
previous_text = []  # 🔹 Mantiene las últimas palabras transcritas para mejorar precisión
MAX_HISTORY_WORDS = 30  # 🔹 Evita que el historial crezca demasiado y genere repeticiones

# 🛠️ Cargar modelo optimizado
print("Cargando modelo...")
model_size = "tiny"
model = WhisperModel(model_size, device="cpu", compute_type="float32", cpu_threads=4)
print("Modelo cargado correctamente")

async def process_audio(websocket):
    global previous_text

    print("Cliente conectado al WebSocket.")

    async for data in websocket:
        try:
            # 🔹 Convertir el audio recibido a un formato legible
            audio_data = np.frombuffer(data, dtype=np.float32)

            # 🔹 Usar contexto solo si no hay repeticiones detectadas
            initial_prompt = " ".join(previous_text[-MAX_HISTORY_WORDS:]) if len(previous_text) > 5 else ""

            # 🚀 Transcripción en tiempo real
            segments, _ = model.transcribe(
                audio_data, 
                beam_size=10,  
                vad_filter=True,  
                language="es",  
                condition_on_previous_text=True,
                suppress_blank=True,  # 🔹 Evita silencios como predicciones
                temperature=0.2,  # 🔹 Reduce la creatividad del modelo para evitar repeticiones
                initial_prompt=initial_prompt
            )

            # 📝 Construir transcripción
            transcribed_text = ""
            for segment in segments:
                text = segment.text

                # ❌ Si el modelo empieza a repetir palabras, se reinicia el historial
                if len(previous_text) > 5 and text in " ".join(previous_text[-5:]):
                    print("⚠️ Se detectó repetición en la transcripción. Reseteando contexto.")
                    previous_text = []

                # Evitar que se repitan palabras al unir segmentos
                if previous_text and text.startswith(previous_text[-1]):
                    text = text[len(previous_text[-1]):]

                previous_text.extend(text.split())
                previous_text = previous_text[-MAX_HISTORY_WORDS:]  # 🔹 Mantiene solo las últimas 30 palabras

                transcribed_text += " " + text

            # 🔹 Enviar la transcripción al cliente
            await websocket.send(transcribed_text.strip())

        except Exception as e:
            print(f"❌ Error en transcripción: {e}")

    print("Cliente desconectado.")

async def start_server():
    async with websockets.serve(process_audio, "localhost", 8765):
        await asyncio.Future()  # Mantiene el servidor corriendo

# 🔹 Mantener la estructura original sin asyncio.run()
print("Iniciando servidor WebSocket en ws://localhost:8765")
asyncio.get_event_loop().run_until_complete(start_server())
asyncio.get_event_loop().run_forever()
