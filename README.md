# No More Limits – Real-Time Speech-to-Text Transcription  

## 📌 Description  
**No More Limits** is a real-time speech-to-text transcription tool designed for **deaf and hard-of-hearing individuals**, built using **faster_whisper** and **WebSockets**. It enables fast and continuous voice-to-text conversion, facilitating communication between hearing and non-hearing individuals.  

The system consists of a **Python server** that processes audio and a **web client** that captures voice input and displays transcriptions in real time.  

## 🚀 Installation and Setup  

### 🔧 Requirements  
- **Server**: Python 3.9  
- **Client**: A web browser that supports WebSockets  

### 🔹 Server Setup  
1. **Create a Python virtual environment**  
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
venv\Scripts\activate  # On Windows
```

#### Install dependencies
```bash
pip install -r ./backend/requirements.txt
```

#### Run the server
```bash
py faster_whisper_websockets.py
```


### 🔹 Client Setup
Open ./frontend/index.html in a web browser.
Click the "Record" button and grant microphone permissions.
## 💡 Contributing
This project is open to contributions! If you would like to collaborate, feel free to submit a Pull Request (PR) with improvements, optimizations, or new features. Any help is appreciated!

## 📜 License
This project is open-source. You are free to use, modify, and contribute to it.