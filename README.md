# Friday Voice Assistant

A Turkish voice assistant built with Python that uses speech recognition, text-to-speech, and natural language processing capabilities. The assistant features a modern GUI built with CustomTkinter and system tray integration.
You can config it for other languages.

## Features

- Voice command recognition with hotword detection ("Hey Jarvis" and other variants)
- Text-to-speech capabilities using ElevenLabs API
- Natural language understanding using transformer models
- Modern GUI with dark/light theme support
- System tray integration
- Weather information retrieval
- System controls (shutdown, restart, sleep)
- Application launching
- Media playback controls
- Volume control
- Note-taking functionality
- Time and date information

## Prerequisites

- Python 3.11 or higher
- Windows operating system (some features are Windows-specific)
- Internet connection for API services

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ttstest
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install customtkinter
pip install vosk
pip install elevenlabs
pip install transformers
pip install python-dotenv
pip install Pillow
pip install pycaw
pip install comtypes
pip install SpeechRecognition
```

4. Download the Vosk model:
- Create a `models` directory
- Download the Turkish model from https://alphacephei.com/vosk/models (vosk-model-small-tr-0.3)
- Extract it to `models/` folder as folder (root/models/vosk-model-small-tr-0.3)

5. Create a `.env` file in the root directory with your API keys:
- There is an example file in root directory.
```env
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID_WOMAN=your_voice_id
WEATHERAPI_API_KEY=your_weatherapi_key
```

## Usage

1. Start the application:
```bash
python main.py
```

2. The application will start and minimize to the system tray. You can:
   - Click the tray icon to show/hide the window
   - Use the tray menu to toggle hotword detection or quit

3. Voice Commands:
   - Activate the assistant by saying "Hey Jarvis" or other configured hotwords
   - Wait for the confirmation sound
   - Speak your command in Turkish

4. Available Commands:
   - Ask for time and date
   - Control system (shutdown, restart, sleep)
   - Launch applications
   - Check weather
   - Control media playback
   - Adjust system volume
   - Take notes

5. Manual Input:
   - Use the text input field to type commands
   - Click "Gönder" or press Enter to execute

## Configuration

You can customize various settings in `config.py`:
- API keys and endpoints
- Voice recognition settings
- Hotwords and confirmation phrases
- Application shortcuts
- Command intents and thresholds

## Project Structure

- `main.py`: Application entry point
- `gui.py`: GUI implementation using CustomTkinter
- `assistant.py`: Core voice assistant functionality
- `config.py`: Configuration settings

## Dependencies

- CustomTkinter: Modern GUI framework
- Vosk: Offline speech recognition
- ElevenLabs: Text-to-speech service
- Transformers: Natural language processing
- python-dotenv: Environment variable management
- pycaw: Windows audio control
- SpeechRecognition: Speech recognition framework

## Note

This project requires API keys from:
- ElevenLabs (for text-to-speech)
- WeatherAPI (for weather information)

Make sure to obtain these keys and add them to your `.env` file before running the application.
