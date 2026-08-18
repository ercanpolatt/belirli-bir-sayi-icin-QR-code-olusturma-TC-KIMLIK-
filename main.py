"""
İşçi TC Kimlik QR Kod Oluşturma ve Yazdırma Uygulaması
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
        self.root.title("İşçi TC Kimlik QR Kod Oluşturma & Yazdırma Programı")
        self.root.geometry("1100x720")
        self.root.minsize(950, 650)
        
        # Tema ve Stil Ayarları
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure_styles()
        
        # Veritabanı Kurulumu
        self.db_file = os.path.join(os.path.dirname(__file__), "workers.db")
        self.init_db()
        
        # Aktif Önizleme Görseli
        self.current_badge_image = None
        self.current_qr_image = None
        self.current_worker_data = None
        
        # Ana Arayüz Bilişenleri
        self.build_ui()
        self.refresh_worker_list()
        self.update_printer_list()

    def configure_styles(self):
        """Arayüz renk ve yazı tipi stillerini yapılandırır."""
        bg_dark = "#0F172A"
        bg_card = "#1E293B"
        fg_white = "#F8FAFC"
        accent_blue = "#2563EB"
        
        self.root.configure(bg="#F1F5F9")
        
        self.style.configure("TFrame", background="#F1F5F9")
        self.style.configure("Card.TFrame", background="#FFFFFF", relief="flat", borderwidth=1)
        self.style.configure("Header.TFrame", background=bg_dark)
        
        self.style.configure("Header.TLabel", background=bg_dark, foreground=fg_white, font=("Segoe UI", 16, "bold"))
        self.style.configure("SubHeader.TLabel", background=bg_dark, foreground="#94A3B8", font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", background="#FFFFFF", foreground="#0F172A", font=("Segoe UI", 12, "bold"))
        self.style.configure("Normal.TLabel", background="#FFFFFF", foreground="#334155", font=("Segoe UI", 10))
        
        self.style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), background=accent_blue, foreground="white")
        self.style.map("Primary.TButton", background=[("active", "#1D4ED8")])
        
        self.style.configure("Success.TButton", font=("Segoe UI", 10, "bold"), background="#059669", foreground="white")
        self.style.map("Success.TButton", background=[("active", "#047857")])

        self.style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#E2E8F0", foreground="#0F172A")

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
        header_frame = ttk.Frame(self.root, style="Header.TFrame", padding=(20, 15))
        header_frame.pack(fill="x", side="top")
        
        ttk.Label(header_frame, text="İŞÇİ TC KİMLİK QR KOD & YAZDIRMA UYGULAMASI", style="Header.TLabel").pack(anchor="w")
        ttk.Label(header_frame, text="İşçi TC Kimlik numarasına göre QR kod üretin, önizleyin ve yazıcıdan çıktı alın.", style="SubHeader.TLabel").pack(anchor="w", pady=(2, 0))

        # 2. Ana İçerik Alanı (Sol Paneli & Sağ Paneli)
        main_container = ttk.Frame(self.root, padding=15)
        main_container.pack(fill="both", expand=True)
        
        # Grid Ağırlıkları
        main_container.columnconfigure(0, weight=4)  # Sol panel
        main_container.columnconfigure(1, weight=6)  # Sağ panel
        main_container.rowconfigure(0, weight=1)

        # ---------------- SOL PANEL (Form & Canlı Önizleme) ----------------
        left_card = ttk.Frame(main_container, style="Card.TFrame", padding=15)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ttk.Label(left_card, text="İşçi Bilgileri ve QR Oluşturma", style="Title.TLabel").pack(anchor="w", pady=(0, 10))
        
        # Form Alanları
        form_frame = ttk.Frame(left_card, style="Card.TFrame")
        form_frame.pack(fill="x", pady=5)
        form_frame.columnconfigure(1, weight=1)
        
        # Adı
        ttk.Label(form_frame, text="İşçi Adı:", style="Normal.TLabel").grid(row=0, column=0, sticky="w", pady=4)
        self.entry_name = ttk.Entry(form_frame, font=("Segoe UI", 10))
        self.entry_name.grid(row=0, column=1, sticky="ew", pady=4, padx=(10, 0))
        
        # Soyadı
        ttk.Label(form_frame, text="İşçi Soyadı:", style="Normal.TLabel").grid(row=1, column=0, sticky="w", pady=4)
        self.entry_surname = ttk.Entry(form_frame, font=("Segoe UI", 10))
        self.entry_surname.grid(row=1, column=1, sticky="ew", pady=4, padx=(10, 0))
        
        # TC Kimlik No
        ttk.Label(form_frame, text="TC Kimlik No (11 Hane):", style="Normal.TLabel").grid(row=2, column=0, sticky="w", pady=4)
        self.entry_tckn = ttk.Entry(form_frame, font=("Segoe UI", 11, "bold"))
        self.entry_tckn.grid(row=2, column=1, sticky="ew", pady=4, padx=(10, 0))
        
        # Canlı Tuşlama Takibi (Sadece rakam ve max 11 hane)
        self.entry_tckn.bind("<KeyRelease>", self.on_tckn_input)
        
        # Butonlar
        btn_frame = ttk.Frame(left_card, style="Card.TFrame")
        btn_frame.pack(fill="x", pady=12)
        
        btn_generate = ttk.Button(btn_frame, text="QR Kod Oluştur", style="Primary.TButton", command=self.action_generate_qr)
        btn_generate.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        btn_save_worker = ttk.Button(btn_frame, text="Listeye Kaydet", command=self.action_save_worker)
        btn_save_worker.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # Doğrulama Mesaj Alanı
        self.lbl_status = ttk.Label(left_card, text="Lütfen 11 haneli TC Kimlik numarasını giriniz.", font=("Segoe UI", 9), foreground="#64748B", background="#FFFFFF")
        self.lbl_status.pack(anchor="w", pady=(0, 10))

        # Önizleme Kutu Alanı
        ttk.Label(left_card, text="Yazdırma Önizlemesi", style="Title.TLabel").pack(anchor="w", pady=(5, 5))
        
        preview_border = tk.Frame(left_card, bg="#CBD5E1", bd=1)
        preview_border.pack(fill="both", expand=True, pady=5)
        
        self.lbl_preview = tk.Label(preview_border, bg="#F8FAFC", text="QR Kod Görseli Burada Görünecek")
        self.lbl_preview.pack(fill="both", expand=True)
        
        # Yazdırma ve Dışa Aktarma Butonları
        print_action_frame = ttk.Frame(left_card, style="Card.TFrame")
        print_action_frame.pack(fill="x", pady=(10, 0))
        
        btn_print = ttk.Button(print_action_frame, text="🖨️ Yazıcı Seç ve Yazdır", style="Success.TButton", command=self.action_print_current)
        btn_print.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        btn_export_png = ttk.Button(print_action_frame, text="💾 PNG Olarak Kaydet", command=self.action_save_png)
        btn_export_png.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # ---------------- SAĞ PANEL (Kayıtlı İşçi Listesi & Toplu İşlemler) ----------------
        right_card = ttk.Frame(main_container, style="Card.TFrame", padding=15)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Üst Arama ve Başlık
        right_top = ttk.Frame(right_card, style="Card.TFrame")
        right_top.pack(fill="x", pady=(0, 10))
        
        ttk.Label(right_top, text="Kayıtlı İşçiler & QR Listesi", style="Title.TLabel").pack(side="left")
        
        # Arama Kutusu
        search_frame = ttk.Frame(right_top, style="Card.TFrame")
        search_frame.pack(side="right")
        ttk.Label(search_frame, text="Ara:", style="Normal.TLabel").pack(side="left", padx=(0, 5))
        self.entry_search = ttk.Entry(search_frame, font=("Segoe UI", 9))
        self.entry_search.pack(side="left")
        self.entry_search.bind("<KeyRelease>", self.on_search)

        # Tablo (Treeview)
        table_frame = ttk.Frame(right_card, style="Card.TFrame")
        table_frame.pack(fill="both", expand=True)
        
        columns = ("id", "name", "surname", "tckn", "created_at")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="extended")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Adı")
        self.tree.heading("surname", text="Soyadı")
        self.tree.heading("tckn", text="TC Kimlik No")
        self.tree.heading("created_at", text="Kayıt Tarihi")
        
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("name", width=120)
        self.tree.column("surname", width=120)
        self.tree.column("tckn", width=130, anchor="center")
        self.tree.column("created_at", width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Alt Buton Grubu (Toplu işlemler & Silme)
        bottom_btn_frame = ttk.Frame(right_card, style="Card.TFrame")
        bottom_btn_frame.pack(fill="x", pady=(10, 0))
        
        btn_print_selected = ttk.Button(bottom_btn_frame, text="🖨️ Seçilenleri Yazdır (3'lü Izgara)", command=self.action_print_selected)
        btn_print_selected.pack(side="left", padx=(0, 5))
        
        btn_import_excel = ttk.Button(bottom_btn_frame, text="📂 Excel/CSV'den Aktar", command=self.action_import_excel)
        btn_import_excel.pack(side="left", padx=5)
        
        btn_export_all = ttk.Button(bottom_btn_frame, text="📁 Tüm QR'ları Klasöre Aktar", command=self.action_export_all_qr)
        btn_export_all.pack(side="left", padx=5)
        
        btn_delete = ttk.Button(bottom_btn_frame, text="🗑️ Sil", command=self.action_delete_worker)
        btn_delete.pack(side="right")

        # 3. En Alt Durum Çubuğu (Status Bar)
        self.status_bar = ttk.Label(self.root, text="Sistem hazır.", font=("Segoe UI", 9), background="#E2E8F0", padding=(15, 5))
        self.status_bar.pack(fill="x", side="bottom")

    def update_printer_list(self):
        """Varsayılan yazıcı bilgisini durum çubuğunda gösterir."""
        default_p = printer_service.get_default_printer()
        if default_p:
            self.set_status(f"Varsayılan Yazıcı: {default_p}")
        else:
            self.set_status("Sistemde varsayılan yazıcı bulunamadı.")

    def set_status(self, msg: str):
        """Durum çubuğunu günceller."""
        self.status_bar.config(text=msg)

    def on_tckn_input(self, event):
        """TCKN alanına girilen değeri canlı denetler."""
        val = self.entry_tckn.get().strip()
        # Sadece rakamları tut
        clean_val = "".join([c for c in val if c.isdigit()])[:11]
        if val != clean_val:
            self.entry_tckn.delete(0, tk.END)
            self.entry_tckn.insert(0, clean_val)
            
        if len(clean_val) == 11:
            is_valid, msg = qr_generator.validate_tckn(clean_val)
            if is_valid:
                self.lbl_status.config(text="✓ " + msg, foreground="#059669")
            else:
                self.lbl_status.config(text="⚠ " + msg, foreground="#DC2626")
        else:
            self.lbl_status.config(text=f"TC Kimlik No ({len(clean_val)}/11 hane)", foreground="#64748B")

    def action_generate_qr(self):
        """Girilen bilgilere göre QR kod ve yaka kartı oluşturup önizler."""
        name = self.entry_name.get().strip()
        surname = self.entry_surname.get().strip()
        tckn = self.entry_tckn.get().strip()
        
        is_valid, msg = qr_generator.validate_tckn(tckn)
        if not is_valid:
            messagebox.showwarning("Geçersiz TC Kimlik No", msg)
            return
            
        # Kart Görseli ve Yalnızca QR Görseli Üret
        self.current_badge_image = qr_generator.create_printable_badge(name, surname, tckn)
        self.current_qr_image = qr_generator.generate_qr_image(tckn)
        self.current_worker_data = {"name": name, "surname": surname, "tckn": tckn}
        
        # Önizlemeyi Güncelle
        self.display_preview(self.current_badge_image)
        self.set_status(f"QR Kod oluşturuldu: TC={tckn}")

    def display_preview(self, pil_image: Image.Image):
        """PIL Görselini ekrandaki önizleme kutusuna boyutlandırıp yerleştirir."""
        box_w = self.lbl_preview.winfo_width() or 400
        box_h = self.lbl_preview.winfo_height() or 250
        
        # Orantılı Boyutlandırma
        img_copy = pil_image.copy()
        img_copy.thumbnail((box_w - 20, box_h - 20), Image.Resampling.LANCZOS)
        
        tk_img = ImageTk.PhotoImage(img_copy)
        self.lbl_preview.config(image=tk_img, text="")
        self.lbl_preview.image = tk_img  # Garbage collection engelleyici

    def action_save_worker(self):
        """Girişi yapılan işçiyi veritabanına kaydeder."""
        name = self.entry_name.get().strip()
        surname = self.entry_surname.get().strip()
        tckn = self.entry_tckn.get().strip()
        
        is_valid, msg = qr_generator.validate_tckn(tckn)
        if not is_valid:
            messagebox.showwarning("Geçersiz TC Kimlik No", msg)
            return
            
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO workers (name, surname, tckn, created_at) VALUES (?, ?, ?, ?)",
                           (name, surname, tckn, created_at))
            conn.commit()
            messagebox.showinfo("Başarılı", f"İşçi '{name} {surname}' başarıyla kaydedildi.")
            self.refresh_worker_list()
        except sqlite3.IntegrityError:
            messagebox.showerror("Hata", "Bu TC Kimlik numarası zaten sistemde kayıtlı!")
        finally:
            conn.close()

    def refresh_worker_list(self, query: str = ""):
        """Veritabanındaki işçi listesini tabloya doldurur."""
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
        """Tablodan bir işçi seçildiğinde bilgilerini forma doldurur ve QR oluşturur."""
        selected = self.tree.selection()
        if not selected:
            return
        item_values = self.tree.item(selected[0], "values")
        if item_values:
            _, name, surname, tckn, _ = item_values
            
            self.entry_name.delete(0, tk.END)
            self.entry_name.insert(0, name)
            
            self.entry_surname.delete(0, tk.END)
            self.entry_surname.insert(0, surname)
            
            self.entry_tckn.delete(0, tk.END)
            self.entry_tckn.insert(0, tckn)
            
            self.action_generate_qr()

    def action_print_current(self):
        """Şu an önizlenen QR/Kartı yazıcı seçimi penceresi açarak yazdırır."""
        if self.current_badge_image is None:
            # Otomatik oluşturmayı dene
            tckn = self.entry_tckn.get().strip()
            if tckn:
                self.action_generate_qr()
            else:
                messagebox.showwarning("Uyarı", "Yazdırılacak bir QR Kod henüz oluşturulmadı!")
                return
                
        if self.current_badge_image is None:
            return

        # Yazıcı Seçim Penceresi
        self.open_printer_select_dialog(self.current_badge_image)

    def action_print_selected(self):
        """Tabloda seçili işçilerin QR kartlarını 3'lü dizilimde A4 sayfasına yerleştirip yazdırır."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen önce tablodan yazdırılacak en az 1 işçi seçiniz.\n(Birden fazla seçim için Ctrl veya Shift tuşunu kullanabilirsiniz).")
            return
            
        workers = []
        for item in selected:
            item_values = self.tree.item(item, "values")
            if item_values:
                _, name, surname, tckn, _ = item_values
                workers.append((name, surname, str(tckn)))
                
        if len(workers) == 1:
            name, surname, tckn = workers[0]
            badge_img = qr_generator.create_printable_badge(name, surname, tckn)
            self.display_preview(badge_img)
            self.open_printer_select_dialog(badge_img)
        else:
            # 3'lü dizilimde A4 sayfaları oluştur
            pages = qr_generator.create_grid_printable_pages(workers, items_per_row=3)
            if pages:
                self.display_preview(pages[0])
                self.open_printer_select_dialog(pages)

    def open_printer_select_dialog(self, print_target):
        """Kullanıcının bilgisayarındaki yazıcıları listeleyen pencere açar (Tek görsel veya çoklu sayfa)."""
        printers = printer_service.get_installed_printers()
        default_p = printer_service.get_default_printer()
        
        if not printers:
            messagebox.showerror("Yazıcı Bulunamadı", "Sisteminizde tanımlı hiçbir yazıcı bulunamadı!")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Yazıcı Seçimi ve Çıktı Alma")
        dialog.geometry("450, 260")
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
        page_info_text = f"Toplam {len(print_target)} sayfa 3'lü dizilimde yazdırılacaktır." if is_multi else "Görsel yazıcı sayfasına sığdırılacaktır."
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
                success, msg = printer_service.print_images_to_printer(print_target, selected_printer)
            else:
                success, msg = printer_service.print_image_to_printer(print_target, selected_printer)
                
            if success:
                messagebox.showinfo("Başarılı", f"Yazdırma işlemi tamamlandı:\n{msg}")
                self.set_status(f"Yazdırıldı: {selected_printer}")
            else:
                messagebox.showerror("Yazdırma Hatası", msg)
                self.set_status("Yazdırma sırasında hata oluştu.")

        btn_box = ttk.Frame(dialog, padding=15)
        btn_box.pack(fill="x", side="bottom")
        
        ttk.Button(btn_box, text="Yazdır", style="Success.TButton", command=start_printing).pack(side="right", padx=(5, 0))
        ttk.Button(btn_box, text="İptal", command=dialog.destroy).pack(side="right", padx=(0, 5))

    def action_save_png(self):
        """Oluşturulan QR/Kart görselini PNG dosyası olarak kaydeder."""
        if self.current_badge_image is None:
            messagebox.showwarning("Uyarı", "Kaydedilecek bir QR Kod oluşturulmadı!")
            return
            
        tckn = self.current_worker_data.get("tckn", "qr_code")
        name = self.current_worker_data.get("name", "isci")
        
        default_filename = f"QR_{name}_{tckn}.png"
        filepath = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("PNG Görseli", "*.png"), ("Tüm Dosyalar", "*.*")],
                                                initialfile=default_filename)
        if filepath:
            self.current_badge_image.save(filepath)
            messagebox.showinfo("Başarılı", f"Görsel başarıyla kaydedildi:\n{filepath}")

    def action_delete_worker(self):
        """Seçili işçiyi veritabanından siler."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Silinecek işçiyi tablodan seçiniz.")
            return
            
        item_values = self.tree.item(selected[0], "values")
        worker_id, name, surname, tckn, _ = item_values
        
        confirm = messagebox.askyesno("Silme Onayı", f"'{name} {surname}' (TC: {tckn}) isimli işçiyi silmek istediğinize emin misiniz?")
        if confirm:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM workers WHERE id = ?", (worker_id,))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Silindi", "İşçi kaydı başarıyla silindi.")
            self.refresh_worker_list()

    def action_import_excel(self):
        """Excel veya CSV dosyasından esnek kolon eşleme ile toplu işçi aktarır."""
        filepath = filedialog.askopenfilename(filetypes=[("Excel / CSV Dosyaları", "*.xlsx *.csv"), ("Tüm Dosyalar", "*.*")])
        if not filepath:
            return
            
        try:
            imported_count = 0
            skipped_count = 0
            
            rows = []
            if filepath.endswith(".csv"):
                import csv
                with open(filepath, mode="r", encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    rows = [dict(r) for r in reader]
            else:
                import openpyxl
                wb = openpyxl.load_workbook(filepath, data_only=True)
                sheet = wb.active
                headers = [str(cell.value).strip() if cell.value is not None else "" for cell in sheet[1]]
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    row_dict = {}
                    for idx, val in enumerate(row):
                        if idx < len(headers) and headers[idx]:
                            row_dict[headers[idx]] = str(val).strip() if val is not None else ""
                    if any(row_dict.values()):
                        rows.append(row_dict)
                    
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            def norm(k):
                return str(k).strip().lower().replace("ı", "i").replace("ş", "s").replace("ğ", "g").replace("ü", "u").replace("ö", "o").replace("ç", "c")

            for r in rows:
                name, surname, tckn = "", "", ""
                
                for k, v in r.items():
                    nk = norm(k)
                    if nk in ["ad", "adi", "isim", "isım", "name", "first_name", "first name"]:
                        name = str(v).strip()
                    elif nk in ["soyad", "soyadi", "soyisim", "soyısım", "surname", "last_name", "last name"]:
                        surname = str(v).strip()
                    elif nk in ["tc", "tckn", "tcno", "tc_no", "tc kimlik", "tc_kimlik", "tc kimlik no", "tc_kimlik_no"]:
                        tckn = str(v).strip().split(".")[0]  # Excel sayılarından .0 temizleme

                is_valid, _ = qr_generator.validate_tckn(tckn)
                if is_valid:
                    try:
                        cursor.execute("INSERT INTO workers (name, surname, tckn, created_at) VALUES (?, ?, ?, ?)",
                                       (name, surname, tckn, created_at))
                        imported_count += 1
                    except sqlite3.IntegrityError:
                        skipped_count += 1
                else:
                    skipped_count += 1
                    
            conn.commit()
            conn.close()
            
            messagebox.showinfo("İçe Aktarma Tamamlandı", f"İçe Aktarılan: {imported_count} işçi\nAtlanan (Geçersiz/Mevcut TC): {skipped_count}")
            self.refresh_worker_list()
            
        except Exception as e:
            messagebox.showerror("İçe Aktarma Hatası", f"Dosya okunurken hata oluştu:\n{str(e)}")

    def action_export_all_qr(self):
        """Tüm kayıtlı işçilerin QR kodlarını bir klasöre PNG olarak kaydeder."""
        output_dir = filedialog.askdirectory(title="QR Kodların Kaydedileceği Klasörü Seçin")
        if not output_dir:
            return
            
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name, surname, tckn FROM workers")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            messagebox.showwarning("Uyarı", "Sistemde kayıtlı işçi bulunamadı.")
            return
            
        exported = 0
        for name, surname, tckn in rows:
            badge_img = qr_generator.create_printable_badge(name, surname, tckn)
            file_name = f"QR_{name}_{surname}_{tckn}.png".replace(" ", "_")
            save_path = os.path.join(output_dir, file_name)
            badge_img.save(save_path)
            exported += 1
            
        messagebox.showinfo("Tamamlandı", f"{exported} adet QR kartı başarıyla klasöre kaydedildi:\n{output_dir}")


def main():
    root = tk.Tk()
    app = QRCodeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
