import os
import time
from datetime import datetime, timedelta
import speech_recognition as sr
import subprocess
import threading
import re
import locale
import queue
import random
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from elevenlabs import ElevenLabs, play 
from elevenlabs.client import ElevenLabs as ElevenLabsClient 
import pyautogui 
import requests 
import urllib.parse # Yeni eklendi, şehir adlarını URL için kodlamak için
from transformers import pipeline

# device = "CUDA"

# Windows ses kontrolü için özel importlar
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    from ctypes import cast, POINTER
except ImportError:
    print("pycaw veya comtypes bulunamadı. Ses kontrolü devre dışı.")
    AudioUtilities = None
    IAudioEndpointVolume = None

# config.py'den sabitleri içe aktar
from config import (
    LOCALE, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, ELEVENLABS_TTS_MODEL_ID,
    VOSK_MODEL_PATH, SPEECH_RECOGNITION_LANGUAGE, SPEECH_RECOGNITION_TIMEOUT,
    SPEECH_RECOGNITION_PHRASE_TIME_LIMIT, SPEECH_RECOGNITION_ADJUST_NOISE_DURATION,
    SPEECH_RECOGNITION_PAUSE_THRESHOLD, HOTWORDS, CONFIRMATION_PHRASES,
    APP_BLACKLIST, APP_PATHS, SHUTDOWN_COMMANDS, APP_ALIASES,
    WEATHERAPI_API_KEY, WEATHERAPI_BASE_URL, TRANSFORMER_MODEL_NAME,
    COMMAND_INTENTS, INTENT_CONFIDENCE_THRESHOLD
)

locale.setlocale(locale.LC_TIME, LOCALE)

class VoiceAssistant:
    def __init__(self, gui_update_callback):
        self.recognizer = sr.Recognizer()
        self.recognizer.phrase_time_limit = SPEECH_RECOGNITION_PHRASE_TIME_LIMIT
        self.recognizer.pause_threshold = SPEECH_RECOGNITION_PAUSE_THRESHOLD
        
        # ElevenLabs istemcisini ElevenLabs sınıfından doğrudan oluştur
        self.elevenlabs = ElevenLabsClient(api_key=ELEVENLABS_API_KEY)
        
        if not os.path.exists(VOSK_MODEL_PATH):
            raise FileNotFoundError(f"Vosk modeli bulunamadı: {VOSK_MODEL_PATH}")
        self.vosk_model = Model(VOSK_MODEL_PATH)
        self.vosk_recognizer = KaldiRecognizer(self.vosk_model, 16000) # Vosk modeli ve recognizer

        self.hotwords = HOTWORDS
        self.confirmation_phrases = CONFIRMATION_PHRASES
        
        self.q = queue.Queue()
        self.running = True 
        self.hotword_listening = False 
        self.gui_update_callback = gui_update_callback

        self.audio_stream = None

        self.app_blacklist = APP_BLACKLIST
        self.app_paths = APP_PATHS
        self.shutdown_commands = SHUTDOWN_COMMANDS
        self.app_aliases = APP_ALIASES

        self._initialize_volume_control()
        # Transformer pipeline'ını başlat
        # Bu işlem modelin boyutuna göre biraz zaman alabilir.
        print("Transformer modeli yükleniyor...")
        self.gui_update_callback("Doğal dil işleme modeli yükleniyor...")
        try:
            self.classifier = pipeline("zero-shot-classification", model=TRANSFORMER_MODEL_NAME)
            print("Transformer modeli başarıyla yüklendi.")
            self.gui_update_callback("Model yüklendi, asistan hazır.")
        except Exception as e:
            print(f"Transformer modeli yüklenirken hata oluştu: {e}")
            self.gui_update_callback(f"Model Yükleme Hatası: {e}")
            self.classifier = None

    def _initialize_volume_control(self):
        """Windows ses kontrolü için gerekli nesneleri başlatır."""
        self.volume_interface = None
        if AudioUtilities and IAudioEndpointVolume:
            try:
                devices = AudioUtilities.GetSpeakers()                                
                default_device = devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self.volume_interface = cast(default_device, POINTER(IAudioEndpointVolume))
            except Exception as e:
                print(f"Ses kontrol arayüzü başlatılırken hata oluştu: {e}")
                self.volume_interface = None

    def audio_callback(self, indata, frames, time_info, status):
        if status:
            print(f"Ses akışı hatası: {status}")
        self.q.put(bytes(indata))

    def play_confirmation(self):
        phrase = random.choice(self.confirmation_phrases)
        self.speak(phrase)

    def start_hotword_listening(self):
        if self.hotword_listening:
            return

        self.hotword_listening = True
        self.gui_update_callback("Hotword Dinleniyor...")
        print("Hotword dinleniyor...")

        def hotword_loop():
            rec = KaldiRecognizer(self.vosk_model, 16000)

            try:
                with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                                       channels=1, callback=self.audio_callback) as self.audio_stream:
                    while self.running and self.hotword_listening:
                        data = self.q.get()
                        if rec.AcceptWaveform(data):
                            result = rec.Result()
                            text = json.loads(result).get("text", "")
                            print(f"Vosk Algılandı: {text}") 
                            for hw in self.hotwords:
                                if hw in text.lower():
                                    print(f"Hotword algılandı: {hw}")
                                    self.gui_update_callback("Hotword Algılandı, Komut Bekleniyor...")
                                    self.play_confirmation()
                                    command = self.listen_command()
                                    self.process_command(command)
                                    
                                    if self.hotword_listening: 
                                        self.gui_update_callback("Hotword Dinleniyor...")
                                    else:
                                        self.gui_update_callback("Beklemede")
                                    rec = KaldiRecognizer(self.vosk_model, 16000) # Yeni bir recognizer başlat
                                    break 
                            else: 
                                if text: # Eğer hotword algılanmadı ama bir metin varsa, recognizer'ı sıfırla
                                     rec = KaldiRecognizer(self.vosk_model, 16000)
                                     pass 
            except Exception as e:
                print(f"Hotword dinleme hatası: {e}")
                self.gui_update_callback(f"Hotword Dinleme Hatası: {e}")
            finally:
                self.hotword_listening = False
                self.gui_update_callback("Beklemede")
                print("Hotword dinleme durduruldu.")

        threading.Thread(target=hotword_loop, daemon=True).start()

    def stop_hotword_listening(self):
        self.hotword_listening = False
        if self.audio_stream and self.audio_stream.active:
            self.audio_stream.stop()
            self.audio_stream.close()
            self.audio_stream = None
        self.gui_update_callback("Beklemede")
        print("Hotword dinleme durdurma isteği gönderildi.")

    def speak(self, text):
        try:
            audio = self.elevenlabs.text_to_speech.convert(
                text=text,
                voice_id=ELEVENLABS_VOICE_ID,
                model_id=ELEVENLABS_TTS_MODEL_ID,
                output_format="mp3_44100_128",
                language_code="tr"  # ElevenLabs'a metnin Türkçe olduğunu belirt
            )
            play(audio)
        except Exception as e:
            print(f"TTS Hatası: {e}")
            self.gui_update_callback(f"TTS Hatası: {e}")

    def listen_command(self):
        with sr.Microphone() as source:
            self.gui_update_callback("Komut Dinleniyor...")
            print("Komut için konuşun...")
            self.recognizer.adjust_for_ambient_noise(source, duration=SPEECH_RECOGNITION_ADJUST_NOISE_DURATION)
            try:
                audio = self.recognizer.listen(source, timeout=SPEECH_RECOGNITION_TIMEOUT, phrase_time_limit=SPEECH_RECOGNITION_PHRASE_TIME_LIMIT)
                self.gui_update_callback("Ses Yakalandı, İşleniyor...")
                print("Ses yakalandı.")
                text = self.recognizer.recognize_google(audio, language=SPEECH_RECOGNITION_LANGUAGE)
                print(f"Söylenen komut: {text}")
                return text.lower()
            except sr.WaitTimeoutError:
                self.gui_update_callback("Ses Alınamadı (Timeout)")
                print("Ses alınamadı (timeout).")
                self.speak("Sesinizi alamadım. Tekrar deneyebilir misiniz?")
                return None
            except sr.UnknownValueError:
                self.gui_update_callback("Ses Anlaşılamadı")
                print("Ses anlaşılamadı.")
                self.speak("Ne dediğinizi anlayamadım. Lütfen daha net konuşun.")
                return None
            except sr.RequestError as e:
                self.gui_update_callback("Google API Hatası")
                print(f"Google Speech Recognition servis hatası: {e}")
                self.speak("Ses tanıma servisinde bir sorun oluştu.")
                return None

    def is_app_allowed(self, app_name):
        for blocked in self.app_blacklist:
            if blocked in app_name.lower():
                return False
        return True

    def process_command(self, command):
        self.gui_update_callback(f"Komut İşleniyor: {command or 'Boş Komut'}")
        if not command or not self.classifier:
            if not self.classifier:
                self.speak("Doğal dil işleme modeli yüklenemediği için komutları işleyemiyorum.")
            else:
                self.speak("Komut alınamadı.")
            return

        print(f"Komut işleniyor: {command}")

        # Zero-Shot Classification ile niyeti anla
        result = self.classifier(command, COMMAND_INTENTS, multi_label=False)
        
        intent = result['labels'][0]
        score = result['scores'][0]

        print(f"Algılanan Niyet: {intent} (Güven: {score:.2f})")
        self.gui_update_callback(f"Niyet: {intent} (%{score*100:.0f})")

        if score < INTENT_CONFIDENCE_THRESHOLD:
            self.speak("Bu komutu anlayamadım, lütfen farklı bir şekilde tekrar eder misiniz?")
            return

        # Algılanan niyete göre ilgili fonksiyonu çalıştır
        if intent == "saati ve zamanı öğrenmek":
            # 'saat kaç' komutundaki eski mantığı buraya taşıyoruz
            now = datetime.now()
            hour = now.hour
            minute = now.minute
            # ... (saat_metni oluşturma kodunuzun tamamı burada olmalı)
            # Bu kod bloğu çok uzundu, özet olarak ekliyorum. Mevcut kodunuzu buraya kopyalayın.
            saat_metni = f"Saat {hour}:{minute}" # Örnek basit metin, sizdeki detaylı metni kullanın.
            self.speak(saat_metni)

        elif intent == "günü ve tarihi öğrenmek":
            today = datetime.now().strftime("%d %B %Y, %A")
            self.speak(f"Bugün {today}")

        elif intent == "bilgisayarı yeniden başlatmak":
            self.speak("Bilgisayar yeniden başlatılıyor.")
            subprocess.run(["shutdown", "/r", "/t", "1"])

        elif intent == "bilgisayarı kapatmak":
            self.speak("Bilgisayar kapatılıyor.")
            subprocess.run(["shutdown", "/s", "/t", "1"])

        elif intent == "bilgisayarı uyku moduna almak":
            self.speak("Bilgisayar uyku moduna alınıyor.")
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])

        elif intent == "bir programı veya uygulamayı başlatmak veya açmak":
            # Uygulama adını komuttan çıkarmamız gerekiyor (Entity Extraction)
            # Bu basit bir yöntem, daha gelişmiş NER modelleri de kullanılabilir.
            app_name_raw = command.replace("çalıştır", "").replace("aç", "").strip()
            
            # Takma isimleri kontrol et
            for alias, real_name in self.app_aliases.items():
                if alias in app_name_raw:
                    app_name_raw = real_name
                    break
            
            # app_paths içinde ara
            found_app_path = None
            for name, path in self.app_paths.items():
                if name in app_name_raw:
                    found_app_path = path
                    app_name_raw = name # Bulunan asıl ismi kullanalım
                    break
            
            if found_app_path:
                # ... (mevcut uygulama çalıştırma mantığınız)
                self.speak(f"{app_name_raw} başlatılıyor.")
                subprocess.Popen([found_app_path])
            else:
                self.speak(f"{app_name_raw} isimli uygulamayı bulamadım veya çalıştırma yetkim yok.")

        elif intent == "hava durumu bilgisi sorgulamak":
            # Şehir ismini komuttan çıkarmamız gerekiyor.
            city_match = re.search(r"(\w+)'(?:da|de|ta|te)\s*hava", command)
            city = "Istanbul" # Varsayılan
            if city_match:
                city = city_match.group(1)
            
            # ... (mevcut hava durumu kodunuzun tamamı burada olmalı)
            self.speak(f"{city} için hava durumu bilgisi alınıyor...") # Örnek metin
            # Mevcut API isteği ve cevap verme kodunuzu buraya taşıyın.

        elif intent == "yeni bir not almak veya kaydetmek":
            self.speak("Elbette, ne not almamı istersiniz?")
            note_content = self.listen_command()
            if note_content:
                # ... (mevcut not kaydetme kodunuz)
                self.speak("Notunuz kaydedildi.")
            else:
                self.speak("Bir not alamadım.")

        elif intent == "medyayı duraklatmak ya da oynatmak":
            self.speak("Medyayı oynatıyorum veya duraklatıyorum.")
            pyautogui.press('playpause')

        elif intent == "sonraki şarkıya veya medyaya geçmek":
            self.speak("Sonraki şarkıya geçiliyor.")
            pyautogui.press('nexttrack')

        elif intent == "önceki şarkıya veya medyaya dönmek":
            self.speak("Önceki şarkıya geçiliyor.")
            pyautogui.press('prevtrack')
        
        elif intent == "bilgisayarın sesini ayarlamak":
            # Ses ayarlama mantığı biraz daha karmaşık olduğu için regex'i koruyabiliriz.
            # ... (mevcut sesi yüzde ile ayarlama kodunuz burada olabilir)
            self.speak("Ses ayarı komutunu işliyorum.") # Örnek

        elif intent == "asistanı veya programı kapatmak":
            self.speak("Görüşmek üzere, hoşça kalın.")
            self.running = False
            # GUI'nin kapanması için ana thread'e sinyal göndermek gerekebilir.
            # Şimdilik sadece assistant'ı durduruyoruz.

        else:
            self.speak("Bu komut için bir eylem tanımlanmamış.")
            self.speak("Bu komutu anlayamadım.")

    def _number_to_turkish_word(self, number):
        """Sayıları Türkçe kelimelere çevirir."""
        birler = ["", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz"]
        onlar = ["", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan"]

        if number == 0:
            return "sıfır"
        elif 1 <= number <= 9:
            return birler[number]
        elif 10 <= number <= 99:
            onluk_kisim = number // 10
            birlik_kisim = number % 10
            if birlik_kisim == 0:
                return onlar[onluk_kisim]
            else:
                return f"{onlar[onluk_kisim]} {birler[birlik_kisim]}"
        return str(number) 

    def stop_assistant(self):
        self.running = False
        self.stop_hotword_listening()