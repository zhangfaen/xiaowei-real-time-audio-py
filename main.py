import asyncio
import numpy as np
import sounddevice as sd
from google import genai

client = genai.Client()

# --- sounddevice config ---
FORMAT = "int16"
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

# --- Live API config ---
MODEL = "gemini-2.5-flash-native-audio-preview-12-2025"

# 可选语音列表（具体支持哪些请查阅官方文档）:
# Kore - 男声
# Aoede - 女声
# Fenrir - 男声
# Puck - 中性
VOICE_NAME = "Aoede"  # 修改这里选择你喜欢的音色

CONFIG = {
    "response_modalities": ["AUDIO"],
    "speech_config": {
        "voiceConfig": {
            "prebuiltVoiceConfig": {
                "voiceName": VOICE_NAME,
            }
        }
    },
    "system_instruction": """
你是小薇，一位温柔可爱的女性AI助手。
你的名字叫小薇，说话简洁、有耐心，总是面带微笑。
你是一位热情、友好的助手，总是尽力帮助用户。
请保持对话自然、亲切。
""",
}

audio_queue_output = asyncio.Queue()
audio_queue_mic = asyncio.Queue(maxsize=5)
audio_stream = None

async def listen_audio():
    """Listens for audio and puts it into the mic audio queue."""
    global audio_stream
    audio_stream = sd.InputStream(
        samplerate=SEND_SAMPLE_RATE,
        channels=CHANNELS,
        dtype=FORMAT,
        blocksize=CHUNK_SIZE,
    )
    audio_stream.start()
    while True:
        data, _ = await asyncio.to_thread(audio_stream.read, CHUNK_SIZE)
        await audio_queue_mic.put({"data": data.tobytes(), "mime_type": "audio/pcm"})

async def send_realtime(session):
    """Sends audio from the mic audio queue to the GenAI session."""
    while True:
        msg = await audio_queue_mic.get()
        await session.send_realtime_input(audio=msg)

async def receive_audio(session):
    """Receives responses from GenAI and puts audio data into the speaker audio queue."""
    while True:
        turn = session.receive()
        async for response in turn:
            if (response.server_content and response.server_content.model_turn):
                for part in response.server_content.model_turn.parts:
                    if part.inline_data and isinstance(part.inline_data.data, bytes):
                        audio_queue_output.put_nowait(part.inline_data.data)

        # Empty the queue on interruption to stop playback
        while not audio_queue_output.empty():
            audio_queue_output.get_nowait()

async def play_audio():
    """Plays audio from the speaker audio queue."""
    stream = sd.OutputStream(
        samplerate=RECEIVE_SAMPLE_RATE,
        channels=CHANNELS,
        dtype=FORMAT,
        blocksize=CHUNK_SIZE,
    )
    stream.start()
    while True:
        bytestream = await audio_queue_output.get()
        audio_data = np.frombuffer(bytestream, dtype=FORMAT)
        await asyncio.to_thread(stream.write, audio_data)

async def run():
    """Main function to run the audio loop."""
    try:
        async with client.aio.live.connect(
            model=MODEL, config=CONFIG
        ) as live_session:
            print("Connected to Gemini. Start speaking!")
            tasks = [
                asyncio.create_task(send_realtime(live_session)),
                asyncio.create_task(listen_audio()),
                asyncio.create_task(receive_audio(live_session)),
                asyncio.create_task(play_audio()),
            ]
            await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        pass
    finally:
        if audio_stream:
            audio_stream.stop()
            audio_stream.close()
        print("\nConnection closed.")

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("Interrupted by user.")