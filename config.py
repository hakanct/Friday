import os
from dotenv import load_dotenv

load_dotenv(".env")

# API Anahtarları
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
WEATHERAPI_API_KEY = os.getenv("WEATHERAPI_API_KEY") # weatherapi.com için yeni anahtar

# ElevenLabs Ses ID'leri ve Modelleri
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID_WOMAN")
ELEVENLABS_TTS_MODEL_ID = "eleven_turbo_v2_5" # Eleven Labs'in en hızlı modellerinden biri

# Vosk Modeli
VOSK_MODEL_PATH = "models/"+os.getenv("VOSK_MODEL_NAME", "vosk-model-small-en-us-0.15")

# Ses Tanıma Ayarları (SpeechRecognition)
LOCALE = os.getenv("LOCALE", "en_US") # Varsayılan olarak İngilizce
SPEECH_RECOGNITION_LANGUAGE = os.getenv("SPEECH_RECOGNITION_LANGUAGE", "en") # Türkçe varsayılan
SPEECH_RECOGNITION_TIMEOUT = 8
SPEECH_RECOGNITION_PHRASE_TIME_LIMIT = 10
SPEECH_RECOGNITION_ADJUST_NOISE_DURATION = 1.0
SPEECH_RECOGNITION_PAUSE_THRESHOLD = 2.0

# Hotword Ayarları
HOTWORDS = [
    "hey friday", "hey asistan", "hey bilgisayar",
    "friday komut ver", "komut ver", "dinle friday",
    "friday dinle", "friday", "asistan", "bilgisayar",
    "hey asistanım", "asistanım", "bilgisayarım", 
    "bilgisayarım dinle", "asistanım dinle",
    "asistan dinle"
]
CONFIRMATION_PHRASES = [
    "evet?", "buyrun", "dinliyorum", "ne yapabilirim?",
    "nasıl yardımcı olabilirim?", "emrinize amadeyim",
    "evet lordum?", "emredin", "ne var ne yok?",
    "sizi dinliyorum", "söyleyin efendim", "buyrun efendim",
    "my captain my captain", "emredersiniz",
]

# Uygulama Blacklist
APP_BLACKLIST = [
    "cmd", "powershell", "regedit", "taskmgr", "services", "msconfig"
]

# Uygulama Yolları (Kullanıcıya özel olanlar)
APP_PATHS = {
    "zen browser": r"C:\Program Files\Zen Browser\zen.exe",
    "youtube music": r"C:\Users\tonog\AppData\Local\Programs\youtube-music\YouTube Music.exe",
    "github desktop": r"C:\Users\tonog\AppData\Local\GitHubDesktop\GitHubDesktop.exe",
    "notion": r"C:\Users\tonog\AppData\Local\Programs\Notion\Notion.exe",
    "obsidian": r"C:\Users\tonog\AppData\Local\Programs\Obsidian\Obsidian.exe",
    "nora": r"C:\Users\tonog\AppData\Local\Programs\Nora\Nora.exe",
    "thunderbird": r"C:\Program Files\Mozilla Thunderbird\thunderbird.exe",
}

# Kapatma Komutları
SHUTDOWN_COMMANDS = [
    "programı durdur", "programı kapat", "programı sonlandır", 
    "kapat friday", "güle güle", "friday dinleme modundan çık",
    "friday dinleme modunu kapat", "friday dinleme modunu durdur",
    "friday kapan", "friday kapat", "friday sessiz ol",
    "friday artık dinleme", "friday artık konuşma",
    "friday kapatabilirsin", "yardımıma ihtiyacım kalmadı",
    "tamam kapat", "artık dinleme", "bitti",
    "kapatabilirsin"
]

# Uygulama Kısaltmaları (çalıştır komutu için)
APP_ALIASES = {
    "chrome": "google chrome",
    "excel": "microsoft excel",
    "word": "microsoft excel", # Word yerine Excel hatası düzeltildi
    "powerpoint": "microsoft powerpoint",
    "edge": "microsoft edge",
    "vscode": "code",
    "vs code": "code",
}

# Hava Durumu Ayarları (weatherapi.com için)
WEATHERAPI_BASE_URL = "http://api.weatherapi.com/v1/current.json" # WeatherAPI güncel hava durumu URL'si

TRANSFORMER_MODEL_NAME = "facebook/bart-large-mnli"
# TRANSFORMER_MODEL_NAME = "savasy/bert-base-turkish-sentiment-cased"
# TRANSFORMER_MODEL_NAME = "savasy/bert-turkish-uncased-qnli"
COMMAND_INTENTS = [
    "saati ve zamanı öğrenmek",
    "günü ve tarihi öğrenmek",
    "bir programı veya uygulamayı başlatmak veya açmak",
    "bilgisayarı yeniden başlatmak",
    "bilgisayarı kapatmak",
    "bilgisayarı uyku moduna almak",
    "medyayı duraklatmak veya oynatmak",
    "sonraki şarkıya veya medyaya geçmek",
    "önceki şarkıya veya medyaya dönmek",
    "bilgisayarın sesini ayarlamak",
    "yeni bir not almak veya kaydetmek",
    "hava durumu bilgisi sorgulamak",
    "asistanı veya programı kapatmak"
]
INTENT_CONFIDENCE_THRESHOLD = 0.60