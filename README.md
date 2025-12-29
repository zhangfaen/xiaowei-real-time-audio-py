# XiaoWei Real-Time Audio

A real-time voice conversation application powered by Google's Gemini 2.5 Flash native audio API.

## Features

- **Real-time microphone input**: Captures audio from your microphone and sends it to Gemini
- **Real-time audio response**: Receives and plays back Gemini's audio responses
- **Full-duplex communication**: Simultaneous audio recording and playback

## Requirements

- Python 3.10+
- Google API Key (get one at https://aistudio.google.com/)
- Microphone and speakers

## Installation

```bash
# Install required packages
pip install sounddevice numpy google-genai 
pip install "httpx[socks]"
```

**Note**: If you use a SOCKS proxy, make sure `httpx[socks]` is installed.

## Configuration

Set your Google API key as an environment variable:

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

Or replace `main.py` line 6 with:

```python
client = genai.Client(api_key="your-api-key-here")
```

## Usage

```bash
python main.py
```

When you see `Connected to Gemini. Start speaking!`, start talking to Gemini. Press `Ctrl+C` to exit.

## Audio Configuration

You can modify the audio parameters in `main.py`:

```python
FORMAT = "int16"           # Audio format
CHANNELS = 1               # Mono audio
SEND_SAMPLE_RATE = 16000   # Microphone sample rate (Hz)
RECEIVE_SAMPLE_RATE = 24000 # Speaker sample rate (Hz)
CHUNK_SIZE = 1024          # Audio chunk size
```

## Architecture

- `listen_audio()`: Captures microphone input and queues it
- `send_realtime()`: Sends queued audio to Gemini
- `receive_audio()`: Receives Gemini's audio responses
- `play_audio()`: Plays received audio through speakers

## License

MIT
