import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import time

from config_manager import ConfigManager
from ocr_engine import OCREngine
from clipboard_monitor import ClipboardMonitor

# Set default theme to System
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("500x350")
        self.config_manager = config_manager
        
        # Center the window
        self.center_window()
        self.lift()
        self.focus_force()
        self.grab_set()
        
        self.create_widgets()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        self.grid_columnconfigure(1, weight=1)
        
        pads = {'padx': 20, 'pady': (20, 5)}
        entry_width = 300

        # Title
        ctk.CTkLabel(self, text="API Configuration", font=("Roboto Medium", 20)).grid(row=0, column=0, columnspan=2, pady=20)

        # API URL
        ctk.CTkLabel(self, text="API URL:").grid(row=1, column=0, sticky="e", padx=20, pady=5)
        self.url_entry = ctk.CTkEntry(self, width=entry_width)
        self.url_entry.insert(0, self.config_manager.get("api_url", ""))
        self.url_entry.grid(row=1, column=1, sticky="w", padx=20, pady=5)
        
        # API Key
        ctk.CTkLabel(self, text="API Key:").grid(row=2, column=0, sticky="e", padx=20, pady=5)
        self.key_entry = ctk.CTkEntry(self, width=entry_width, show="*")
        self.key_entry.insert(0, self.config_manager.get("api_key", ""))
        self.key_entry.grid(row=2, column=1, sticky="w", padx=20, pady=5)

        
        # Model
        ctk.CTkLabel(self, text="Model:").grid(row=3, column=0, sticky="e", padx=20, pady=5)
        self.model_entry = ctk.CTkEntry(self, width=entry_width)
        self.model_entry.insert(0, self.config_manager.get("model", ""))
        self.model_entry.grid(row=3, column=1, sticky="w", padx=20, pady=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=30)
        
        ctk.CTkButton(btn_frame, text="Save", command=self.save, width=100).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy, width=100, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE")).pack(side="left", padx=10)

    def save(self):
        self.config_manager.set("api_url", self.url_entry.get().strip())
        self.config_manager.set("api_key", self.key_entry.get().strip())
        self.config_manager.set("model", self.model_entry.get().strip())
        self.destroy()

class ClipboardOCRApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("DeepSeek-OCR Clipboard")
        self.geometry("1100x700")
        
        # Standard System Title Bar (Requested by user)
        # self.overrideredirect(True) 
        
        self.current_image = None # Store for retry

        self.config_manager = ConfigManager()
        self.ocr_engine = OCREngine(self.config_manager)
        self.monitor = ClipboardMonitor()
        
        self.is_paused = False
        self.always_on_top = False
        
        self.setup_ui()
        
        # Thread checking loop
        self.after(1000, self.check_clipboard_loop)
        
        # Check API Key on startup
        self.after(500, self.check_api_key)

    def check_api_key(self):
        key = self.config_manager.get("api_key")
        if not key or key == "YOUR_API_KEY_HERE":
            response = messagebox.askyesno("配置缺失", "未检测到有效的 DeepSeek API Key。\n\n是否立即前往设置？\n(您也可以设置环境变量 DEEPSEEK_API_KEY)")
            if response:
                self.open_settings()
            else:
                 self.status_bar.configure(text="Warning: No API Key configured")

    def setup_ui(self):
        # Configure layout weights
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1) # 1/3 width
        self.grid_columnconfigure(1, weight=2) # 2/3 width

        # --- Top Toolbar ---
        # Height slightly reduced, removed some internal padding to reduce "white edge" feel if any
        toolbar = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color=("gray90", "gray10")) 
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        
        # Title in Toolbar - adjusted padding
        ctk.CTkLabel(toolbar, text="DeepSeek-OCR Clipboard", font=("Roboto Medium", 20)).pack(side="left", padx=20, pady=10)
        
        # Controls in Toolbar (Right side)
        self.btn_settings = ctk.CTkButton(toolbar, text="Settings", width=80, command=self.open_settings, fg_color="transparent", border_width=2, text_color=("gray10", "gray90"))
        self.btn_settings.pack(side="right", padx=10)
        
        self.btn_pause = ctk.CTkButton(toolbar, text="Pause", width=80, command=self.toggle_pause, fg_color="#E57373", hover_color="#EF5350")
        self.btn_pause.pack(side="right", padx=10)
        
        self.btn_top = ctk.CTkButton(toolbar, text="Pin", width=60, command=self.toggle_top, fg_color="transparent", border_width=2, text_color=("gray10", "gray90"))
        self.btn_top.pack(side="right", padx=10)

        # Auto Copy Switch
        self.auto_copy_var = ctk.IntVar(value=0)
        self.switch_auto_copy = ctk.CTkSwitch(toolbar, text="Auto Copy", variable=self.auto_copy_var, onvalue=1, offvalue=0)
        self.switch_auto_copy.pack(side="right", padx=15)

        # Mode Selection
        self.mode_var = ctk.StringVar(value="Pure Text")
        self.mode_menu = ctk.CTkOptionMenu(toolbar, values=["Pure Text", "Markdown", "Figure"], variable=self.mode_var, width=120)
        self.mode_menu.pack(side="right", padx=10)
        ctk.CTkLabel(toolbar, text="Mode:", text_color="gray").pack(side="right", padx=(15, 0))

        # Theme Toggle - Explicit colors for visibility in Light Mode
        self.btn_theme = ctk.CTkButton(toolbar, text="☀/☾", width=40, command=self.toggle_theme, fg_color="transparent", border_width=2, text_color=("gray10", "gray90"))
        self.btn_theme.pack(side="right", padx=10)

        # Drag bindings removed (using system title bar)

        # --- Content Area ---
        
        # Left Panel - Image
        left_panel = ctk.CTkFrame(self, corner_radius=15)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(15, 7), pady=15)
        
        ctk.CTkLabel(left_panel, text="Clipboard", font=("Roboto Medium", 14), text_color="gray").pack(pady=(10, 5))
        
        self.image_display = ctk.CTkLabel(left_panel, text="Waiting for image...", text_color="gray", corner_radius=10)
        self.image_display.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Right Panel - OCR Result
        right_panel = ctk.CTkFrame(self, corner_radius=15)
        right_panel.grid(row=1, column=1, sticky="nsew", padx=(7, 15), pady=15)
        
        # Header for Right Panel
        rp_header = ctk.CTkFrame(right_panel, fg_color="transparent", height=30)
        rp_header.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(rp_header, text="Result", font=("Roboto Medium", 14), text_color="gray").pack(side="left")
        
        self.btn_retry = ctk.CTkButton(rp_header, text="Retry", width=60, height=24, command=self.retry_ocr, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"))
        self.btn_retry.pack(side="right")
        
        self.text_area = ctk.CTkTextbox(right_panel, font=("Roboto", 14), corner_radius=10)
        self.text_area.pack(expand=True, fill="both", padx=10, pady=10)

        # Status Bar
        self.status_bar = ctk.CTkLabel(self, text="Ready", text_color="gray", anchor="w", font=("Roboto", 12))
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 5))

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.btn_pause.configure(text="Resume", fg_color="#66BB6A", hover_color="#43A047")
            self.status_bar.configure(text="Paused")
        else:
            self.btn_pause.configure(text="Pause", fg_color="#E57373", hover_color="#EF5350")
            self.status_bar.configure(text="Monitoring...")
        
    def toggle_top(self):
        self.always_on_top = not self.always_on_top
        self.attributes("-topmost", self.always_on_top)
        if self.always_on_top:
            self.btn_top.configure(fg_color=("#3B8ED0", "#1F6AA5"), text_color="white")
        else:
            self.btn_top.configure(fg_color="transparent", text_color=("gray10", "#DCE4EE")) # Fix Pin visibility too
    
        # Ensure pin button text color is visible in both modes
        self.btn_top.configure(text_color=("gray10", "#DCE4EE"))

    def open_settings(self):
        SettingsDialog(self, self.config_manager)

    def check_clipboard_loop(self):
        if not self.is_paused:
            image = self.monitor.check()
            if image:
                self.process_new_image(image)
        self.after(1000, self.check_clipboard_loop)

    def process_new_image(self, image):
        self.current_image = image
        self.status_bar.configure(text="Processing...")
        self.display_image(image)
        
        self.text_area.delete("1.0", "end")
        self.text_area.insert("end", "Running OCR...\n")
        
        threading.Thread(target=self.run_ocr, args=(image,), daemon=True).start()

    def display_image(self, image):
        # Resize logic
        self.update_idletasks() # Ensure sizes are current
        panel_w = self.image_display.winfo_width()
        panel_h = self.image_display.winfo_height()
        
        if panel_w < 100: panel_w = 400
        if panel_h < 100: panel_h = 400

        # Create copy and resize preserving aspect ratio
        img_copy = image.copy()
        
        # Calculate aspect ratio
        img_ratio = img_copy.width / img_copy.height
        panel_ratio = panel_w / panel_h

        if img_ratio > panel_ratio:
            # Width limiting
            new_w = panel_w
            new_h = int(new_w / img_ratio)
        else:
            # Height limiting
            new_h = panel_h
            new_w = int(new_h * img_ratio)
            
        img_copy = img_copy.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        ctk_image = ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=(new_w, new_h))
        self.image_display.configure(image=ctk_image, text="")
        self.image_display.image = ctk_image # Keep ref

    def start_move(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def do_move(self, event):
        deltax = event.x - self._drag_data["x"]
        deltay = event.y - self._drag_data["y"]
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def quit_app(self):
        self.destroy()

    def minimize_app(self):
        # Withdraw to tray (iconify)
        self.withdraw()
        # On Mac, withdraw often hides it completely. 'iconify' is safer.
        self.iconify()

    def maximize_app(self):
        self.is_maximized = not self.is_maximized
        # CTk doesn't support 'zoomed' state on Mac well in overriding mode.
        # We can simulate by setting geometry to screen size.
        if self.is_maximized:
            self._pre_max_geom = self.geometry()
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            self.geometry(f"{w}x{h}+0+0")
        else:
            if hasattr(self, '_pre_max_geom'):
                self.geometry(self._pre_max_geom)

    def retry_ocr(self):
        if self.current_image:
             self.status_bar.configure(text="Retrying...")
             self.text_area.delete("1.0", "end")
             self.text_area.insert("end", "Retrying OCR...\n")
             threading.Thread(target=self.run_ocr, args=(self.current_image,), daemon=True).start()
        else:
             messagebox.showinfo("Retry", "No image to retry.")

    def toggle_theme(self):
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")

    def run_ocr(self, image):
        mode = self.mode_var.get()
        result = self.ocr_engine.perform_ocr(image, mode=mode)
        
        # Update UI in main thread
        def update_text():
            self.text_area.delete("1.0", "end")
            self.text_area.insert("end", result)
            self.status_bar.configure(text="OCR Completed")
            
            # Auto Copy
            if self.auto_copy_var.get() == 1:
                self.clipboard_clear()
                self.clipboard_append(result)
                self.update() # Keep clipboard
                self.status_bar.configure(text="OCR Completed (Copied to Clipboard)")
        
        self.after(0, update_text)

if __name__ == "__main__":
    app = ClipboardOCRApp()
    app.mainloop()
