let socket;
let audioContext;
let source;
let processor;
let fromSampleRate;
const toSampleRate = 16000;
let transcriptionText = "";

document.getElementById("startButton").addEventListener("click", async () => {
    socket = new WebSocket("ws://localhost:8765");
    socket.onopen = () => console.log("Conectado al servidor WebSocket.");
    socket.onmessage = (event) => {
        transcriptionText += " " + event.data;
        document.getElementById("transcription").innerText = transcriptionText.trim();
    };
    socket.onerror = (error) => console.error("WebSocket Error:", error);
    socket.onclose = () => console.log("Conexión cerrada.");

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioContext = new AudioContext();
    fromSampleRate = audioContext.sampleRate;
    source = audioContext.createMediaStreamSource(stream);
    processor = audioContext.createScriptProcessor(4096, 1, 1);
    source.connect(processor);
    processor.connect(audioContext.destination);

    processor.onaudioprocess = (event) => {
        let input = event.inputBuffer.getChannelData(0);
        let downsampled = downsample(input, fromSampleRate, toSampleRate);
        if (socket.readyState === WebSocket.OPEN) {
            socket.send(downsampled.buffer);
        }
    };

    document.getElementById("startButton").disabled = true;
    document.getElementById("stopButton").disabled = false;
});

document.getElementById("stopButton").addEventListener("click", () => {
    if (processor) processor.disconnect();
    if (source) source.disconnect();
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close();
    }

    transcriptionText = "";
    document.getElementById("transcription").innerText = "";
    document.getElementById("startButton").disabled = false;
    document.getElementById("stopButton").disabled = true;
});

function downsample(buffer, fromSampleRate, toSampleRate) {
    let sampleRateRatio = Math.round(fromSampleRate / toSampleRate);
    let newLength = Math.round(buffer.length / sampleRateRatio);
    let result = new Float32Array(newLength);
    let offsetResult = 0;
    let offsetBuffer = 0;
    while (offsetResult < result.length) {
        let nextOffsetBuffer = Math.round((offsetResult + 1) * sampleRateRatio);
        let accum = 0, count = 0;
        for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {
            accum += buffer[i];
            count++;
        }
        result[offsetResult] = accum / count;
        offsetResult++;
        offsetBuffer = nextOffsetBuffer;
    }
    return result;
}