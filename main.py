"""
İşçi TC Kimlik & Özel Kod / Barkod Oluşturma, Yazdırma ve Excel Entegrasyon Uygulaması
Ana Kullanıcı Arayüzü (GUI)
"""
import sys
import os
import json
import sqlite3
import ctypes
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

# Windows High-DPI Uyumluluğu (Yüksek çözünürlüklü ekranlarda net yazı/buton görünümü)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# Kendi modüllerimiz
import qr_generator
import printer_service


class QRCodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Barkod & QR Kod Studio | Excel & Baskı Entegrasyonu")
        self.root.geometry("1280x820")
        self.root.minsize(1080, 720)
        
        # Tema ve Stil Ayarları
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure_styles()
        
        # Veritabanı Kurulumu
        self.db_file = os.path.join(os.path.dirname(__file__), "workers.db")
        self.init_db()
        
        # Aktif Önizleme Görseli & Durumlar
        self.current_badge_image = None
        self.current_worker_data = None
        self.sort_column = "id"
        self.sort_reverse = True
        self._resize_timer = None
        
        # Değişkenler
        self.var_code_mode = tk.StringVar(value="barcode")        # "barcode", "qr", "both"
        self.var_barcode_type = tk.StringVar(value="Code 128 (Genel)") # "code128", "code39", "ean13", "ean8", "upca"
        self.var_show_barcode_text = tk.BooleanVar(value=True)    # Barkod altında kod yazısı
        self.var_strict_tckn = tk.BooleanVar(value=False)         # Sıkı 11 haneli TC kontrolü
        self.var_company_title = tk.StringVar(value="")           # Üst kurum/şirket başlığı
        
        # Ana Arayüz Bileşenleri
        self.build_ui()
        self.bind_shortcuts()
        self.refresh_worker_list()
        self.update_printer_list()

    def configure_styles(self):
        """Arayüz renk ve yazı tipi stillerini yapılandırır."""
        bg_dark = "#0F172A"       # Slate 900
        fg_white = "#F8FAFC"      # Slate 50
        accent_blue = "#2563EB"   # Blue 600
        accent_emerald = "#059669" # Emerald 600
        accent_green = "#107C41"   # Excel Green
        
        self.root.configure(bg="#F1F5F9")
        
        self.style.configure("TFrame", background="#F1F5F9")
        self.style.configure("Card.TFrame", background="#FFFFFF", relief="flat", borderwidth=1)
        self.style.configure("Header.TFrame", background=bg_dark)
        
        self.style.configure("Header.TLabel", background=bg_dark, foreground=fg_white, font=("Segoe UI", 15, "bold"))
        self.style.configure("SubHeader.TLabel", background=bg_dark, foreground="#94A3B8", font=("Segoe UI", 9))
        self.style.configure("Title.TLabel", background="#FFFFFF", foreground="#0F172A", font=("Segoe UI", 11, "bold"))
        self.style.configure("Normal.TLabel", background="#FFFFFF", foreground="#334155", font=("Segoe UI", 9))
        self.style.configure("Sub.TLabel", background="#FFFFFF", foreground="#64748B", font=("Segoe UI", 8))
        
        self.style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"), background=accent_blue, foreground="white", padding=(8, 4))
        self.style.map("Primary.TButton", background=[("active", "#1D4ED8"), ("pressed", "#1E40AF")])
        
        self.style.configure("Success.TButton", font=("Segoe UI", 9, "bold"), background=accent_emerald, foreground="white", padding=(8, 4))
        self.style.map("Success.TButton", background=[("active", "#047857"), ("pressed", "#065F46")])

        self.style.configure("Excel.TButton", font=("Segoe UI", 9, "bold"), background=accent_green, foreground="white", padding=(8, 4))
        self.style.map("Excel.TButton", background=[("active", "#0B5A2F"), ("pressed", "#064E26")])

        self.style.configure("Action.TButton", font=("Segoe UI", 9), background="#E2E8F0", foreground="#0F172A", padding=(8, 4))
        self.style.map("Action.TButton", background=[("active", "#CBD5E1"), ("pressed", "#94A3B8")])

        self.style.configure("Danger.TButton", font=("Segoe UI", 9), background="#FEE2E2", foreground="#991B1B", padding=(8, 4))
        self.style.map("Danger.TButton", background=[("active", "#FECACA"), ("pressed", "#FCA5A5")])

        self.style.configure("Card.TRadiobutton", background="#FFFFFF", font=("Segoe UI", 9))
        self.style.configure("Card.TCheckbutton", background="#FFFFFF", font=("Segoe UI", 9))
        self.style.configure("Card.TLabelframe", background="#FFFFFF")
        self.style.configure("Card.TLabelframe.Label", background="#FFFFFF", font=("Segoe UI", 9, "bold"), foreground="#1E293B")

        self.style.configure("Treeview", font=("Segoe UI", 9), rowheight=28)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#E2E8F0", foreground="#0F172A", relief="flat")
        self.style.map("Treeview", background=[("selected", "#3B82F6")], foreground=[("selected", "white")])

    def init_db(self):
        """Veritabanı tablosunu oluşturur."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    surname TEXT NOT NULL,
                    tckn TEXT UNIQUE NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def build_ui(self):
        """Tüm arayüz düzenini oluşturur."""
        # 1. Üst Header Bar
        header_frame = ttk.Frame(self.root, style="Header.TFrame", padding=(20, 12))
        header_frame.pack(fill="x", side="top")
        
        header_inner = ttk.Frame(header_frame, style="Header.TFrame")
        header_inner.pack(fill="x")
        
        ttk.Label(header_inner, text="🏷️ BARKOD & QR KOD STUDIO", style="Header.TLabel").pack(side="left")
        ttk.Label(header_inner, text="v2.5 Professional", font=("Segoe UI", 9, "bold"), background="#1E293B", foreground="#38BDF8", padding=(6, 2)).pack(side="left", padx=(10, 0))
        
        ttk.Label(header_frame, text="Sayı/Harf/TC'den Barkod & QR Kod Üretimi • Excel'e Canlı/Görselli Aktarım • A4 Çoklu Yazıcı Çıktısı", style="SubHeader.TLabel").pack(anchor="w", pady=(2, 0))

        # 2. Ana İçerik Alanı
        main_container = ttk.Frame(self.root, padding=12)
        main_container.pack(fill="both", expand=True)
        
        main_container.columnconfigure(0, weight=5)
        main_container.columnconfigure(1, weight=7)
        main_container.rowconfigure(0, weight=1)

        # ---------------- SOL PANEL (Form & Kod Seçimi & Canlı Önizleme) ----------------
        left_card = ttk.Frame(main_container, style="Card.TFrame", padding=14)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        left_header_box = ttk.Frame(left_card, style="Card.TFrame")
        left_header_box.pack(fill="x", pady=(0, 6))
        ttk.Label(left_header_box, text="Kod Bilgileri ve Barkod Ayarları", style="Title.TLabel").pack(side="left")
        
        btn_clear_form = ttk.Button(left_header_box, text="🧹 Temizle", style="Action.TButton", command=self.action_clear_form)
        btn_clear_form.pack(side="right")
        
        # Form Alanları
        form_frame = ttk.Frame(left_card, style="Card.TFrame")
        form_frame.pack(fill="x", pady=2)
        form_frame.columnconfigure(1, weight=1)
        
        # Kod Değeri / Sayı / Harf
        ttk.Label(form_frame, text="Barkod / Kod Değeri:", font=("Segoe UI", 9, "bold"), background="#FFFFFF", foreground="#1E293B").grid(row=0, column=0, sticky="w", pady=3)
        self.entry_tckn = ttk.Entry(form_frame, font=("Segoe UI", 10, "bold"))
        self.entry_tckn.grid(row=0, column=1, sticky="ew", pady=3, padx=(8, 0))
        self.entry_tckn.bind("<KeyRelease>", self.on_code_input)

        # İsim / Başlık (Opsiyonel)
        ttk.Label(form_frame, text="İsim / Başlık (Opsiyonel):", style="Normal.TLabel").grid(row=1, column=0, sticky="w", pady=3)
        self.entry_name = ttk.Entry(form_frame, font=("Segoe UI", 9))
        self.entry_name.grid(row=1, column=1, sticky="ew", pady=3, padx=(8, 0))
        self.entry_name.bind("<KeyRelease>", lambda e: self.auto_refresh_preview())
        
        # Soyisim / Detay (Opsiyonel)
        ttk.Label(form_frame, text="Soyisim / Ek Bilgi:", style="Normal.TLabel").grid(row=2, column=0, sticky="w", pady=3)
        self.entry_surname = ttk.Entry(form_frame, font=("Segoe UI", 9))
        self.entry_surname.grid(row=2, column=1, sticky="ew", pady=3, padx=(8, 0))
        self.entry_surname.bind("<KeyRelease>", lambda e: self.auto_refresh_preview())

        # Firma / Kurum Başlığı (Opsiyonel)
        ttk.Label(form_frame, text="Kurum / Firma Başlığı:", style="Normal.TLabel").grid(row=3, column=0, sticky="w", pady=3)
        self.entry_company = ttk.Entry(form_frame, font=("Segoe UI", 9), textvariable=self.var_company_title)
        self.entry_company.grid(row=3, column=1, sticky="ew", pady=3, padx=(8, 0))
        self.entry_company.bind("<KeyRelease>", lambda e: self.auto_refresh_preview())

        # Doğrulama Mesaj Alanı
        self.lbl_status = ttk.Label(left_card, text="Barkod veya QR koda dönüştürülecek sayı/harf değerini giriniz.", font=("Segoe UI", 9), foreground="#64748B", background="#FFFFFF")
        self.lbl_status.pack(anchor="w", pady=(2, 6))

        # Kod Türü ve Seçenekler Çerçevesi
        code_type_frame = ttk.LabelFrame(left_card, text=" Kod Formatı ve Türü ", style="Card.TLabelframe", padding=(8, 6))
        code_type_frame.pack(fill="x", pady=(0, 6))

        modes_box = ttk.Frame(code_type_frame, style="Card.TFrame")
        modes_box.pack(fill="x")

        rb_bc = ttk.Radiobutton(modes_box, text="📊 Çizgi Barkod (1D)", value="barcode", variable=self.var_code_mode, style="Card.TRadiobutton", command=self.on_mode_change)
        rb_bc.pack(side="left", padx=(0, 10))

        rb_qr = ttk.Radiobutton(modes_box, text="📱 QR Kod (2D)", value="qr", variable=self.var_code_mode, style="Card.TRadiobutton", command=self.on_mode_change)
        rb_qr.pack(side="left", padx=(0, 10))

        rb_both = ttk.Radiobutton(modes_box, text="🔄 QR + Barkod", value="both", variable=self.var_code_mode, style="Card.TRadiobutton", command=self.on_mode_change)
        rb_both.pack(side="left")

        # Barkod İnce Ayar Satırı
        bc_opt_box = ttk.Frame(code_type_frame, style="Card.TFrame")
        bc_opt_box.pack(fill="x", pady=(6, 0))

        ttk.Label(bc_opt_box, text="Tür:", style="Sub.TLabel").pack(side="left", padx=(0, 4))
        self.cb_bctype = ttk.Combobox(
            bc_opt_box,
            textvariable=self.var_barcode_type,
            values=[
                "Code 128 (Genel)",
                "Code 39 (Alfanümerik)",
                "EAN-13 (13 Hane)",
                "EAN-8 (8 Hane)",
                "UPC-A (12 Hane)"
            ],
            state="readonly",
            width=20,
            font=("Segoe UI", 8)
        )
        self.cb_bctype.current(0)
        self.cb_bctype.pack(side="left", padx=(0, 8))
        self.cb_bctype.bind("<<ComboboxSelected>>", lambda e: self.on_mode_change())

        chk_text = ttk.Checkbutton(bc_opt_box, text="Alt Yazı", variable=self.var_show_barcode_text, style="Card.TCheckbutton", command=self.auto_refresh_preview)
        chk_text.pack(side="left", padx=(0, 8))

        chk_strict = ttk.Checkbutton(bc_opt_box, text="Sıkı TC Kontrolü", variable=self.var_strict_tckn, style="Card.TCheckbutton", command=self.on_strict_toggle)
        chk_strict.pack(side="left")

        # Butonlar Satırı
        btn_frame = ttk.Frame(left_card, style="Card.TFrame")
        btn_frame.pack(fill="x", pady=(3, 6))
        
        btn_generate = ttk.Button(btn_frame, text="✨ Barkod Oluştur", style="Primary.TButton", command=self.action_generate_code)
        btn_generate.pack(side="left", fill="x", expand=True, padx=(0, 3))
        
        btn_save_worker = ttk.Button(btn_frame, text="➕ Listeye Ekle", style="Action.TButton", command=self.action_save_worker)
        btn_save_worker.pack(side="left", fill="x", expand=True, padx=3)

        btn_copy_image = ttk.Button(btn_frame, text="🖼️ Görseli Kopyala", style="Excel.TButton", command=self.action_copy_image_to_clipboard)
        btn_copy_image.pack(side="left", fill="x", expand=True, padx=(3, 0))

        # Önizleme Kutu Alanı
        preview_header_box = ttk.Frame(left_card, style="Card.TFrame")
        preview_header_box.pack(fill="x", pady=(2, 2))
        ttk.Label(preview_header_box, text="Kart & Baskı Önizlemesi", style="Title.TLabel").pack(side="left")
        ttk.Label(preview_header_box, text="(Excel'e Ctrl+V ile yapıştırabilirsiniz)", font=("Segoe UI", 8), foreground="#64748B", background="#FFFFFF").pack(side="right")
        
        self.preview_border = tk.Frame(left_card, bg="#CBD5E1", bd=1)
        self.preview_border.pack(fill="both", expand=True, pady=(0, 4))
        self.preview_border.bind("<Configure>", self.on_preview_resize)
        
        self.lbl_preview = tk.Label(self.preview_border, bg="#F8FAFC", text="Barkod / QR Kod Önizlemesi Burada Görünecektir", font=("Segoe UI", 9), fg="#64748B")
        self.lbl_preview.pack(fill="both", expand=True)
        
        # Alt Hızlı İşlem Butonları
        print_action_frame = ttk.Frame(left_card, style="Card.TFrame")
        print_action_frame.pack(fill="x", pady=(2, 0))
        
        btn_print = ttk.Button(print_action_frame, text="🖨️ Yazdır...", style="Success.TButton", command=self.action_print_current)
        btn_print.pack(side="left", fill="x", expand=True, padx=(0, 3))
        
        btn_export_png = ttk.Button(print_action_frame, text="💾 PNG Kaydet", style="Action.TButton", command=self.action_save_png)
        btn_export_png.pack(side="left", fill="x", expand=True, padx=3)

        btn_copy_tc = ttk.Button(print_action_frame, text="📋 Kodu Kopyala", style="Action.TButton", command=self.action_copy_tc)
        btn_copy_tc.pack(side="left", fill="x", expand=True, padx=(3, 0))

        # ---------------- SAĞ PANEL (Kayıtlı İşçiler & Toplu İşlemler) ----------------
        right_card = ttk.Frame(main_container, style="Card.TFrame", padding=14)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        
        right_top = ttk.Frame(right_card, style="Card.TFrame")
        right_top.pack(fill="x", pady=(0, 6))
        
        self.lbl_table_title = ttk.Label(right_top, text="Kayıtlı Kodlar Listesi", style="Title.TLabel")
        self.lbl_table_title.pack(side="left")
        
        search_frame = ttk.Frame(right_top, style="Card.TFrame")
        search_frame.pack(side="right")
        ttk.Label(search_frame, text="🔍 Ara:", style="Normal.TLabel").pack(side="left", padx=(0, 4))
        self.entry_search = ttk.Entry(search_frame, font=("Segoe UI", 9), width=20)
        self.entry_search.pack(side="left")
        self.entry_search.bind("<KeyRelease>", self.on_search)

        # Tablo (Treeview)
        table_frame = ttk.Frame(right_card, style="Card.TFrame")
        table_frame.pack(fill="both", expand=True)
        
        columns = ("id", "name", "surname", "tckn", "created_at")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="extended")
        
        self.tree.heading("id", text="ID ↕", command=lambda: self.sort_tree_column("id", False))
        self.tree.heading("name", text="İsim / Başlık ↕", command=lambda: self.sort_tree_column("name", False))
        self.tree.heading("surname", text="Soyisim / Detay ↕", command=lambda: self.sort_tree_column("surname", False))
        self.tree.heading("tckn", text="Barkod / Kod Değeri ↕", command=lambda: self.sort_tree_column("tckn", False))
        self.tree.heading("created_at", text="Kayıt Tarihi ↕", command=lambda: self.sort_tree_column("created_at", False))
        
        self.tree.column("id", width=45, anchor="center")
        self.tree.column("name", width=120)
        self.tree.column("surname", width=120)
        self.tree.column("tckn", width=140, anchor="center")
        self.tree.column("created_at", width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        
        # Sağ Tık Menüsü (Context Menu)
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="📊 Seçilenleri Excel Formatında Kopyala (Ctrl+C)", command=self.action_copy_table_selection)
        self.context_menu.add_command(label="🖼️ Önizlemedeki Tekli Görseli Kopyala (Ctrl+Shift+C)", command=self.action_copy_image_to_clipboard)
        self.context_menu.add_command(label="📑 Tüm Seçilenlerin A4 Çıktısını Kopyala (Word'e Yapıştır)", command=self.action_copy_selected_as_a4_to_clipboard)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📋 Excel Panosundan Yapıştır (Ctrl+V)", command=self.action_paste_from_clipboard)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🖨️ Seçilenleri Yazdır (Ctrl+P)", command=self.action_print_selected)
        self.context_menu.add_command(label="🗑️ Seçilenleri Sil (Delete)", command=self.action_delete_worker)
        
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Alt Buton Grubu - Üst Satır (Excel & Seri Üretim)
        excel_action_frame = ttk.Frame(right_card, style="Card.TFrame")
        excel_action_frame.pack(fill="x", pady=(6, 4))
        
        btn_paste_clip = ttk.Button(excel_action_frame, text="📋 Excel'den Yapıştır (Pano)", style="Excel.TButton", command=self.action_paste_from_clipboard)
        btn_paste_clip.pack(side="left", padx=(0, 4))
        
        btn_export_xlsx = ttk.Button(excel_action_frame, text="📊 Excel'e Aktar (.xlsx)...", style="Excel.TButton", command=self.open_export_excel_dialog)
        btn_export_xlsx.pack(side="left", padx=4)

        btn_seq_gen = ttk.Button(excel_action_frame, text="🔢 Seri / Sıralı Kod Üret", style="Action.TButton", command=self.open_serial_generator_dialog)
        btn_seq_gen.pack(side="left", padx=4)

        btn_copy_excel = ttk.Button(excel_action_frame, text="📑 Tabloyu Kopyala", style="Action.TButton", command=self.action_copy_table_selection)
        btn_copy_excel.pack(side="right")

        # Alt Buton Grubu - İkinci Satır (Yazdırma, Dosyadan Aktarım & Silme)
        bottom_btn_frame = ttk.Frame(right_card, style="Card.TFrame")
        bottom_btn_frame.pack(fill="x", pady=(2, 0))
        
        btn_print_selected = ttk.Button(bottom_btn_frame, text="🖨️ Seçilenleri Yazdır (A4)", style="Success.TButton", command=self.action_print_selected)
        btn_print_selected.pack(side="left", padx=(0, 4))
        
        btn_import_excel = ttk.Button(bottom_btn_frame, text="📂 Excel Dosyası Seç", style="Action.TButton", command=self.action_import_excel)
        btn_import_excel.pack(side="left", padx=4)
        
        btn_export_bulk = ttk.Button(bottom_btn_frame, text="📁 Toplu Resim Aktar...", style="Action.TButton", command=self.action_export_bulk_dialog)
        btn_export_bulk.pack(side="left", padx=4)
        btn_delete = ttk.Button(bottom_btn_frame, text="🗑️ Seçileni Sil", style="Danger.TButton", command=self.action_delete_worker)
        btn_delete.pack(side="right")
        
        btn_delete_all = ttk.Button(bottom_btn_frame, text="🧨 Tümünü Temizle", style="Danger.TButton", command=self.action_delete_all_workers)
        btn_delete_all.pack(side="right", padx=(0, 4))

        # 3. En Alt Durum Çubuğu
        self.status_bar_frame = ttk.Frame(self.root, style="Header.TFrame", padding=(15, 6))
        self.status_bar_frame.pack(fill="x", side="bottom")
        
        self.status_bar = ttk.Label(self.status_bar_frame, text="Sistem hazır.", font=("Segoe UI", 9), foreground="#E2E8F0", background="#0F172A")
        self.status_bar.pack(side="left")

        self.status_counter = ttk.Label(self.status_bar_frame, text="0 Kayıt", font=("Segoe UI", 9, "bold"), foreground="#38BDF8", background="#0F172A")
        self.status_counter.pack(side="right")

    def bind_shortcuts(self):
        """Klavye kısayollarını tanımlar."""
        self.root.bind("<Control-c>", lambda e: self.on_ctrl_c(e))
        self.root.bind("<Control-Shift-C>", lambda e: self.action_copy_image_to_clipboard())
        self.root.bind("<Control-Shift-c>", lambda e: self.action_copy_image_to_clipboard())
        self.root.bind("<Control-v>", lambda e: self.on_ctrl_v(e))
        self.root.bind("<Control-a>", lambda e: self.on_ctrl_a(e))
        self.root.bind("<Control-p>", lambda e: self.action_print_selected())
        self.root.bind("<Delete>", lambda e: self.on_delete_key(e))

    def on_ctrl_c(self, event):
        """Ctrl+C tuşuna basıldığında odak tablodaysa seçili satırları Excel formatında kopyalar."""
        focused = self.root.focus_get()
        if isinstance(focused, (tk.Entry, ttk.Entry)):
            return
        self.action_copy_table_selection()

    def on_ctrl_v(self, event):
        """Ctrl+V tuşuna basıldığında odak tablodaysa panodaki Excel verilerini aktarır."""
        focused = self.root.focus_get()
        if isinstance(focused, (tk.Entry, ttk.Entry)):
            return
        self.action_paste_from_clipboard()

    def on_ctrl_a(self, event):
        """Ctrl+A ile tablodaki tüm satırları seçer."""
        focused = self.root.focus_get()
        if isinstance(focused, (tk.Entry, ttk.Entry)):
            return
        for item in self.tree.get_children():
            self.tree.selection_add(item)
        return "break"

    def on_delete_key(self, event):
        """Delete tuşuna basıldığında seçili satırları siler."""
        focused = self.root.focus_get()
        if isinstance(focused, (tk.Entry, ttk.Entry)):
            return
        self.action_delete_worker()

    def show_context_menu(self, event):
        """Sağ tıklandığında menüyü açar."""
        item = self.tree.identify_row(event.y)
        if item:
            if item not in self.tree.selection():
                self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def get_clean_barcode_type(self) -> str:
        """Combobox değerinden clean barcode type döndürür."""
        val = self.var_barcode_type.get().lower()
        if "ean-13" in val or "ean13" in val:
            return "ean13"
        elif "ean-8" in val or "ean8" in val:
            return "ean8"
        elif "upc" in val:
            return "upca"
        elif "39" in val:
            return "code39"
        return "code128"

    def update_printer_list(self):
        """Varsayılan yazıcı bilgisini durum çubuğunda gösterir."""
        default_p = printer_service.get_default_printer()
        if default_p:
            self.set_status(f"Hazır | Varsayılan Yazıcı: {default_p}")
        else:
            self.set_status("Hazır | Sistemde varsayılan yazıcı bulunamadı.")

    def set_status(self, msg: str):
        """Durum çubuğunu günceller."""
        self.status_bar.config(text=msg)

    def on_mode_change(self):
        """Kod formatı değiştiğinde önizlemeyi yeniler."""
        self.auto_refresh_preview()

    def on_strict_toggle(self):
        """Sıkı TC kontrolü açılıp kapandığında denetimi yeniler."""
        self.on_code_input(None)

    def action_clear_form(self):
        """Form alanlarını temizler."""
        self.entry_name.delete(0, tk.END)
        self.entry_surname.delete(0, tk.END)
        self.entry_tckn.delete(0, tk.END)
        self.lbl_status.config(text="Form temizlendi. Yeni değer girebilirsiniz.", foreground="#64748B")
        self.lbl_preview.config(image="", text="Barkod / QR Kod Önizlemesi Burada Görünecektir")
        self.lbl_preview.image = None
        self.current_badge_image = None
        self.current_worker_data = None
        self.entry_tckn.focus_set()

    def on_code_input(self, event):
        """Kod alanına yazıldıkça canlı denetler ve önizler."""
        val = self.entry_tckn.get().strip()
        strict = self.var_strict_tckn.get()
        b_type = self.get_clean_barcode_type()
        
        if not val:
            self.lbl_status.config(text="Barkod veya QR koda dönüştürülecek sayı/harf değerini giriniz.", foreground="#64748B")
            return

        is_valid, msg = qr_generator.validate_code_value(val, strict_tckn=strict, barcode_type=b_type)
        if is_valid:
            self.lbl_status.config(text="✓ " + msg, foreground="#059669")
            self.auto_refresh_preview()
        else:
            self.lbl_status.config(text="⚠ " + msg, foreground="#DC2626")

    def auto_refresh_preview(self):
        """Geçerli bir kod varsa önizlemeyi anında yeniler."""
        code_val = self.entry_tckn.get().strip()
        if code_val:
            strict = self.var_strict_tckn.get()
            b_type = self.get_clean_barcode_type()
            is_valid, _ = qr_generator.validate_code_value(code_val, strict_tckn=strict, barcode_type=b_type)
            if is_valid:
                self.action_generate_code(silent=True)

    def on_preview_resize(self, event):
        """Pencere boyutu değiştiğinde önizleme görselini orantılı yeniden ölçekler."""
        if self.current_badge_image:
            if self._resize_timer:
                self.root.after_cancel(self._resize_timer)
            self._resize_timer = self.root.after(100, lambda: self.display_preview(self.current_badge_image))

    def action_generate_code(self, silent: bool = False):
        """Girilen bilgilere göre Barkod / QR / Kombine kart oluşturup önizler."""
        name = self.entry_name.get().strip()
        surname = self.entry_surname.get().strip()
        code_val = self.entry_tckn.get().strip()
        company = self.var_company_title.get().strip()
        strict = self.var_strict_tckn.get()
        barcode_type = self.get_clean_barcode_type()
        
        is_valid, msg = qr_generator.validate_code_value(code_val, strict_tckn=strict, barcode_type=barcode_type)
        if not is_valid:
            if not silent:
                messagebox.showwarning("Geçersiz Kod Değeri", msg)
            return
            
        code_mode = self.var_code_mode.get()
        show_text = self.var_show_barcode_text.get()

        # Kart Görseli Üret
        self.current_badge_image = qr_generator.create_printable_badge(
            name=name,
            surname=surname,
            code_value=code_val,
            code_mode=code_mode,
            barcode_type=barcode_type,
            show_barcode_text=show_text,
            company_title=company
        )
        self.current_worker_data = {"name": name, "surname": surname, "tckn": code_val, "company": company}
        
        # Önizlemeyi Güncelle
        self.display_preview(self.current_badge_image)
        mode_label = "Barkod (" + barcode_type.upper() + ")" if code_mode == "barcode" else ("QR Kod" if code_mode == "qr" else "QR + Barkod")
        self.set_status(f"{mode_label} oluşturuldu: {code_val}")

    def display_preview(self, pil_image: Image.Image):
        """PIL Görselini ekrandaki önizleme kutusuna boyutlandırıp yerleştirir."""
        if not pil_image:
            return
        box_w = self.preview_border.winfo_width()
        box_h = self.preview_border.winfo_height()
        if box_w < 50 or box_h < 50:
            box_w, box_h = 420, 260
        
        img_copy = pil_image.copy()
        img_copy.thumbnail((box_w - 16, box_h - 16), Image.Resampling.LANCZOS)
        
        tk_img = ImageTk.PhotoImage(img_copy)
        self.lbl_preview.config(image=tk_img, text="")
        self.lbl_preview.image = tk_img

    def action_copy_image_to_clipboard(self):
        """Şu an önizlenen görseli doğrudan Windows Panosuna (Bitmap) kopyalar. Excel'de Ctrl+V ile resim yapışır!"""
        if self.current_badge_image is None:
            code_val = self.entry_tckn.get().strip()
            if code_val:
                self.action_generate_code(silent=True)
                
        if self.current_badge_image is None:
            messagebox.showwarning("Uyarı", "Kopyalanacak bir barkod görseli henüz oluşturulmadı!")
            return
            
        success = qr_generator.copy_image_to_clipboard(self.current_badge_image)
        if success:
            code_str = self.current_worker_data.get("tckn", "") if self.current_worker_data else ""
            msg = f"✓ Barkod görseli panoya kopyalandı!\nExcel, Word veya Paint'e geçip Ctrl+V ile doğrudan resim olarak yapıştırabilirsiniz."
            self.set_status(f"Görsel Panoya Kopyalandı (Excel'e Ctrl+V yapıştırabilirsiniz) - Kod: {code_str}")
            messagebox.showinfo("Panoya Kopyalandı", msg)
        else:
            messagebox.showerror("Hata", "Görsel panoya kopyalanırken hata oluştu.")

    def action_copy_selected_as_a4_to_clipboard(self):
        """Tabloda seçili kayıtları A4 sayfalarına dizip Word'e yapıştırılabilir şekilde panoya kopyalar."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen önce tablodan kopyalanacak kayıtları seçiniz.")
            return
            
        workers = []
        for item in selected:
            item_values = self.tree.item(item, "values")
            if item_values:
                _, name, surname, code_val, _ = item_values
                workers.append((name, surname, str(code_val)))
                
        code_mode = self.var_code_mode.get()
        barcode_type = self.get_clean_barcode_type()
        show_text = self.var_show_barcode_text.get()
        company = self.var_company_title.get().strip()
        
        self.set_status("A4 sayfaları oluşturuluyor, lütfen bekleyiniz...")
        self.root.update_idletasks()
        
        pages = qr_generator.create_grid_printable_pages(
            workers,
            items_per_row=3,
            rows_per_page=4,
            code_mode=code_mode,
            barcode_type=barcode_type,
            show_barcode_text=show_text,
            company_title=company
        )
        
        if not pages:
            self.set_status("Kopyalanacak görsel oluşturulamadı.")
            return
            
        success = qr_generator.copy_files_to_clipboard_as_hdrop(pages)
        if success:
            messagebox.showinfo("Kopyalandı", f"{len(workers)} kayıt {len(pages)} sayfa A4 düzeninde panoya kopyalandı.\nWord'e geçip Ctrl+V ile yapıştırdığınızda sayfalar halinde dizilecektir!")
            self.set_status(f"{len(pages)} sayfa A4 görseli panoya kopyalandı.")
        else:
            messagebox.showerror("Hata", "Panoya kopyalama başarısız oldu.")
            self.set_status("Pano hatası.")

    def action_copy_tc(self):
        """Barkod / Kod metin değerini panoya kopyalar."""
        code_val = self.entry_tckn.get().strip()
        if not code_val:
            messagebox.showwarning("Uyarı", "Kopyalanacak kod değeri bulunamadı.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(code_val)
        self.set_status(f"Kod panoya kopyalandı: {code_val}")

    def action_copy_table_selection(self):
        """Tabloda seçili satırları Excel uyumlu Tab-Separated (TSV) formatında panoya kopyalar."""
        selected = self.tree.selection()
        if not selected:
            selected = self.tree.get_children()
            
        if not selected:
            messagebox.showwarning("Uyarı", "Tabloda kopyalanacak kayıt bulunamadı.")
            return
            
        lines = ["Sıra\tİsim / Başlık\tSoyisim / Detay\tBarkod / Kod Değeri\tKayıt Tarihi"]
        for item in selected:
            vals = self.tree.item(item, "values")
            if vals:
                lines.append("\t".join(str(v) for v in vals))
                
        clipboard_text = "\n".join(lines)
        self.root.clipboard_clear()
        self.root.clipboard_append(clipboard_text)
        
        self.set_status(f"{len(selected)} kayıt Excel formatında panoya kopyalandı (Excel'de Ctrl+V yapın).")
        messagebox.showinfo("Excel İçin Kopyalandı", f"{len(selected)} kayıt başarıyla panoya kopyalandı!\nExcel sayfasına geçip dilediğiniz hücreye Ctrl+V ile yapıştırabilirsiniz.")

    def action_paste_from_clipboard(self):
        """Panodaki (Excel'den kopyalanmış) sekmeli veya satırlı metni anında içeri aktarır."""
        try:
            raw_text = self.root.clipboard_get()
        except Exception:
            messagebox.showwarning("Pano Boş", "Panoda yapıştırılacak metin bulunamadı.\nLütfen önce Excel'den satırları seçip Ctrl+C ile kopyalayınız.")
            return
            
        if not raw_text or not raw_text.strip():
            messagebox.showwarning("Pano Boş", "Panodaki metin boş.")
            return
            
        workers_found = qr_generator.parse_clipboard_table_text(raw_text)
        if not workers_found:
            messagebox.showwarning("Kayıt Bulunamadı", "Panodaki metinden geçerli bir kod veya kayıt çıkarılamadı.")
            return
            
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        imported_count = 0
        skipped_count = 0
        
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            for w in workers_found:
                name = w["name"]
                surname = w["surname"]
                code_val = w["tckn"]
                try:
                    cursor.execute("INSERT INTO workers (name, surname, tckn, created_at) VALUES (?, ?, ?, ?)",
                                   (name, surname, code_val, created_at))
                    imported_count += 1
                except sqlite3.IntegrityError:
                    skipped_count += 1
            conn.commit()
        
        self.refresh_worker_list()
        msg = f"✓ Panodan Tespit Edilen: {len(workers_found)} kayıt\n✓ Başarıyla Eklenen: {imported_count} yeni kayıt\n⚠ Atlanan (Sistemde Zaten Kayıtlı): {skipped_count}"
        messagebox.showinfo("Panodan Aktarım Başarılı", msg)
        self.set_status(f"Excel Panosundan {imported_count} kayıt eklendi.")

    def open_export_excel_dialog(self):
        """Excel'e aktarma seçenekleri (Metin Tablosu vs Resimli Hücreler) sunar."""
        selected = self.tree.selection()
        if not selected:
            selected = self.tree.get_children()
            
        if not selected:
            messagebox.showwarning("Uyarı", "Excel'e aktarılacak kayıt bulunamadı.")
            return

        records = [self.tree.item(item, "values") for item in selected if self.tree.item(item, "values")]

        dialog = tk.Toplevel(self.root)
        dialog.title("Excel Dışa Aktarma Seçenekleri")
        dialog.geometry("450x260")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="📊 Excel'e Aktar (.xlsx)", font=("Segoe UI", 12, "bold")).pack(pady=(15, 8))
        ttk.Label(dialog, text=f"Toplam {len(records)} kayıt aktarılacak. Formatı seçiniz:", style="Normal.TLabel").pack(pady=(0, 10))

        var_opt = tk.StringVar(value="with_images")

        rb1 = ttk.Radiobutton(dialog, text="🖼️ Görselli Excel Tablosu (Barkod resimleri hücrelere gömülür)", value="with_images", variable=var_opt)
        rb1.pack(anchor="w", padx=25, pady=4)

        rb2 = ttk.Radiobutton(dialog, text="📄 Standart Metin Tablosu (Hızlı & Sade veri tablosu)", value="text_only", variable=var_opt)
        rb2.pack(anchor="w", padx=25, pady=4)

        def do_export():
            dialog.destroy()
            default_filename = f"Barkod_Listesi_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Dosyası", "*.xlsx"), ("Tüm Dosyalar", "*.*")],
                initialfile=default_filename
            )
            if not filepath:
                return

            include_img = (var_opt.get() == "with_images")
            code_mode = self.var_code_mode.get()
            b_type = self.get_clean_barcode_type()

            self.set_status("Excel dosyası oluşturuluyor, lütfen bekleyiniz...")
            self.root.update_idletasks()

            try:
                qr_generator.export_records_to_excel(
                    records=records,
                    filepath=filepath,
                    include_images=include_img,
                    code_mode=code_mode,
                    barcode_type=b_type
                )
                messagebox.showinfo("Excel'e Aktarıldı", f"Toplam {len(records)} kayıt başarıyla Excel dosyasına aktarıldı:\n{filepath}")
                self.set_status(f"Excel dosyası oluşturuldu: {filepath}")
            except Exception as e:
                messagebox.showerror("Hata", f"Excel kaydedilirken hata oluştu:\n{str(e)}")
                self.set_status("Excel aktarımında hata oluştu.")

        btn_box = ttk.Frame(dialog, padding=15)
        btn_box.pack(fill="x", side="bottom")

        ttk.Button(btn_box, text="Dışa Aktar", style="Excel.TButton", command=do_export).pack(side="right", padx=(5, 0))
        ttk.Button(btn_box, text="İptal", style="Action.TButton", command=dialog.destroy).pack(side="right", padx=(0, 5))

    def open_serial_generator_dialog(self):
        """Toplu sıralı / seri barkod üretim penceresini açar."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Sıralı / Seri Barkod Üretici")
        dialog.geometry("480x370")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="🔢 Toplu Sıralı / Seri Kod Üretici", font=("Segoe UI", 12, "bold")).pack(pady=(15, 10))

        form_box = ttk.Frame(dialog, padding=15)
        form_box.pack(fill="x")
        form_box.columnconfigure(1, weight=1)

        ttk.Label(form_box, text="Başlangıç Numarası:", style="Normal.TLabel").grid(row=0, column=0, sticky="w", pady=4)
        entry_start = ttk.Entry(form_box, font=("Segoe UI", 9))
        entry_start.insert(0, "1001")
        entry_start.grid(row=0, column=1, sticky="ew", pady=4, padx=(10, 0))

        ttk.Label(form_box, text="Üretilecek Adet:", style="Normal.TLabel").grid(row=1, column=0, sticky="w", pady=4)
        entry_count = ttk.Entry(form_box, font=("Segoe UI", 9))
        entry_count.insert(0, "50")
        entry_count.grid(row=1, column=1, sticky="ew", pady=4, padx=(10, 0))

        ttk.Label(form_box, text="Ön Ek (Örn: URUN-):", style="Normal.TLabel").grid(row=2, column=0, sticky="w", pady=4)
        entry_prefix = ttk.Entry(form_box, font=("Segoe UI", 9))
        entry_prefix.insert(0, "URUN-")
        entry_prefix.grid(row=2, column=1, sticky="ew", pady=4, padx=(10, 0))

        ttk.Label(form_box, text="Basamak (Sıfırla Doldurma):", style="Normal.TLabel").grid(row=3, column=0, sticky="w", pady=4)
        entry_pad = ttk.Entry(form_box, font=("Segoe UI", 9))
        entry_pad.insert(0, "4")
        entry_pad.grid(row=3, column=1, sticky="ew", pady=4, padx=(10, 0))

        ttk.Label(form_box, text="İsim Şablonu (Opsiyonel):", style="Normal.TLabel").grid(row=4, column=0, sticky="w", pady=4)
        entry_itemname = ttk.Entry(form_box, font=("Segoe UI", 9))
        entry_itemname.insert(0, "Ürün #{no}")
        entry_itemname.grid(row=4, column=1, sticky="ew", pady=4, padx=(10, 0))

        def generate_and_save_serial():
            try:
                start_num = int(entry_start.get().strip())
                count = int(entry_count.get().strip())
                prefix = entry_prefix.get().strip()
                pad_len = int(entry_pad.get().strip() or "0")
                name_tpl = entry_itemname.get().strip()
                
                if count <= 0 or count > 5000:
                    messagebox.showwarning("Geçersiz Adet", "Üretilecek adet 1 ile 5000 arasında olmalıdır.")
                    return
            except ValueError:
                messagebox.showerror("Hata", "Lütfen başlangıç numarası, adet ve basamak alanlarına geçerli tamsayılar giriniz.")
                return

            dialog.destroy()
            items = qr_generator.generate_sequential_codes(
                start_num=start_num,
                count=count,
                prefix=prefix,
                pad_length=pad_len,
                name_template=name_tpl
            )

            created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
            added = 0
            skipped = 0
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                for itm in items:
                    try:
                        cursor.execute("INSERT INTO workers (name, surname, tckn, created_at) VALUES (?, ?, ?, ?)",
                                       (itm["name"], itm["surname"], itm["tckn"], created_at))
                        added += 1
                    except sqlite3.IntegrityError:
                        skipped += 1
                conn.commit()

            self.refresh_worker_list()
            messagebox.showinfo("Seri Üretim Tamamlandı", f"✓ {added} adet sıralı barkod listeye eklendi.\n⚠ Atlanan (Zaten Kayıtlı): {skipped}")
            self.set_status(f"{added} adet sıralı barkod oluşturuldu ({prefix}{start_num}...)")

        btn_box = ttk.Frame(dialog, padding=15)
        btn_box.pack(fill="x", side="bottom")

        ttk.Button(btn_box, text="Üret ve Listeye Ekle", style="Success.TButton", command=generate_and_save_serial).pack(side="right", padx=(5, 0))
        ttk.Button(btn_box, text="İptal", style="Action.TButton", command=dialog.destroy).pack(side="right", padx=(0, 5))

    def action_save_worker(self):
        """Girişi yapılan kaydı veritabanına ekler."""
        name = self.entry_name.get().strip()
        surname = self.entry_surname.get().strip()
        code_val = self.entry_tckn.get().strip()
        strict = self.var_strict_tckn.get()
        barcode_type = self.get_clean_barcode_type()
        
        is_valid, msg = qr_generator.validate_code_value(code_val, strict_tckn=strict, barcode_type=barcode_type)
        if not is_valid:
            messagebox.showwarning("Geçersiz Değer", msg)
            return
            
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO workers (name, surname, tckn, created_at) VALUES (?, ?, ?, ?)",
                               (name, surname, code_val, created_at))
                conn.commit()
            label_disp = f"'{name} {surname}' ({code_val})" if (name or surname) else f"'{code_val}'"
            messagebox.showinfo("Başarılı", f"Kayıt {label_disp} başarıyla kaydedildi.")
            self.refresh_worker_list()
        except sqlite3.IntegrityError:
            messagebox.showerror("Hata", "Bu kod değeri sistemde zaten kayıtlı!")

    def sort_tree_column(self, col: str, reverse: bool):
        """Tablodaki verileri tıklanan sütun başlığına göre sıralar."""
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children("")]
        
        # ID veya sayısal sütunlar için int sıralaması
        if col == "id":
            try:
                data.sort(key=lambda t: int(t[0]), reverse=reverse)
            except ValueError:
                data.sort(reverse=reverse)
        else:
            data.sort(reverse=reverse)

        for index, (_, child) in enumerate(data):
            self.tree.move(child, "", index)

        # Başlık ok göstergelerini güncelle
        headings = {
            "id": "ID",
            "name": "İsim / Başlık",
            "surname": "Soyisim / Detay",
            "tckn": "Barkod / Kod Değeri",
            "created_at": "Kayıt Tarihi"
        }
        for c, title in headings.items():
            if c == col:
                arrow = " 🔽" if reverse else " 🔼"
                self.tree.heading(c, text=f"{title}{arrow}", command=lambda c=c: self.sort_tree_column(c, not reverse))
            else:
                self.tree.heading(c, text=f"{title} ↕", command=lambda c=c: self.sort_tree_column(c, False))

    def refresh_worker_list(self, query: str = ""):
        """Veritabanındaki listeyi tabloya doldurur."""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            if query:
                q = f"%{query}%"
                cursor.execute("SELECT id, name, surname, tckn, created_at FROM workers WHERE name LIKE ? OR surname LIKE ? OR tckn LIKE ?", (q, q, q))
            else:
                cursor.execute("SELECT id, name, surname, tckn, created_at FROM workers ORDER BY id DESC")
            rows = cursor.fetchall()
        
        for row in rows:
            self.tree.insert("", "end", values=row)

        self.lbl_table_title.config(text=f"Kayıtlı Kodlar Listesi ({len(rows)} Kayıt)")
        self.status_counter.config(text=f"Toplam: {len(rows)} Kayıt")

    def on_search(self, event):
        """Arama kutusuna yazıldıkça tabloyu filtreler."""
        q = self.entry_search.get().strip()
        self.refresh_worker_list(q)

    def on_tree_select(self, event):
        """Tablodan bir kayıt seçildiğinde forma doldurur, istatistik günceller ve barkod oluşturur."""
        selected = self.tree.selection()
        if not selected:
            return
            
        sel_count = len(selected)
        total_count = len(self.tree.get_children())
        self.status_counter.config(text=f"Seçilen: {sel_count} / Toplam: {total_count}")
        
        item_values = self.tree.item(selected[0], "values")
        if item_values:
            _, name, surname, code_val, _ = item_values
            
            self.entry_name.delete(0, tk.END)
            self.entry_name.insert(0, name)
            
            self.entry_surname.delete(0, tk.END)
            self.entry_surname.insert(0, surname)
            
            self.entry_tckn.delete(0, tk.END)
            self.entry_tckn.insert(0, code_val)
            
            self.action_generate_code(silent=True)

    def on_tree_double_click(self, event):
        """Çift tıklandığında hızlı yazdırma veya önizleme penceresini hedefler."""
        selected = self.tree.selection()
        if selected:
            self.action_generate_code()

    def action_print_current(self):
        """Şu an önizlenen kartı yazıcı seçimi penceresi açarak yazdırır."""
        if self.current_badge_image is None:
            code_val = self.entry_tckn.get().strip()
            if code_val:
                self.action_generate_code()
            else:
                messagebox.showwarning("Uyarı", "Yazdırılacak bir kod henüz oluşturulmadı!")
                return
                
        if self.current_badge_image is None:
            return

        self.open_printer_select_dialog(self.current_badge_image, doc_name="Barkod / Kart Çıktısı")

    def action_print_selected(self):
        """Tabloda seçili kayıtları A4 sayfasına 3'lü dizilimde yerleştirip yazdırır."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen önce tablodan yazdırılacak en az 1 kayıt seçiniz.\n(Birden fazla seçim için Ctrl veya Shift tuşunu kullanabilirsiniz).")
            return
            
        workers = []
        for item in selected:
            item_values = self.tree.item(item, "values")
            if item_values:
                _, name, surname, code_val, _ = item_values
                workers.append((name, surname, str(code_val)))
                
        code_mode = self.var_code_mode.get()
        barcode_type = self.get_clean_barcode_type()
        show_text = self.var_show_barcode_text.get()
        company = self.var_company_title.get().strip()

        if len(workers) == 1:
            name, surname, code_val = workers[0]
            badge_img = qr_generator.create_printable_badge(
                name, surname, code_val,
                code_mode=code_mode,
                barcode_type=barcode_type,
                show_barcode_text=show_text,
                company_title=company
            )
            self.display_preview(badge_img)
            self.open_printer_select_dialog(badge_img, doc_name=f"Barkod Kartı - {code_val}")
        else:
            pages = qr_generator.create_grid_printable_pages(
                workers,
                items_per_row=3,
                rows_per_page=4,
                code_mode=code_mode,
                barcode_type=barcode_type,
                show_barcode_text=show_text,
                company_title=company
            )
            if pages:
                self.display_preview(pages[0])
                self.open_printer_select_dialog(pages, doc_name=f"Barkod Kartları - {len(workers)} Adet")

    def open_printer_select_dialog(self, print_target, doc_name: str = "Barkod Kartı"):
        """Kullanıcının bilgisayarındaki yazıcıları listeleyen pencere açar."""
        printers = printer_service.get_installed_printers()
        default_p = printer_service.get_default_printer()
        
        if not printers:
            messagebox.showerror("Yazıcı Bulunamadı", "Sisteminizde tanımlı hiçbir yazıcı bulunamadı!")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Yazıcı Seçimi ve Çıktı Alma")
        dialog.geometry("460x270")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="🖨️ Çıktı Alınacak Yazıcıyı Seçiniz", font=("Segoe UI", 12, "bold")).pack(pady=(15, 10))

        combo_frame = ttk.Frame(dialog, padding=10)
        combo_frame.pack(fill="x")
        
        ttk.Label(combo_frame, text="Yazıcı Listesi:", style="Normal.TLabel").pack(anchor="w", pady=(0, 5))
        
        combo_printers = ttk.Combobox(combo_frame, values=printers, font=("Segoe UI", 10), state="readonly")
        combo_printers.pack(fill="x")
        
        if default_p in printers:
            combo_printers.set(default_p)
        elif printers:
            combo_printers.set(printers[0])

        is_multi = isinstance(print_target, list)
        page_info_text = f"Toplam {len(print_target)} sayfa A4 formatında 3'lü dizilimle yazdırılacaktır." if is_multi else "Görsel seçilen yazıcı sayfasına sığdırılacaktır."
        info_lbl = ttk.Label(dialog, text=page_info_text, font=("Segoe UI", 9), foreground="#64748B")
        info_lbl.pack(pady=5)

        def start_printing():
            selected_printer = combo_printers.get()
            if not selected_printer:
                messagebox.showwarning("Uyarı", "Lütfen bir yazıcı seçiniz!")
                return
                
            dialog.destroy()
            self.set_status(f"Yazdırılıyor... ({selected_printer})")
            
            if is_multi:
                success, msg = printer_service.print_images_to_printer(print_target, selected_printer, doc_name=doc_name)
            else:
                success, msg = printer_service.print_image_to_printer(print_target, selected_printer, doc_name=doc_name)
                
            if success:
                messagebox.showinfo("Başarılı", f"Yazdırma işlemi tamamlandı:\n{msg}")
                self.set_status(f"Yazdırıldı: {selected_printer}")
            else:
                messagebox.showerror("Yazdırma Hatası", msg)
                self.set_status("Yazdırma sırasında hata oluştu.")

        btn_box = ttk.Frame(dialog, padding=15)
        btn_box.pack(fill="x", side="bottom")
        
        ttk.Button(btn_box, text="Yazdır", style="Success.TButton", command=start_printing).pack(side="right", padx=(5, 0))
        ttk.Button(btn_box, text="İptal", style="Action.TButton", command=dialog.destroy).pack(side="right", padx=(0, 5))

    def action_save_png(self):
        """Oluşturulan kart veya kod görselini PNG dosyası olarak kaydeder."""
        if self.current_badge_image is None:
            messagebox.showwarning("Uyarı", "Kaydedilecek bir kod görseli oluşturulmadı!")
            return
            
        code_val = self.current_worker_data.get("tckn", "kod") if self.current_worker_data else "kod"
        name = self.current_worker_data.get("name", "") if self.current_worker_data else ""
        mode = self.var_code_mode.get()
        
        clean_name = f"_{name}".strip() if name else ""
        default_filename = f"{mode.upper()}{clean_name}_{code_val}.png".replace(" ", "_")
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Görseli", "*.png"), ("Tüm Dosyalar", "*.*")],
            initialfile=default_filename
        )
        if filepath:
            self.current_badge_image.save(filepath)
            messagebox.showinfo("Başarılı", f"Görsel başarıyla kaydedildi:\n{filepath}")

    def action_delete_worker(self):
        """Seçili kaydı veritabanından siler."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Silinecek kaydı tablodan seçiniz.")
            return
            
        count = len(selected)
        confirm = messagebox.askyesno("Silme Onayı", f"Seçilen {count} adet kaydı silmek istediğinize emin misiniz?")
        if confirm:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                for item in selected:
                    item_values = self.tree.item(item, "values")
                    if item_values:
                        worker_id = item_values[0]
                        cursor.execute("DELETE FROM workers WHERE id = ?", (worker_id,))
                conn.commit()
            
            messagebox.showinfo("Silindi", f"{count} adet kayıt başarıyla silindi.")
            self.refresh_worker_list()

    def action_delete_all_workers(self):
        """Veritabanındaki tüm kayıtları temizler."""
        items = self.tree.get_children()
        if not items:
            messagebox.showwarning("Uyarı", "Tablo zaten boş.")
            return
            
        confirm = messagebox.askyesno(
            "Tümünü Temizleme Onayı", 
            "DİKKAT: Tablodaki TÜM kayıtları silmek istediğinize emin misiniz?\nBu işlem geri alınamaz!",
            icon='warning'
        )
        if confirm:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM workers")
                conn.commit()
            
            messagebox.showinfo("Temizlendi", "Tüm kayıtlar başarıyla silindi.")
            self.refresh_worker_list()

    def action_import_excel(self):
        """Excel veya CSV dosyasından toplu kayıt aktarır."""
        filepath = filedialog.askopenfilename(filetypes=[("Excel / CSV Dosyaları", "*.xlsx *.csv *.xls"), ("Tüm Dosyalar", "*.*")])
        if not filepath:
            return
            
        try:
            workers_found = qr_generator.smart_parse_excel_or_csv(filepath)
            
            if not workers_found:
                messagebox.showwarning("Kayıt Bulunamadı", "Dosyada aktarılabilecek geçerli kod veya TC kimlik numarası bulunamadı.")
                return

            imported_count = 0
            skipped_count = 0
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                for w in workers_found:
                    name = w["name"]
                    surname = w["surname"]
                    code_val = w["tckn"]
                    try:
                        cursor.execute("INSERT INTO workers (name, surname, tckn, created_at) VALUES (?, ?, ?, ?)",
                                       (name, surname, code_val, created_at))
                        imported_count += 1
                    except sqlite3.IntegrityError:
                        skipped_count += 1
                conn.commit()
            
            msg = f"✓ Toplam Tespit Edilen: {len(workers_found)} kayıt\n✓ İçe Aktarılan: {imported_count} yeni kayıt\n⚠ Atlanan (Sistemde Zaten Kayıtlı): {skipped_count}"
            messagebox.showinfo("İçe Aktarma Başarılı", msg)
            self.refresh_worker_list()
            self.set_status(f"Excel'den {imported_count} kayıt eklendi.")
            
        except Exception as e:
            messagebox.showerror("İçe Aktarma Hatası", f"Dosya işlenirken hata oluştu:\n{str(e)}")

    def action_export_bulk_dialog(self):
        """Kullanıcıya QR, Barkod veya Kart formatında toplu dışa aktarma penceresi sunar."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, surname, tckn FROM workers")
            rows = cursor.fetchall()
        
        if not rows:
            messagebox.showwarning("Uyarı", "Sistemde kayıtlı veri bulunamadı.")
            return

        export_dialog = tk.Toplevel(self.root)
        export_dialog.title("Toplu Görsel Dışa Aktarma")
        export_dialog.geometry("450x330")
        export_dialog.resizable(False, False)
        export_dialog.transient(self.root)
        export_dialog.grab_set()

        ttk.Label(export_dialog, text="📁 Toplu Resim Dışa Aktarma", font=("Segoe UI", 12, "bold")).pack(pady=(15, 10))

        content_frame = ttk.Frame(export_dialog, padding=15)
        content_frame.pack(fill="x")

        ttk.Label(content_frame, text=f"Sistemdeki toplam {len(rows)} kayıt için çıktı türünü seçin:", style="Normal.TLabel").pack(anchor="w", pady=(0, 10))

        var_bulk_type = tk.StringVar(value="barcode_only")

        rb1 = ttk.Radiobutton(content_frame, text="📊 Yalnızca Çizgi Barkodlar (.png)", value="barcode_only", variable=var_bulk_type)
        rb1.pack(anchor="w", pady=3)

        rb2 = ttk.Radiobutton(content_frame, text="📱 Yalnızca QR Kodlar (.png)", value="qr_only", variable=var_bulk_type)
        rb2.pack(anchor="w", pady=3)

        rb_qr_text = ttk.Radiobutton(content_frame, text="👤 QR Kod + İsim/TC Alt Alta (.png)", value="qr_with_text", variable=var_bulk_type)
        rb_qr_text.pack(anchor="w", pady=3)

        rb3 = ttk.Radiobutton(content_frame, text="📇 Hazır Baskı Kartları / Etiketleri (.png)", value="cards", variable=var_bulk_type)
        rb3.pack(anchor="w", pady=3)

        def do_export():
            target_dir = filedialog.askdirectory(title="Kayıt Klasörünü Seçin", parent=export_dialog)
            if not target_dir:
                return
                
            export_type = var_bulk_type.get()
            export_dialog.destroy()
            
            code_mode = self.var_code_mode.get()
            barcode_type = self.get_clean_barcode_type()
            show_text = self.var_show_barcode_text.get()
            company = self.var_company_title.get().strip()

            exported = 0
            for name, surname, code_val in rows:
                clean_name = f"{name}_{surname}".strip().replace(" ", "_")
                if clean_name:
                    clean_name = f"{clean_name}_"
                    
                if export_type == "cards":
                    img = qr_generator.create_printable_badge(
                        name, surname, code_val,
                        code_mode=code_mode,
                        barcode_type=barcode_type,
                        show_barcode_text=show_text,
                        company_title=company
                    )
                    file_name = f"KART_{clean_name}{code_val}.png"
                elif export_type == "qr_with_text":
                    img = qr_generator.generate_qr_with_text(code_val, name, surname, show_text=show_text)
                    file_name = f"QR_ISIMLI_{clean_name}{code_val}.png"
                elif export_type == "qr_only":
                    img = qr_generator.generate_qr_image(code_val, box_size=12)
                    file_name = f"QR_{clean_name}{code_val}.png"
                else:
                    img = qr_generator.generate_barcode_image(code_val, barcode_type=barcode_type, show_text=show_text)
                    file_name = f"BARKOD_{clean_name}{code_val}.png"
                    
                save_path = os.path.join(target_dir, file_name)
                img.save(save_path)
                exported += 1
                
            messagebox.showinfo("Tamamlandı", f"{exported} adet görsel başarıyla klasöre kaydedildi:\n{target_dir}")
            self.set_status(f"{exported} görsel klasöre aktarıldı.")

        btn_box = ttk.Frame(export_dialog, padding=15)
        btn_box.pack(fill="x", side="bottom")

        ttk.Button(btn_box, text="Klasör Seç ve Aktar", style="Success.TButton", command=do_export).pack(side="right", padx=(5, 0))
        ttk.Button(btn_box, text="İptal", style="Action.TButton", command=export_dialog.destroy).pack(side="right", padx=(0, 5))


def main():
    root = tk.Tk()
    app = QRCodeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
