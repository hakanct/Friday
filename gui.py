import customtkinter as ctk
import tkinter.messagebox as messagebox
import threading
import pystray
from PIL import Image, ImageDraw
from datetime import datetime
import time

from assistant import VoiceAssistant
from config import SHUTDOWN_COMMANDS

# CustomTkinter'ın görünüm modunu sistemden al
ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue") 

class JarvisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jarvis Asistan")
        self.root.geometry("600x650")
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window_on_close)
        self.root.resizable(False, False)

        # Nord Theme Renk Paleti (Hem Light hem Dark için adapte edilebilir)
        # Dark Mod için Nord Renkleri (Varsayılan olarak bu kullanılacak)
        self.dark_nord_bg_primary = "#2E3440"   # nord0 - Koyu Arkaplan
        self.dark_nord_bg_secondary = "#3B4252" # nord1 - Daha Açık Arkaplan (örn: frame, konsol)
        self.dark_nord_text_color = "#ECEFF4"   # nord6 - En açık gri / Yazı
        self.dark_nord_accent_color = "#5E81AC" # nord10 - Koyu Mavi (Butonlar)
        self.dark_nord_hover_color = "#81A1C1"  # nord9 - Açık Mavi (Buton Hover)
        self.dark_nord_red = "#BF616A"          # nord11 - Kırmızı (Çıkış Butonu)

        # Light Mod için Nord Renkleri (Sistem Light Moda geçtiğinde kullanılacak)
        self.light_nord_bg_primary = "#ECEFF4"  # nord6 - Açık Arkaplan
        self.light_nord_bg_secondary = "#E5E9F0" # nord5 - Daha Koyu Arkaplan (örn: frame, konsol)
        self.light_nord_text_color = "#2E3440"  # nord0 - Koyu Yazı
        self.light_nord_accent_color = "#5E81AC" # nord10 - Koyu Mavi (Butonlar, Light modda da aynı kalabilir)
        self.light_nord_hover_color = "#81A1C1" # nord9 - Açık Mavi (Buton Hover)
        self.light_nord_red = "#BF616A"         # nord11 - Kırmızı

        # İlk başlangıçta mevcut tema moduna göre renkleri belirle
        initial_mode = ctk.get_appearance_mode()
        if initial_mode == "Dark":
            self.current_bg_primary_color = self.dark_nord_bg_primary
            self.current_bg_secondary_color = self.dark_nord_bg_secondary
            self.current_text_color = self.dark_nord_text_color
            self.current_accent_color = self.dark_nord_accent_color
            self.current_hover_color = self.dark_nord_hover_color
            self.current_red_color = self.dark_nord_red
            self.current_console_bg_color = self.dark_nord_bg_secondary
        else: # Light Mode
            self.current_bg_primary_color = self.light_nord_bg_primary
            self.current_bg_secondary_color = self.light_nord_bg_secondary
            self.current_text_color = self.light_nord_text_color
            self.current_accent_color = self.light_nord_accent_color
            self.current_hover_color = self.light_nord_hover_color
            self.current_red_color = self.light_nord_red
            self.current_console_bg_color = self.light_nord_bg_secondary

        # CustomTkinter'ın kendi font sistemi
        try:
            self.main_font = ctk.CTkFont(family="JetBrains Mono", size=11)
            self.label_font = ctk.CTkFont(family="JetBrains Mono", size=16, weight="bold")
            self.console_font = ctk.CTkFont(family="JetBrains Mono", size=10)
        except:
            self.main_font = ctk.CTkFont(family="Consolas", size=11)
            self.label_font = ctk.CTkFont(family="Consolas", size=16, weight="bold")
            self.console_font = ctk.CTkFont(family="Consolas", size=10)
            print("Uyarı: JetBrains Mono fontu bulunamadı. Consolas (veya varsayılan monospace) kullanılıyor.")

        # Ana çerçeve
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=10, 
                                       fg_color=self.current_bg_secondary_color)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.status_var = ctk.StringVar(value="Başlatılmamış")
        self.hotword_active = False

        # Durum Label
        self.status_label = ctk.CTkLabel(self.main_frame, textvariable=self.status_var, 
                                        font=self.label_font, text_color=self.current_text_color)
        self.status_label.pack(pady=15)

        # Buton çerçevesi
        self.btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        # Hotword toggle butonu
        self.hotword_btn = ctk.CTkButton(self.btn_frame, text="Hotword Dinlemeyi Başlat", command=self.toggle_hotword,
                                        font=self.main_font, corner_radius=8, 
                                        fg_color=self.current_accent_color,
                                        hover_color=self.current_hover_color,
                                        text_color=self.current_text_color)
        self.hotword_btn.grid(row=0, column=0, padx=10, pady=5)

        # Manuel sesli komut butonu
        self.listen_btn = ctk.CTkButton(self.btn_frame, text="Sesli Komut Dinle", command=self.manual_listen,
                                       font=self.main_font, corner_radius=8, 
                                       fg_color=self.current_accent_color,
                                       hover_color=self.current_hover_color,
                                       text_color=self.current_text_color)
        self.listen_btn.grid(row=0, column=1, padx=10, pady=5)

        # Komut textbox ve gönderme
        self.cmd_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.cmd_frame.pack(pady=15)

        # cmd_entry için border_width 2 yapıldı
        self.cmd_entry = ctk.CTkEntry(self.cmd_frame, width=250, font=self.main_font, corner_radius=8,
                                     fg_color=self.current_bg_secondary_color,
                                     text_color=self.current_text_color,
                                     border_color=self.current_accent_color,
                                     border_width=2) # Border genişliği 2 yapıldı
        self.cmd_entry.grid(row=0, column=0, padx=5, pady=5)
        self.send_cmd_btn = ctk.CTkButton(self.cmd_frame, text="Gönder", command=self.send_command,
                                         font=self.main_font, corner_radius=8, 
                                         fg_color=self.current_accent_color,
                                         hover_color=self.current_hover_color,
                                         text_color=self.current_text_color)
        self.send_cmd_btn.grid(row=0, column=1, padx=5, pady=5)

        # Konsol alanı (ctk.CTkTextbox kullanıldı)
        # width 450, height 120 yapıldı (küçültüldü)
        self.console_output = ctk.CTkTextbox(self.main_frame, width=450, height=60, font=self.console_font,
                                            corner_radius=8, state="disabled", wrap="word",
                                            fg_color=self.current_console_bg_color,
                                            text_color=self.current_text_color,
                                            border_color=self.current_accent_color, # Konsolun da kenarlığı olsun
                                            border_width=2) # Konsol kenarlık genişliği
        self.console_output.pack(pady=10, padx=10, fill="both", expand=True)

        # Çıkış butonu
        self.exit_btn = ctk.CTkButton(self.main_frame, text="Uygulamayı Kapat", command=self.exit_app,
                                     font=self.main_font, corner_radius=8, 
                                     fg_color=self.current_red_color,
                                     hover_color="#CC0000",
                                     text_color=self.current_text_color)
        self.exit_btn.pack(pady=15)

        self.assistant = VoiceAssistant(self.update_status)

        self.hotword_thread = None

        self.tray_icon = None
        self.create_tray_icon()
        self.update_status("Beklemede")

        self.last_checked_theme = ctk.get_appearance_mode()
        
        # Tema değişimini 10 dakikada bir kontrol etmeye başla
        self.start_theme_monitor()

    def set_current_theme_colors(self):
        """Mevcut sisteme göre Nord renklerini ayarlar ve widget'ları günceller."""
        current_mode = ctk.get_appearance_mode() # "Dark" veya "Light"

        if current_mode == "Dark":
            self.current_bg_primary_color = self.dark_nord_bg_primary
            self.current_bg_secondary_color = self.dark_nord_bg_secondary
            self.current_text_color = self.dark_nord_text_color
            self.current_accent_color = self.dark_nord_accent_color
            self.current_hover_color = self.dark_nord_hover_color
            self.current_red_color = self.dark_nord_red
            self.current_console_bg_color = self.dark_nord_bg_secondary

        else: # Light Mode
            self.current_bg_primary_color = self.light_nord_bg_primary
            self.current_bg_secondary_color = self.light_nord_bg_secondary
            self.current_text_color = self.light_nord_text_color
            self.current_accent_color = self.light_nord_accent_color
            self.current_hover_color = self.light_nord_hover_color
            self.current_red_color = self.light_nord_red
            self.current_console_bg_color = self.light_nord_bg_secondary

        # Widget renklerini güncelle
        self.main_frame.configure(fg_color=self.current_bg_secondary_color)
        self.status_label.configure(text_color=self.current_text_color)
        
        self.hotword_btn.configure(fg_color=self.current_accent_color, hover_color=self.current_hover_color, text_color=self.current_text_color)
        self.listen_btn.configure(fg_color=self.current_accent_color, hover_color=self.current_hover_color, text_color=self.current_text_color)
        self.send_cmd_btn.configure(fg_color=self.current_accent_color, hover_color=self.current_hover_color, text_color=self.current_text_color)
        self.exit_btn.configure(fg_color=self.current_red_color, text_color=self.current_text_color)

        # Border genişliğini ve rengini güncelle
        self.cmd_entry.configure(fg_color=self.current_bg_secondary_color, text_color=self.current_text_color, border_color=self.current_accent_color, border_width=2)
        self.console_output.configure(fg_color=self.current_console_bg_color, text_color=self.current_text_color, border_color=self.current_accent_color, border_width=2)
            
    def check_theme_periodically(self):
        """Temayı periyodik olarak kontrol eder ve gerekirse günceller."""
        current_mode = ctk.get_appearance_mode()
        if current_mode != self.last_checked_theme:
            print(f"Tema değişti: {current_mode}") # Tema değiştiğinde terminale yazsın
            self.set_current_theme_colors()
            self.last_checked_theme = current_mode
        
        # 10 dakika (600000 milisaniye) sonra tekrar çağır
        self.root.after(600000, self.check_theme_periodically)

    def start_theme_monitor(self):
        """Tema kontrol döngüsünü başlatır."""
        # İlk kontrolü hemen yap ki UI başlangıçta doğru temada olsun
        self.set_current_theme_colors() 
        # Sonra 10 dakikada bir kontrolü başlat
        self.root.after(600000, self.check_theme_periodically)

    def update_status(self, status_text):
        self.root.after(0, self._update_status_gui, status_text)

    def _update_status_gui(self, status_text):
        self.status_var.set(status_text)
        
        self.console_output.configure(state="normal")
        current_time = datetime.now().strftime("%H:%M:%S")
        self.console_output.insert("end", f"[{current_time}] {status_text}\n")
        self.console_output.see("end")
        self.console_output.configure(state="disabled")
        print(f"GUI Durumu: {status_text}")

    def toggle_hotword(self):
        if not self.hotword_active:
            self.assistant.start_hotword_listening()
            self.hotword_active = True
            self.hotword_btn.configure(text="Hotword Dinlemeyi Durdur")
            if self.tray_icon:
                self.tray_icon.menu = self.create_tray_menu()
        else:
            self.assistant.stop_hotword_listening()
            self.hotword_active = False
            self.hotword_btn.configure(text="Hotword Dinlemeyi Başlat")
            if self.tray_icon:
                self.tray_icon.menu = self.create_tray_menu()

    def manual_listen(self):
        def listen_and_process():
            command = self.assistant.listen_command()
            self.assistant.process_command(command)
            if self.hotword_active:
                self.update_status("Hotword Dinleniyor...")
            else:
                self.update_status("Beklemede")

        threading.Thread(target=listen_and_process, daemon=True).start()

    def send_command(self):
        command = self.cmd_entry.get().strip().lower()
        if not command:
            messagebox.showwarning("Uyarı", "Lütfen bir komut girin.", parent=self.root)
            return
        
        self.cmd_entry.delete(0, ctk.END)

        def process_text_cmd():
            if any(phrase in command for phrase in SHUTDOWN_COMMANDS):
                self.assistant.speak("Hoşça kalın.")
                time.sleep(1)
                self.root.after(100, self.exit_app)
                return
            
            self.assistant.process_command(command)
            if self.hotword_active:
                self.update_status("Hotword Dinleniyor...")
            else:
                self.update_status("Beklemede")

        threading.Thread(target=process_text_cmd, daemon=True).start()

    def exit_app(self):
        self.assistant.stop_assistant()
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
        self.root.destroy()
        import os
        os._exit(0)

    def hide_window_on_close(self):
        self.root.withdraw()
        self.update_status("Arka Planda Çalışıyor")

    def create_image(self):
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), "black")
        dc = ImageDraw.Draw(image)
        dc.rectangle((16, 16, 48, 48), fill="white")
        return image

    def on_tray_quit(self, icon, item):
        self.root.after(0, self.exit_app)

    def on_tray_toggle_hotword(self, icon, item):
        self.root.after(0, self.toggle_hotword)

    def show_window(self, icon, item):
        self.root.after(0, self.root.deiconify)

    def create_tray_menu(self):
        hotword_menu_text = "Hotword Dinlemeyi Durdur" if self.hotword_active else "Hotword Dinlemeyi Başlat"
        
        menu = (
            pystray.MenuItem(hotword_menu_text, self.on_tray_toggle_hotword),
            pystray.MenuItem("Pencereyi Göster", self.show_window),
            pystray.MenuItem("Çıkış", self.on_tray_quit)
        )
        return menu

    def create_tray_icon(self):
        self.tray_icon = pystray.Icon("jarvis_asistan", self.create_image(), "Jarvis Asistan", self.create_tray_menu())
        threading.Thread(target=self.tray_icon.run, daemon=True).start()