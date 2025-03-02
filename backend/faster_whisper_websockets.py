from faster_whisper import WhisperModel
import numpy as np
import sys
import asyncio
import websockets

# 📝 Variable para almacenar el historial de contexto (máximo 50 palabras)
previous_text = []
MAX_HISTORY_WORDS = 50  # 🔹 Evita que el historial crezca demasiado

# 🛠️ Cargar modelo optimizado
print("Cargando modelo...")
model_size = "tiny"
model = WhisperModel(model_size, device="cpu", compute_type="float32", cpu_threads=4)
print("Modelo cargado correctamente")

async def process_audio(websocket):
    global previous_text

    count = 0
    frames = []

    print("Servidor WebSocket iniciado en ws://localhost:8765")

    async for data in websocket:
        frames.append(data)
        count += 1

        # Cuando se acumulan 20 fragmentos, transcribir
        if count > 20:
            chunk_frames = np.frombuffer(b"".join(frames), dtype=np.float32)

            # 🔹 Generar el contexto limitado de las últimas 50 palabras
            initial_prompt = " ".join(previous_text[-MAX_HISTORY_WORDS:]) if previous_text else ""

            # 🚀 Transcripción con contexto dinámico
            segments, _ = model.transcribe(
                chunk_frames,
                beam_size=10,
                vad_filter=True,
                language="es",
                condition_on_previous_text=True,
                temperature=0,
                initial_prompt=initial_prompt  # 🔹 Usa solo las últimas 50 palabras como referencia
            )

            results = ""
            for segment in segments:
                text = segment.text

                # Evitar repeticiones innecesarias
                if previous_text and text.startswith(previous_text[-1]):
                    text = text[len(previous_text[-1]):]

                previous_text.extend(text.split())
                previous_text = previous_text[-MAX_HISTORY_WORDS:]  # 🔹 Mantiene solo las últimas 50 palabras

                results += " " + text

            # 🔹 Enviar la transcripción al cliente
            await websocket.send(results.strip())

            # 🔹 Reiniciar el buffer de audio
            count = 0
            frames = []

async def start_server():
    async with websockets.serve(process_audio, "localhost", 8765):
        await asyncio.Future()  # Mantiene el servidor corriendo

# 🔹 Mantener la estructura original sin asyncio.run()
print("Iniciando servidor WebSocket en ws://localhost:8765")
asyncio.get_event_loop().run_until_complete(start_server())
asyncio.get_event_loop().run_forever()
