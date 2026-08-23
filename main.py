"""
İşçi TC Kimlik & Özel Kod / Barkod Oluşturma & Yazdırma Uygulaması
Ana Kullanıcı Arayüzü (GUI)
"""
import sys
import os
import json
import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

# Kendi modüllerimiz
import qr_generator
import printer_service


class QRCodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("İşçi TC Kimlik & Özel Kod / Barkod Uygulaması")
        self.root.geometry("1180x760")
        self.root.minsize(1020, 680)
        
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
        
        # Değişkenler
        self.var_code_mode = tk.StringVar(value="barcode")        # "barcode", "qr", "both"
        self.var_barcode_type = tk.StringVar(value="code128")     # "code128", "code39"
        self.var_show_barcode_text = tk.BooleanVar(value=True)    # Barkod altında kod yazısı
        self.var_strict_tckn = tk.BooleanVar(value=False)         # Sıkı 11 haneli TC kontrolü
        self.var_company_title = tk.StringVar(value="")           # Üst kurum/şirket başlığı
        
        # Ana Arayüz Bileşenleri
        self.build_ui()
        self.refresh_worker_list()
        self.update_printer_list()

    def configure_styles(self):
        """Arayüz renk ve yazı tipi stillerini yapılandırır."""
        bg_dark = "#0F172A"
        fg_white = "#F8FAFC"
        accent_blue = "#2563EB"
        
        self.root.configure(bg="#F1F5F9")
        
        self.style.configure("TFrame", background="#F1F5F9")
        self.style.configure("Card.TFrame", background="#FFFFFF", relief="flat", borderwidth=1)
        self.style.configure("Header.TFrame", background=bg_dark)
        
        self.style.configure("Header.TLabel", background=bg_dark, foreground=fg_white, font=("Segoe UI", 15, "bold"))
        self.style.configure("SubHeader.TLabel", background=bg_dark, foreground="#94A3B8", font=("Segoe UI", 9))
        self.style.configure("Title.TLabel", background="#FFFFFF", foreground="#0F172A", font=("Segoe UI", 11, "bold"))
        self.style.configure("Normal.TLabel", background="#FFFFFF", foreground="#334155", font=("Segoe UI", 9))
        self.style.configure("Sub.TLabel", background="#FFFFFF", foreground="#64748B", font=("Segoe UI", 8))
        
        self.style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"), background=accent_blue, foreground="white")
        self.style.map("Primary.TButton", background=[("active", "#1D4ED8")])
        
        self.style.configure("Success.TButton", font=("Segoe UI", 9, "bold"), background="#059669", foreground="white")
        self.style.map("Success.TButton", background=[("active", "#047857")])

        self.style.configure("Action.TButton", font=("Segoe UI", 9), background="#E2E8F0", foreground="#0F172A")
        self.style.map("Action.TButton", background=[("active", "#CBD5E1")])

        self.style.configure("Card.TRadiobutton", background="#FFFFFF", font=("Segoe UI", 9))
        self.style.configure("Card.TCheckbutton", background="#FFFFFF", font=("Segoe UI", 9))
        self.style.configure("Card.TLabelframe", background="#FFFFFF")
        self.style.configure("Card.TLabelframe.Label", background="#FFFFFF", font=("Segoe UI", 9, "bold"), foreground="#1E293B")

        self.style.configure("Treeview", font=("Segoe UI", 9), rowheight=26)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#E2E8F0", foreground="#0F172A")

    def init_db(self):
        """Veritabanı tablosunu oluşturur."""
        conn = sqlite3.connect(self.db_file)
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
        conn.close()

    def build_ui(self):
        """Tüm arayüz düzenini oluşturur."""
        # 1. Üst Header Bar
        header_frame = ttk.Frame(self.root, style="Header.TFrame", padding=(20, 12))
        header_frame.pack(fill="x", side="top")
        
        ttk.Label(header_frame, text="KOD / BARKOD & QR KOD OLUŞTURMA VE YAZDIRMA", style="Header.TLabel").pack(anchor="w")
        ttk.Label(header_frame, text="Belirlediğiniz Sayı, Harf, Seri Numarası veya TC Kimlik ile 1D Çizgi Barkod & 2D Karekod Üretin", style="SubHeader.TLabel").pack(anchor="w", pady=(2, 0))

        # 2. Ana İçerik Alanı
        main_container = ttk.Frame(self.root, padding=12)
        main_container.pack(fill="both", expand=True)
        
        main_container.columnconfigure(0, weight=5)
        main_container.columnconfigure(1, weight=6)
        main_container.rowconfigure(0, weight=1)

        # ---------------- SOL PANEL (Form & Kod Seçimi & Canlı Önizleme) ----------------
        left_card = ttk.Frame(main_container, style="Card.TFrame", padding=12)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        ttk.Label(left_card, text="Kod Bilgileri ve Barkod Ayarları", style="Title.TLabel").pack(anchor="w", pady=(0, 8))
        
        # Form Alanları
        form_frame = ttk.Frame(left_card, style="Card.TFrame")
        form_frame.pack(fill="x", pady=2)
        form_frame.columnconfigure(1, weight=1)
        
        # Kod Değeri / Sayı / Harf (ZORUNLU ALAN)
        ttk.Label(form_frame, text="Barkod / Kod Değeri:", font=("Segoe UI", 9, "bold"), background="#FFFFFF", foreground="#1E293B").grid(row=0, column=0, sticky="w", pady=3)
        self.entry_tckn = ttk.Entry(form_frame, font=("Segoe UI", 10, "bold"))
        self.entry_tckn.grid(row=0, column=1, sticky="ew", pady=3, padx=(8, 0))
        self.entry_tckn.bind("<KeyRelease>", self.on_code_input)

        # Adı (Opsiyonel)
        ttk.Label(form_frame, text="İsim / Başlık (Opsiyonel):", style="Normal.TLabel").grid(row=1, column=0, sticky="w", pady=3)
        self.entry_name = ttk.Entry(form_frame, font=("Segoe UI", 9))
        self.entry_name.grid(row=1, column=1, sticky="ew", pady=3, padx=(8, 0))
        self.entry_name.bind("<KeyRelease>", lambda e: self.auto_refresh_preview())
        
        # Soyadı (Opsiyonel)
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
        self.lbl_status.pack(anchor="w", pady=(4, 6))

        # Kod Türü ve Seçenekler Çerçevesi
        code_type_frame = ttk.LabelFrame(left_card, text=" Kod Formatı ve Türü ", style="Card.TLabelframe", padding=(8, 6))
        code_type_frame.pack(fill="x", pady=(0, 8))

        modes_box = ttk.Frame(code_type_frame, style="Card.TFrame")
        modes_box.pack(fill="x")

        rb_bc = ttk.Radiobutton(modes_box, text="📊 Çizgi Barkod (1D)", value="barcode", variable=self.var_code_mode, style="Card.TRadiobutton", command=self.on_mode_change)
        rb_bc.pack(side="left", padx=(0, 10))

        rb_qr = ttk.Radiobutton(modes_box, text="📱 QR Kod (2D)", value="qr", variable=self.var_code_mode, style="Card.TRadiobutton", command=self.on_mode_change)
        rb_qr.pack(side="left", padx=(0, 10))

        rb_both = ttk.Radiobutton(modes_box, text="🔄 QR + Barkod (Kombine)", value="both", variable=self.var_code_mode, style="Card.TRadiobutton", command=self.on_mode_change)
        rb_both.pack(side="left")

        # Barkod İnce Ayar Satırı
        bc_opt_box = ttk.Frame(code_type_frame, style="Card.TFrame")
        bc_opt_box.pack(fill="x", pady=(6, 0))

        ttk.Label(bc_opt_box, text="Standart:", style="Sub.TLabel").pack(side="left", padx=(0, 4))
        self.cb_bctype = ttk.Combobox(bc_opt_box, textvariable=self.var_barcode_type, values=["Code 128 (Tüm Sayı/Harf)", "Code 39"], state="readonly", width=18, font=("Segoe UI", 8))
        self.cb_bctype.current(0)
        self.cb_bctype.pack(side="left", padx=(0, 10))
        self.cb_bctype.bind("<<ComboboxSelected>>", lambda e: self.on_mode_change())

        chk_text = ttk.Checkbutton(bc_opt_box, text="Kod Metnini Göster", variable=self.var_show_barcode_text, style="Card.TCheckbutton", command=self.auto_refresh_preview)
        chk_text.pack(side="left", padx=(0, 10))

        chk_strict = ttk.Checkbutton(bc_opt_box, text="Sıkı TC Kontrolü", variable=self.var_strict_tckn, style="Card.TCheckbutton", command=self.on_strict_toggle)
        chk_strict.pack(side="left")

        # Butonlar
        btn_frame = ttk.Frame(left_card, style="Card.TFrame")
        btn_frame.pack(fill="x", pady=(2, 8))
        
        btn_generate = ttk.Button(btn_frame, text="✨ Barkod / Kod Oluştur", style="Primary.TButton", command=self.action_generate_code)
        btn_generate.pack(side="left", fill="x", expand=True, padx=(0, 4))
        
        btn_save_worker = ttk.Button(btn_frame, text="➕ Listeye Kaydet", style="Action.TButton", command=self.action_save_worker)
        btn_save_worker.pack(side="left", fill="x", expand=True, padx=4)

        btn_copy_tc = ttk.Button(btn_frame, text="📋 Kodu Kopyala", style="Action.TButton", command=self.action_copy_tc)
        btn_copy_tc.pack(side="left", fill="x", expand=True, padx=(4, 0))

        # Önizleme Kutu Alanı
        ttk.Label(left_card, text="Kart & Baskı Önizlemesi", style="Title.TLabel").pack(anchor="w", pady=(2, 4))
        
        preview_border = tk.Frame(left_card, bg="#CBD5E1", bd=1)
        preview_border.pack(fill="both", expand=True, pady=(0, 6))
        
        self.lbl_preview = tk.Label(preview_border, bg="#F8FAFC", text="Barkod / QR Kod Önizlemesi Burada Görünecektir")
        self.lbl_preview.pack(fill="both", expand=True)
        
        # Yazdırma ve Dışa Aktarma Butonları
        print_action_frame = ttk.Frame(left_card, style="Card.TFrame")
        print_action_frame.pack(fill="x", pady=(2, 0))
        
        btn_print = ttk.Button(print_action_frame, text="🖨️ Yazıcı Seç ve Yazdır", style="Success.TButton", command=self.action_print_current)
        btn_print.pack(side="left", fill="x", expand=True, padx=(0, 4))
        
        btn_export_png = ttk.Button(print_action_frame, text="💾 PNG Olarak Kaydet", style="Action.TButton", command=self.action_save_png)
        btn_export_png.pack(side="left", fill="x", expand=True, padx=(4, 0))

        # ---------------- SAĞ PANEL (Kayıtlı İşçiler & Toplu İşlemler) ----------------
        right_card = ttk.Frame(main_container, style="Card.TFrame", padding=12)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        
        right_top = ttk.Frame(right_card, style="Card.TFrame")
        right_top.pack(fill="x", pady=(0, 8))
        
        ttk.Label(right_top, text="Kayıtlı Kodlar & Personel Listesi", style="Title.TLabel").pack(side="left")
        
        search_frame = ttk.Frame(right_top, style="Card.TFrame")
        search_frame.pack(side="right")
        ttk.Label(search_frame, text="Ara:", style="Normal.TLabel").pack(side="left", padx=(0, 4))
        self.entry_search = ttk.Entry(search_frame, font=("Segoe UI", 9), width=18)
        self.entry_search.pack(side="left")
        self.entry_search.bind("<KeyRelease>", self.on_search)

        table_frame = ttk.Frame(right_card, style="Card.TFrame")
        table_frame.pack(fill="both", expand=True)
        
        columns = ("id", "name", "surname", "tckn", "created_at")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="extended")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="İsim / Başlık")
        self.tree.heading("surname", text="Soyisim / Detay")
        self.tree.heading("tckn", text="Barkod / Kod Değeri")
        self.tree.heading("created_at", text="Kayıt Tarihi")
        
        self.tree.column("id", width=35, anchor="center")
        self.tree.column("name", width=110)
        self.tree.column("surname", width=110)
        self.tree.column("tckn", width=130, anchor="center")
        self.tree.column("created_at", width=110, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Alt Buton Grubu
        bottom_btn_frame = ttk.Frame(right_card, style="Card.TFrame")
        bottom_btn_frame.pack(fill="x", pady=(8, 0))
        
        btn_print_selected = ttk.Button(bottom_btn_frame, text="🖨️ Seçilenleri Yazdır (A4 3'lü)", style="Success.TButton", command=self.action_print_selected)
        btn_print_selected.pack(side="left", padx=(0, 4))
        
        btn_import_excel = ttk.Button(bottom_btn_frame, text="📂 Excel/CSV'den Aktar", style="Action.TButton", command=self.action_import_excel)
        btn_import_excel.pack(side="left", padx=4)
        
        btn_export_bulk = ttk.Button(bottom_btn_frame, text="📁 Toplu Aktar...", style="Action.TButton", command=self.action_export_bulk_dialog)
        btn_export_bulk.pack(side="left", padx=4)
        
        btn_delete = ttk.Button(bottom_btn_frame, text="🗑️ Sil", style="Action.TButton", command=self.action_delete_worker)
        btn_delete.pack(side="right")

        # 3. En Alt Durum Çubuğu
        self.status_bar = ttk.Label(self.root, text="Sistem hazır.", font=("Segoe UI", 9), background="#E2E8F0", padding=(15, 4))
        self.status_bar.pack(fill="x", side="bottom")

    def get_clean_barcode_type(self) -> str:
        """Combobox değerinden clean barcode type döndürür."""
        val = self.var_barcode_type.get().lower()
        if "39" in val:
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

    def on_code_input(self, event):
        """Kod alanına yazıldıkça canlı denetler ve önizler."""
        val = self.entry_tckn.get().strip()
        strict = self.var_strict_tckn.get()
        
        if not val:
            self.lbl_status.config(text="Barkod veya QR koda dönüştürülecek sayı/harf değerini giriniz.", foreground="#64748B")
            return

        is_valid, msg = qr_generator.validate_code_value(val, strict_tckn=strict)
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
            is_valid, _ = qr_generator.validate_code_value(code_val, strict_tckn=strict)
            if is_valid:
                self.action_generate_code(silent=True)

    def action_generate_code(self, silent: bool = False):
        """Girilen bilgilere göre Barkod / QR / Kombine kart oluşturup önizler."""
        name = self.entry_name.get().strip()
        surname = self.entry_surname.get().strip()
        code_val = self.entry_tckn.get().strip()
        company = self.var_company_title.get().strip()
        strict = self.var_strict_tckn.get()
        
        is_valid, msg = qr_generator.validate_code_value(code_val, strict_tckn=strict)
        if not is_valid:
            if not silent:
                messagebox.showwarning("Geçersiz Kod Değeri", msg)
            return
            
        code_mode = self.var_code_mode.get()
        barcode_type = self.get_clean_barcode_type()
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
        box_w = self.lbl_preview.winfo_width() or 420
        box_h = self.lbl_preview.winfo_height() or 260
        
        img_copy = pil_image.copy()
        img_copy.thumbnail((box_w - 20, box_h - 20), Image.Resampling.LANCZOS)
        
        tk_img = ImageTk.PhotoImage(img_copy)
        self.lbl_preview.config(image=tk_img, text="")
        self.lbl_preview.image = tk_img

    def action_copy_tc(self):
        """Barkod / Kod değerini panoya kopyalar."""
        code_val = self.entry_tckn.get().strip()
        if not code_val:
            messagebox.showwarning("Uyarı", "Kopyalanacak kod değeri bulunamadı.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(code_val)
        self.set_status(f"Panoya kopyalandı: {code_val}")

    def action_save_worker(self):
        """Girişi yapılan kaydı veritabanına ekler."""
        name = self.entry_name.get().strip()
        surname = self.entry_surname.get().strip()
        code_val = self.entry_tckn.get().strip()
        strict = self.var_strict_tckn.get()
        
        is_valid, msg = qr_generator.validate_code_value(code_val, strict_tckn=strict)
        if not is_valid:
            messagebox.showwarning("Geçersiz Değer", msg)
            return
            
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO workers (name, surname, tckn, created_at) VALUES (?, ?, ?, ?)",
                           (name, surname, code_val, created_at))
            conn.commit()
            label_disp = f"'{name} {surname}' ({code_val})" if (name or surname) else f"'{code_val}'"
            messagebox.showinfo("Başarılı", f"Kayıt {label_disp} başarıyla kaydedildi.")
            self.refresh_worker_list()
        except sqlite3.IntegrityError:
            messagebox.showerror("Hata", "Bu kod değeri sistemde zaten kayıtlı!")
        finally:
            conn.close()

    def refresh_worker_list(self, query: str = ""):
        """Veritabanındaki listeyi tabloya doldurur."""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        if query:
            q = f"%{query}%"
            cursor.execute("SELECT id, name, surname, tckn, created_at FROM workers WHERE name LIKE ? OR surname LIKE ? OR tckn LIKE ?", (q, q, q))
        else:
            cursor.execute("SELECT id, name, surname, tckn, created_at FROM workers ORDER BY id DESC")
            
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            self.tree.insert("", "end", values=row)

    def on_search(self, event):
        """Arama kutusuna yazıldıkça tabloyu filtreler."""
        q = self.entry_search.get().strip()
        self.refresh_worker_list(q)

    def on_tree_select(self, event):
        """Tablodan bir kayıt seçildiğinde forma doldurur ve barkod oluşturur."""
        selected = self.tree.selection()
        if not selected:
            return
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
            
        item_values = self.tree.item(selected[0], "values")
        worker_id, name, surname, code_val, _ = item_values
        
        disp_title = f"'{name} {surname}' (Kod: {code_val})" if (name or surname) else f"'{code_val}'"
        confirm = messagebox.askyesno("Silme Onayı", f"{disp_title} kaydını silmek istediğinize emin misiniz?")
        if confirm:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM workers WHERE id = ?", (worker_id,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Silindi", "Kayıt başarıyla silindi.")
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
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
            
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
            conn.close()
            
            msg = f"✓ Toplam Tespit Edilen: {len(workers_found)} kayıt\n✓ İçe Aktarılan: {imported_count} yeni kayıt\n⚠ Atlanan (Sistemde Zaten Kayıtlı): {skipped_count}"
            messagebox.showinfo("İçe Aktarma Başarılı", msg)
            self.refresh_worker_list()
            self.set_status(f"Excel'den {imported_count} kayıt eklendi.")
            
        except Exception as e:
            messagebox.showerror("İçe Aktarma Hatası", f"Dosya işlenirken hata oluştu:\n{str(e)}")

    def action_export_bulk_dialog(self):
        """Kullanıcıya QR, Barkod veya Kart formatında toplu dışa aktarma penceresi sunar."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name, surname, tckn FROM workers")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            messagebox.showwarning("Uyarı", "Sistemde kayıtlı veri bulunamadı.")
            return

        export_dialog = tk.Toplevel(self.root)
        export_dialog.title("Toplu Görsel Dışa Aktarma")
        export_dialog.geometry("450x290")
        export_dialog.resizable(False, False)
        export_dialog.transient(self.root)
        export_dialog.grab_set()

        ttk.Label(export_dialog, text="📁 Toplu Dışa Aktarma Seçenekleri", font=("Segoe UI", 12, "bold")).pack(pady=(15, 10))

        content_frame = ttk.Frame(export_dialog, padding=15)
        content_frame.pack(fill="x")

        ttk.Label(content_frame, text=f"Sistemdeki toplam {len(rows)} kayıt için çıktı türünü seçin:", style="Normal.TLabel").pack(anchor="w", pady=(0, 10))

        var_bulk_type = tk.StringVar(value="barcode_only")

        rb1 = ttk.Radiobutton(content_frame, text="📊 Yalnızca Çizgi Barkodlar (.png)", value="barcode_only", variable=var_bulk_type)
        rb1.pack(anchor="w", pady=3)

        rb2 = ttk.Radiobutton(content_frame, text="📱 Yalnızca QR Kodlar (.png)", value="qr_only", variable=var_bulk_type)
        rb2.pack(anchor="w", pady=3)

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
