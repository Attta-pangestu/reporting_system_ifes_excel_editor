#!/usr/bin/env python3
"""
GUI Application untuk Analisis FFB Scanner Multi-Estate
Menganalisis semua estate sekaligus dengan laporan PDF berbasis tabel sederhana
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import pandas as pd
import os
from datetime import datetime, date
import threading
from firebird_connector import FirebirdConnector
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import json

class MultiEstateFFBAnalysisGUI:
    CONFIG_FILE = "config.json"
    
    def __init__(self, root):
        self.root = root
        self.root.title("LAPORAN KINERJA KERANI, MANDOR, DAN ASISTEN - Multi-Estate")
        self.root.geometry("1100x800") # Lebarkan window untuk path
        self.root.configure(bg='#f0f0f0')
        
        self.ESTATES = self.load_config()
        
        self.setup_ui()
    
    def load_config(self):
        """Memuat konfigurasi dari file JSON."""
        default_estates = {
            "PGE 1A": r"C:\Users\nbgmf\Downloads\PTRJ_P1A\PTRJ_P1A.FDB",
            "PGE 1B": r"C:\Users\nbgmf\Downloads\PTRJ_P1B\PTRJ_P1B.FDB", 
            "PGE 2A": r"C:\Users\nbgmf\Downloads\IFESS_PGE_2A_19-06-2025",
            "PGE 2B": r"C:\Users\nbgmf\Downloads\IFESS_2B_19-06-2025\PTRJ_P2B.FDB",
            "IJL": r"C:\Users\nbgmf\Downloads\IFESS_IJL_19-06-2025\PTRJ_IJL_IMPIANJAYALESTARI.FDB",
            "DME": r"C:\Users\nbgmf\Downloads\IFESS_DME_19-06-2025\PTRJ_DME.FDB",
            "Are B2": r"C:\Users\nbgmf\Downloads\IFESS_ARE_B2_19-06-2025\PTRJ_AB2.FDB",
            "Are B1": r"C:\Users\nbgmf\Downloads\IFESS_ARE_B1_19-06-2025\PTRJ_AB1.FDB",
            "Are A": r"C:\Users\nbgmf\Downloads\IFESS_ARE_A_19-06-2025\PTRJ_ARA.FDB",
            "Are C": r"C:\Users\nbgmf\Downloads\IFESS_ARE_C_19-06-2025\PTRJ_ARC.FDB"
        }
        
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                messagebox.showerror("Error Konfigurasi", f"Gagal memuat {self.CONFIG_FILE}: {e}\nMenggunakan konfigurasi default.")
                return default_estates
        else:
            # Jika file tidak ada, buat dengan nilai default
            self.save_config(default_estates)
            return default_estates

    def save_config(self, data_to_save=None):
        """Menyimpan konfigurasi ke file JSON."""
        try:
            # Jika tidak ada data yang diberikan, ambil dari Treeview
            if data_to_save is None:
                current_config = {}
                for item_id in self.estate_tree.get_children():
                    values = self.estate_tree.item(item_id, 'values')
                    estate_name = values[0]
                    db_path = values[1]
                    current_config[estate_name] = db_path
                data_to_save = current_config

            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(data_to_save, f, indent=4)
            
            if data_to_save: # Hanya tampilkan pesan jika ada data untuk disimpan
                 self.log_message(f"Konfigurasi berhasil disimpan ke {self.CONFIG_FILE}")
        except IOError as e:
            messagebox.showerror("Error Konfigurasi", f"Gagal menyimpan {self.CONFIG_FILE}: {e}")

    def setup_ui(self):
        """Setup user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="LAPORAN KINERJA KERANI, MANDOR, DAN ASISTEN - Multi-Estate", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Estate selection
        estate_frame = ttk.LabelFrame(main_frame, text="Konfigurasi Database Estate", padding="10")
        estate_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Estate Treeview
        tree_frame = ttk.Frame(estate_frame)
        tree_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        columns = ('estate', 'path')
        self.estate_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=6)
        
        self.estate_tree.heading('estate', text='Estate')
        self.estate_tree.heading('path', text='Path Database')
        self.estate_tree.column('estate', width=150, anchor=tk.W)
        self.estate_tree.column('path', width=500, anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.estate_tree.yview)
        self.estate_tree.configure(yscrollcommand=scrollbar.set)
        
        self.estate_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate estate tree
        self.populate_estate_tree()
        
        # Selection buttons
        btn_frame = ttk.Frame(estate_frame)
        btn_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Button(btn_frame, text="Pilih Semua", command=self.select_all_estates).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Hapus Pilihan", command=self.clear_estate_selection).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Ubah Path...", command=self.change_db_path).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Simpan Konfigurasi", command=lambda: self.save_config()).pack(side=tk.LEFT, padx=5)
        
        # Date range
        date_frame = ttk.LabelFrame(main_frame, text="Rentang Tanggal", padding="10")
        date_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(date_frame, text="Tanggal Mulai:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.start_date = DateEntry(date_frame, width=20, background='darkblue', foreground='white')
        self.start_date.grid(row=0, column=1, padx=(10, 20), pady=5)
        
        ttk.Label(date_frame, text="Tanggal Akhir:").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.end_date = DateEntry(date_frame, width=20, background='darkblue', foreground='white')
        self.end_date.grid(row=0, column=3, padx=(10, 0), pady=5)
        
        # Set default dates
        self.start_date.set_date(date(2025, 5, 1))
        self.end_date.set_date(date(2025, 5, 31))
        
        # Progress
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.progress_var = tk.StringVar(value="Siap untuk menganalisis")
        ttk.Label(progress_frame, textvariable=self.progress_var).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Results
        results_frame = ttk.LabelFrame(main_frame, text="Log Analisis", padding="10")
        results_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        text_frame = ttk.Frame(results_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.results_text = tk.Text(text_frame, height=10, width=80)
        results_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Mulai Analisis Kinerja Multi-Estate", 
                  command=self.start_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Hapus Log", command=self.clear_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Buka Folder Output", command=self.open_output_folder).pack(side=tk.LEFT, padx=5)
        
        # Configure weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
    
    def populate_estate_tree(self):
        """Mengisi Treeview dengan data dari self.ESTATES."""
        # Hapus data lama
        for item in self.estate_tree.get_children():
            self.estate_tree.delete(item)
        
        # Tambahkan data baru
        for estate_name, db_path in self.ESTATES.items():
            self.estate_tree.insert('', tk.END, values=(estate_name, db_path))
    
    def change_db_path(self):
        """Membuka dialog untuk mengubah path database."""
        selected_item = self.estate_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Silakan pilih satu estate untuk diubah path-nya.")
            return
            
        # Langsung buka dialog untuk memilih file .FDB, tanpa opsi folder
        new_path = filedialog.askopenfilename(
            title="Pilih File Database (.FDB)", 
            filetypes=[("Firebird Database", "*.fdb")]
        )

        if new_path:
            self.estate_tree.item(selected_item, values=(self.estate_tree.item(selected_item, 'values')[0], new_path))
            self.log_message(f"Path untuk {self.estate_tree.item(selected_item, 'values')[0]} diubah. Jangan lupa simpan konfigurasi.")

    def select_all_estates(self):
        for item in self.estate_tree.get_children():
            self.estate_tree.selection_add(item)
    
    def clear_estate_selection(self):
        self.estate_tree.selection_remove(self.estate_tree.selection())
    
    def start_analysis(self):
        selected_indices = self.estate_tree.selection()
        if not selected_indices:
            messagebox.showerror("Error", "Silakan pilih minimal satu estate")
            return
        
        start_date = self.start_date.get_date()
        end_date = self.end_date.get_date()
        
        if start_date > end_date:
            messagebox.showerror("Error Tanggal", "Tanggal mulai tidak boleh lebih besar dari tanggal akhir.")
            return
        
        thread = threading.Thread(target=self.run_analysis)
        thread.daemon = True
        thread.start()
    
    def run_analysis(self):
        try:
            selected_items = self.estate_tree.selection()
            selected_estates = []
            for item_id in selected_items:
                values = self.estate_tree.item(item_id, 'values')
                estate_name = values[0]
                db_path = values[1]
                selected_estates.append((estate_name, db_path))
            
            if not selected_estates:
                messagebox.showerror("Error", "Silakan pilih minimal satu estate dari daftar.")
                return

            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()
            
            self.log_message("=== LAPORAN KINERJA KERANI, MANDOR, DAN ASISTEN MULTI-ESTATE ===")
            self.log_message(f"Periode: {start_date.strftime('%d %B %Y')} - {end_date.strftime('%d %B %Y')}")
            self.log_message(f"Jumlah Estate: {len(selected_estates)}")
            
            self.progress_bar['maximum'] = len(selected_estates)
            all_results = []
            
            for i, (estate_name, db_path) in enumerate(selected_estates):
                self.progress_var.set(f"Menganalisis {estate_name}")
                self.progress_bar['value'] = i
                self.root.update_idletasks()
                
                try:
                    estate_results = self.analyze_estate(estate_name, db_path, start_date, end_date)
                    if estate_results:
                        all_results.extend(estate_results)
                        self.log_message(f"{estate_name}: {len(estate_results)} divisi")
                    else:
                        self.log_message(f"{estate_name}: Tidak ada data")
                except Exception as e:
                    self.log_message(f"{estate_name}: {str(e)}")
            
            if all_results:
                self.log_message("Membuat laporan kinerja PDF...")
                pdf_path = self.create_pdf_report(all_results, start_date, end_date)
                self.log_message(f"Laporan kinerja PDF: {pdf_path}")
            
            self.progress_var.set("Analisis selesai")
            
        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")
    
    def analyze_estate(self, estate_name, db_path, start_date, end_date):
        # Handle path that is a folder (like PGE 2A)
        if os.path.isdir(db_path):
            # Look for .FDB file in the folder
            for file in os.listdir(db_path):
                if file.upper().endswith('.FDB'):
                    db_path = os.path.join(db_path, file)
                    break
            else:
                self.log_message(f"  No .FDB file found in {db_path}")
                return None
        
        if not os.path.exists(db_path):
            self.log_message(f"  Database not found: {db_path}")
            return None
        
        try:
            connector = FirebirdConnector(db_path)
            if not connector.test_connection():
                return None
            
            employee_mapping = self.get_employee_mapping(connector)
            divisions, month_tables = self.get_divisions(connector, start_date, end_date)
            
            month_num = start_date.month
            use_status_704_filter = (start_date.month == 5 or end_date.month == 5) # Aktif jika rentang menyentuh bulan Mei
            
            # REMOVED STATIC TARGET VALUES - Now using pure transaction-by-transaction analysis
            if use_status_704_filter:
                self.log_message(f"  *** FILTER TRANSSTATUS 704 AKTIF untuk {estate_name} bulan {month_num} ***")
                self.log_message(f"  Menggunakan analisis transaksi real (bukan nilai statis)")
            
            # Akumulasi per karyawan dari semua divisi
            estate_employee_totals = {}
            
            estate_results = []
            for div_id, div_name in divisions.items():
                result = self.analyze_division(connector, estate_name, div_id, div_name, 
                                             start_date, end_date, employee_mapping, use_status_704_filter, month_tables)
                if result:
                    # Akumulasi per karyawan
                    for emp_id, emp_data in result['employee_details'].items():
                        if emp_id not in estate_employee_totals:
                            estate_employee_totals[emp_id] = {
                                'name': emp_data['name'],
                                'kerani': 0,
                                'kerani_verified': 0,
                                'kerani_differences': 0,
                                'mandor': 0,
                                'asisten': 0
                            }
                        
                        estate_employee_totals[emp_id]['kerani'] += emp_data['kerani']
                        estate_employee_totals[emp_id]['kerani_verified'] += emp_data['kerani_verified']
                        estate_employee_totals[emp_id]['kerani_differences'] += emp_data['kerani_differences']
                        estate_employee_totals[emp_id]['mandor'] += emp_data['mandor']
                        estate_employee_totals[emp_id]['asisten'] += emp_data['asisten']
                    
                    estate_results.append(result)
            
            # NO STATIC ADJUSTMENTS - Using pure transaction-by-transaction analysis results
            if use_status_704_filter:
                total_actual_differences = sum(emp_data['kerani_differences'] for emp_data in estate_employee_totals.values())
                self.log_message(f"  HASIL ANALISIS REAL: {total_actual_differences} total perbedaan ditemukan")
                
                # Log detail per karyawan untuk transparansi
                for emp_id, emp_data in estate_employee_totals.items():
                    if emp_data['kerani_differences'] > 0:
                        user_name = emp_data['name']
                        differences = emp_data['kerani_differences']
                        verified = emp_data['kerani_verified']
                        percentage = (differences / verified * 100) if verified > 0 else 0
                        self.log_message(f"    {user_name}: {differences} perbedaan dari {verified} transaksi terverifikasi ({percentage:.1f}%)")
            
            return estate_results
            
        except Exception as e:
            self.log_message(f"  Error analyzing estate {estate_name}: {e}")
            return None
    
    def get_employee_mapping(self, connector):
        query = "SELECT ID, NAME FROM EMP"
        try:
            result = connector.execute_query(query)
            df = connector.to_pandas(result)
            mapping = {}
            if not df.empty:
                for _, row in df.iterrows():
                    emp_id = str(row.iloc[0]).strip()
                    emp_name = str(row.iloc[1]).strip()
                    mapping[emp_id] = emp_name
            return mapping
        except:
            return {}
    
    # REMOVED: get_employee_key_for_target function no longer needed
    # Now using pure transaction-by-transaction analysis without static targets
    
    def get_divisions(self, connector, start_date, end_date):
        # Generate all month tables within the date range
        month_tables = []
        current_date = start_date
        while current_date <= end_date:
            month_tables.append(f"FFBSCANNERDATA{current_date.month:02d}")
            # Move to the next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1, day=1)
        
        month_tables = list(set(month_tables)) # Remove duplicates
        self.log_message(f"  Tabel yang akan di-query: {', '.join(month_tables)}")

        all_divisions = {}
        for ffb_table in month_tables:
            query = f"""
            SELECT DISTINCT b.DIVID, c.DIVNAME
            FROM {ffb_table} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            LEFT JOIN CRDIVISION c ON b.DIVID = c.ID
            WHERE b.DIVID IS NOT NULL AND c.DIVNAME IS NOT NULL
            """
            
            try:
                result = connector.execute_query(query)
                df = connector.to_pandas(result)
                if not df.empty:
                    for _, row in df.iterrows():
                        div_id = str(row.iloc[0]).strip()
                        div_name = str(row.iloc[1]).strip()
                        if div_id not in all_divisions:
                            all_divisions[div_id] = div_name
            except Exception as e:
                self.log_message(f"  Peringatan saat mengambil divisi dari {ffb_table}: {e}")
                continue # Continue to next table if one fails
        
        return all_divisions, month_tables

    def analyze_division(self, connector, estate_name, div_id, div_name, start_date, end_date, employee_mapping, use_status_704_filter, month_tables):
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        all_data_df = pd.DataFrame()
        
        for ffb_table in month_tables:
            # Query untuk mendapatkan data granular untuk analisis duplikat
            query = f"""
            SELECT a.ID, a.SCANUSERID, a.OCID, a.WORKERID, a.CARRIERID, a.FIELDID, a.TASKNO,
                   a.RIPEBCH, a.UNRIPEBCH, a.BLACKBCH, a.ROTTENBCH, a.LONGSTALKBCH, a.RATDMGBCH,
                   a.LOOSEFRUIT, a.TRANSNO, a.TRANSDATE, a.TRANSTIME, a.UPLOADDATETIME,
                   a.RECORDTAG, a.TRANSSTATUS, a.TRANSTYPE, a.LASTUSER, a.LASTUPDATED,
                   a.OVERRIPEBCH, a.UNDERRIPEBCH, a.ABNORMALBCH, a.LOOSEFRUIT2
            FROM {ffb_table} a
            JOIN OCFIELD b ON a.FIELDID = b.ID
            WHERE b.DIVID = '{div_id}'
                AND a.TRANSDATE >= '{start_str}' 
                AND a.TRANSDATE <= '{end_str}'
            """
            try:
                result = connector.execute_query(query)
                df_monthly = connector.to_pandas(result)
                if not df_monthly.empty:
                    all_data_df = pd.concat([all_data_df, df_monthly], ignore_index=True)
            except Exception as e:
                self.log_message(f"  Peringatan saat mengambil data dari {ffb_table}: {e}")
                continue

        df = all_data_df
        if df.empty:
            return None
        
        # Hapus duplikat jika ada data yang tumpang tindih
        df.drop_duplicates(subset=['ID'], inplace=True)
        
        # Logika dari analisis_perbedaan_panen.py: cari duplikat berdasarkan TRANSNO
        duplicated_rows = df[df.duplicated(subset=['TRANSNO'], keep=False)]
        verified_transnos = set(duplicated_rows['TRANSNO'].tolist())

        employee_details = {}
        
        # Inisialisasi struktur detail karyawan
        all_user_ids = df['SCANUSERID'].unique()
        for user_id in all_user_ids:
            user_id_str = str(user_id).strip()
            employee_details[user_id_str] = {
                'name': employee_mapping.get(user_id_str, f"EMP-{user_id_str}"),
                'kerani': 0,
                'kerani_verified': 0, # Tambahan untuk verifikasi per kerani
                'kerani_differences': 0, # Tambahan untuk jumlah perbedaan input
                'mandor': 0,
                'asisten': 0
            }

        # Hitung data Kerani berdasarkan duplikat dan perbedaan input
        kerani_df = df[df['RECORDTAG'] == 'PM']
        if not kerani_df.empty:
            for user_id, group in kerani_df.groupby('SCANUSERID'):
                user_id_str = str(user_id).strip()
                total_created = len(group)
                
                # Hitung jumlah perbedaan input untuk transaksi yang terverifikasi
                # FILTER KHUSUS: Gunakan TRANSSTATUS 704 untuk Estate 1A dan bulan Mei 2025
                differences_count = 0
                for _, kerani_row in group.iterrows():
                    if kerani_row['TRANSNO'] in verified_transnos:
                        # Cari transaksi dengan TRANSNO yang sama tapi RECORDTAG berbeda
                        matching_transactions = df[(df['TRANSNO'] == kerani_row['TRANSNO']) & 
                                                  (df['RECORDTAG'] != 'PM')]
                        
                        # FILTER KHUSUS: Untuk bulan Mei, hanya hitung perbedaan jika 
                        # Mandor/Asisten memiliki TRANSSTATUS = 704 (Kerani bisa 731/732/704)
                        if use_status_704_filter:
                            # Filter hanya transaksi Mandor/Asisten dengan TRANSSTATUS 704 untuk perhitungan perbedaan
                            matching_transactions = matching_transactions[matching_transactions['TRANSSTATUS'] == '704']
                        
                        if not matching_transactions.empty:
                            # Prioritaskan P1 (Asisten) jika ada, jika tidak gunakan P5 (Mandor) - SAMA DENGAN analisis_perbedaan_panen.py
                            p1_records = matching_transactions[matching_transactions['RECORDTAG'] == 'P1']
                            p5_records = matching_transactions[matching_transactions['RECORDTAG'] == 'P5']
                            
                            if not p1_records.empty:
                                other_row = p1_records.iloc[0]
                            elif not p5_records.empty:
                                other_row = p5_records.iloc[0]
                            else:
                                continue
                            
                            # Hitung perbedaan untuk setiap field - MENGGUNAKAN LOGIKA SAMA DENGAN analisis_perbedaan_panen.py
                            fields_to_compare = ['RIPEBCH', 'UNRIPEBCH', 'BLACKBCH', 'ROTTENBCH', 
                                               'LONGSTALKBCH', 'RATDMGBCH', 'LOOSEFRUIT']
                            
                            # Count as 1 transaction difference if ANY field differs (not per field)
                            has_difference = False
                            for field in fields_to_compare:
                                try:
                                    kerani_val = float(kerani_row[field]) if kerani_row[field] else 0
                                    other_val = float(other_row[field]) if other_row[field] else 0
                                    if kerani_val != other_val:
                                        has_difference = True
                                        break  # Exit loop once we find any difference
                                except (ValueError, TypeError) as e:
                                    print(f"Warning: Error comparing {field}: {e}")
                                    continue
                            
                            # Count as 1 transaction difference if any field differs
                            if has_difference:
                                differences_count += 1
                
                # Hitung persentase terverifikasi
                verified_count = len(group[group['TRANSNO'].isin(verified_transnos)])
                percentage = (verified_count / total_created * 100) if total_created > 0 else 0
                
                if user_id_str in employee_details:
                    employee_details[user_id_str]['kerani'] = total_created
                    employee_details[user_id_str]['kerani_verified'] = verified_count
                    employee_details[user_id_str]['kerani_differences'] = differences_count

        # Hitung data Mandor
        mandor_df = df[df['RECORDTAG'] == 'P1']
        if not mandor_df.empty:
            mandor_counts = mandor_df.groupby('SCANUSERID').size()
            for user_id, count in mandor_counts.items():
                user_id_str = str(user_id).strip()
                if user_id_str in employee_details:
                    employee_details[user_id_str]['mandor'] = count

        # Hitung data Asisten
        asisten_df = df[df['RECORDTAG'] == 'P5']
        if not asisten_df.empty:
            asisten_counts = asisten_df.groupby('SCANUSERID').size()
            for user_id, count in asisten_counts.items():
                user_id_str = str(user_id).strip()
                if user_id_str in employee_details:
                    employee_details[user_id_str]['asisten'] = count

        # Hitung total divisi
        kerani_total = sum(d['kerani'] for d in employee_details.values())
        mandor_total = sum(d['mandor'] for d in employee_details.values())
        asisten_total = sum(d['asisten'] for d in employee_details.values())
        
        # Verifikasi keseluruhan berdasarkan logika duplikat
        div_kerani_verified_total = sum(d['kerani_verified'] for d in employee_details.values())
        verification_rate = (div_kerani_verified_total / kerani_total * 100) if kerani_total > 0 else 0
        
        # Log informasi untuk analisis dengan filter status 704
        if use_status_704_filter:
            self.log_message(f"  *** FILTER TRANSSTATUS 704 AKTIF untuk {estate_name} ***")
            total_differences = sum(d['kerani_differences'] for d in employee_details.values())
            self.log_message(f"  Total perbedaan transaksi dengan filter 704: {total_differences}")
            
            # Log detail per karyawan untuk transparansi
            for emp_id, emp_data in employee_details.items():
                if emp_data['kerani_differences'] > 0:
                    verified = emp_data.get('kerani_verified', 0)
                    differences = emp_data['kerani_differences']
                    percentage = (differences / verified * 100) if verified > 0 else 0
                    self.log_message(f"    👤 {emp_data['name']}: {differences} perbedaan dari {verified} terverifikasi ({percentage:.1f}%)")
        
        return {
            'estate': estate_name,
            'division': div_name,
            'kerani_total': kerani_total,
            'mandor_total': mandor_total,
            'asisten_total': asisten_total,
            'verifikasi_total': div_kerani_verified_total, # Total transaksi Kerani yang terverifikasi
            'verification_rate': verification_rate,
            'employee_details': employee_details
        }
    
    def create_pdf_report(self, all_results, start_date, end_date):
        try:
            output_dir = "reports"
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            period = f"{start_date.strftime('%B_%Y')}"
            filename = f"Laporan_Kinerja_Kerani_Mandor_Asisten_{period}_{timestamp}.pdf"
            filepath = os.path.join(output_dir, filename)
            
            # Create PDF document with LANDSCAPE orientation and custom margins
            doc = SimpleDocTemplate(
                filepath, 
                pagesize=landscape(A4),
                leftMargin=30,
                rightMargin=30,
                topMargin=40,
                bottomMargin=40
            )
            styles = getSampleStyleSheet()
            story = []
            
            # Company Header with Logo
            try:
                logo_path = r"D:\Gawean Rebinmas\Monitoring Database\Laporan_Ifess_beda_transno\all_transaksi\assets\logo_rebinmas.jpeg"
                if os.path.exists(logo_path):
                    # Create logo with proper sizing (200x200 pixels converted to points)
                    logo = Image(logo_path, width=72, height=72)  # 1 inch = 72 points
                    logo.hAlign = 'CENTER'
                    story.append(logo)
                    story.append(Spacer(1, 10))
            except Exception as e:
                print(f"Logo loading error: {e}")
            
            header_style = ParagraphStyle(
                'CompanyHeader',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#2E4057'),
                alignment=1,
                spaceAfter=5,
                fontName='Helvetica-Bold'
            )
            
            company_header = Paragraph(
                "<b>PT. REBINMAS JAYA</b><br/>SISTEM MONITORING TRANSAKSI FFB", 
                header_style
            )
            story.append(company_header)
            story.append(Spacer(1, 10))
            
            # Main Title with Enhanced Styling
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#1A365D'),
                spaceAfter=8,
                spaceBefore=10,
                alignment=1,
                fontName='Helvetica-Bold'
            )
            
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#4A5568'),
                spaceAfter=25,
                alignment=1,
                fontName='Helvetica'
            )
            
            title = Paragraph("LAPORAN KINERJA KERANI, MANDOR, DAN ASISTEN", title_style)
            subtitle = Paragraph(f"Periode: {start_date.strftime('%d %B %Y')} - {end_date.strftime('%d %B %Y')}", subtitle_style)
            
            story.append(title)
            story.append(subtitle)
            
            # Add summary statistics box
            total_estates = len(set(result['estate'] for result in all_results))
            total_divisions = len(all_results)
            
            summary_style = ParagraphStyle(
                'SummaryBox',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#2D3748'),
                alignment=1,
                spaceAfter=20,
                leftIndent=50,
                rightIndent=50
            )
            
            summary_text = f"""<b>RINGKASAN ANALISIS:</b> {total_estates} Estate • {total_divisions} Divisi • 
            Analisis Transaksi Real-time • Verifikasi Otomatis"""
            
            summary_box = Paragraph(summary_text, summary_style)
            story.append(summary_box)
            story.append(Spacer(1, 15))
            
            # Create table data with enhanced columns
            table_data = []
            
            # Enhanced Header with White Text (No Boxes)
            header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontSize=8, alignment=1, fontName='Helvetica-Bold', textColor=colors.white)
            header = [
                Paragraph('ESTATE', header_style),
                Paragraph('DIVISI', header_style),
                Paragraph('KARYAWAN', header_style),
                Paragraph('ROLE', header_style),
                Paragraph('JUMLAH<br/>TRANSAKSI', header_style),
                Paragraph('PERSENTASE<br/>TERVERIFIKASI', header_style),
                Paragraph('KETERANGAN<br/>PERBEDAAN', header_style)
            ]
            table_data.append(header)
            
            # Grand totals
            grand_kerani = 0
            grand_mandor = 0
            grand_asisten = 0
            grand_kerani_verified = 0 # FIX: Accumulator for verified kerani transactions
            
            # Process each result
            for result in all_results:
                estate = result['estate']
                division = result['division']
                kerani_total = result['kerani_total']
                mandor_total = result['mandor_total']
                asisten_total = result['asisten_total']
                verifikasi_total = result['verifikasi_total']
                verification_rate = result['verification_rate']
                employee_details = result['employee_details']
                
                # Add division summary row
                # Total transaksi = hanya dari Kerani (tanpa Asisten/Mandor)
                # Persentase terverifikasi = Verified Kerani Transactions / Total Kerani
                total_kerani_only = kerani_total
                total_verified_kerani = verifikasi_total  # Use actual verified kerani transactions
                division_verification_rate = (total_verified_kerani / total_kerani_only * 100) if total_kerani_only > 0 else 0
                
                # Create paragraph styles for table cells
                cell_style = ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)
                cell_style_left = ParagraphStyle('CellStyleLeft', parent=styles['Normal'], fontSize=8, alignment=0)
                
                table_data.append([
                    Paragraph(estate, cell_style),
                    Paragraph(division, cell_style),
                    Paragraph(f"== {division} TOTAL ==", cell_style),
                    Paragraph('SUMMARY', cell_style),
                    Paragraph(str(total_kerani_only), cell_style),
                    Paragraph(f"{division_verification_rate:.2f}% ({total_verified_kerani})", cell_style),
                    Paragraph("", cell_style)
                ])
                
                # Collect employee rows by role type for proper grouping
                kerani_rows = []
                mandor_rows = []
                asisten_rows = []
                
                for emp_id, emp_data in employee_details.items():
                    # KERANI row - Persentase = % transaksi yang sudah diverifikasi dari total yang ia buat
                    if emp_data['kerani'] > 0:
                        # Untuk KERANI: % transaksi yang sudah diverifikasi dari total yang ia buat
                        kerani_verification_rate = (emp_data.get('kerani_verified', 0) / emp_data['kerani'] * 100) if emp_data['kerani'] > 0 else 0
                        
                        # Format dengan jumlah terverifikasi dalam tanda kurung
                        verified_count = emp_data.get('kerani_verified', 0)
                        differences_count = emp_data.get('kerani_differences', 0)
                        percentage_text = f"{kerani_verification_rate:.2f}% ({verified_count})"
                        
                        # Hitung persentase perbedaan = Total perbedaan / Total transaksi terverifikasi Kerani
                        difference_percentage = (differences_count / verified_count * 100) if verified_count > 0 else 0
                        keterangan_text = f"{differences_count} perbedaan ({difference_percentage:.1f}%)"
                        
                        kerani_rows.append([
                            Paragraph(estate, cell_style),
                            Paragraph(division, cell_style),
                            Paragraph(emp_data['name'], cell_style_left),
                            Paragraph('KERANI', cell_style),
                            Paragraph(str(emp_data['kerani']), cell_style),
                            Paragraph(percentage_text, cell_style),
                            Paragraph(keterangan_text, cell_style)
                        ])
                    
                    # MANDOR row - Persentase = % transaksi yang ia buat per total Kerani di divisi
                    if emp_data['mandor'] > 0:
                        # Untuk MANDOR: % transaksi yang ia buat per total Kerani di divisi
                        mandor_percentage = (emp_data['mandor'] / kerani_total * 100) if kerani_total > 0 else 0
                        mandor_rows.append([
                            Paragraph(estate, cell_style),
                            Paragraph(division, cell_style),
                            Paragraph(emp_data['name'], cell_style_left),
                            Paragraph('MANDOR', cell_style),
                            Paragraph(str(emp_data['mandor']), cell_style),
                            Paragraph(f"{mandor_percentage:.2f}%", cell_style),
                            Paragraph("", cell_style)
                        ])
                    
                    # ASISTEN row - Persentase = % transaksi yang ia buat per total Kerani di divisi
                    if emp_data['asisten'] > 0:
                        # Untuk ASISTEN: % transaksi yang ia buat per total Kerani di divisi
                        asisten_percentage = (emp_data['asisten'] / kerani_total * 100) if kerani_total > 0 else 0
                        asisten_rows.append([
                            Paragraph(estate, cell_style),
                            Paragraph(division, cell_style),
                            Paragraph(emp_data['name'], cell_style_left),
                            Paragraph('ASISTEN', cell_style),
                            Paragraph(str(emp_data['asisten']), cell_style),
                            Paragraph(f"{asisten_percentage:.2f}%", cell_style),
                            Paragraph("", cell_style)
                        ])
                
                # Add rows in proper order: KERANI first, then MANDOR, then ASISTEN
                for row in kerani_rows:
                    table_data.append(row)
                for row in mandor_rows:
                    table_data.append(row)
                for row in asisten_rows:
                    table_data.append(row)
                
                # Add separator
                table_data.append([
                    Paragraph('', cell_style), Paragraph('', cell_style), Paragraph('', cell_style),
                    Paragraph('', cell_style), Paragraph('', cell_style), Paragraph('', cell_style), Paragraph('', cell_style)
                ])
                
                # Add to grand totals
                grand_kerani += kerani_total
                grand_mandor += mandor_total
                grand_asisten += asisten_total
                grand_kerani_verified += verifikasi_total # FIX: Accumulate verified totals
            
            # Add grand total row
            # Total transaksi = hanya dari Kerani (tanpa Asisten/Mandor)
            # Persentase terverifikasi = Verified Kerani Transactions / Total Kerani
            grand_total_kerani_only = grand_kerani
            grand_total_verified_kerani = grand_kerani_verified  # Use actual verified kerani transactions
            grand_verification_rate = (grand_total_verified_kerani / grand_total_kerani_only * 100) if grand_total_kerani_only > 0 else 0
            
            # Create paragraph styles for grand total (outside the loop)
            cell_style = ParagraphStyle('CellStyle', parent=styles['Normal'], fontSize=8, alignment=1)
            
            table_data.append([
                Paragraph('=== GRAND TOTAL ===', cell_style),
                Paragraph('', cell_style),
                Paragraph('', cell_style),
                Paragraph('', cell_style),
                Paragraph(str(grand_total_kerani_only), cell_style),
                Paragraph(f"{grand_verification_rate:.2f}% ({grand_total_verified_kerani})", cell_style),
                Paragraph("", cell_style)
            ])
            
            # Create table with custom column widths for better layout and text wrapping
            col_widths = [90, 90, 140, 70, 80, 110, 120]  # Optimized column widths for better text wrapping
            table = Table(table_data, repeatRows=1, colWidths=col_widths)
            
            # Enhanced Modern Table Styling
            style = TableStyle([
                # Header styling - clean header without boxes
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C5282')),  # Deep blue header
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Body styling with alternating colors
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Grid styling - ONLY for body rows (excluding header)
                ('GRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),  # Light gray grid for body only
                
                # Alternating row colors for better readability
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F7FAFC'), colors.white]),
            ])
            
            # Enhanced row highlighting with modern color schemes
            for i, row in enumerate(table_data):
                # Skip header row
                if i == 0:
                    continue
                    
                # Highlight SUMMARY and GRAND TOTAL rows with premium styling
                if 'TOTAL' in str(row[2]) or 'GRAND TOTAL' in str(row[0]):
                    style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#4299E1'))  # Professional blue
                    style.add('TEXTCOLOR', (0, i), (-1, i), colors.white)
                    style.add('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold')
                    style.add('FONTSIZE', (0, i), (-1, i), 9)
                    style.add('TOPPADDING', (0, i), (-1, i), 10)
                    style.add('BOTTOMPADDING', (0, i), (-1, i), 10)
                
                # Enhanced KERANI row styling
                elif len(row) > 3 and hasattr(row[3], 'text') and 'KERANI' in str(row[3].text):
                    # Highlight entire KERANI row with subtle background
                    style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FFF5F5'))  # Light red background
                    
                    # Percentage column with attention-grabbing color
                    style.add('TEXTCOLOR', (5, i), (5, i), colors.HexColor('#E53E3E'))  # Strong red
                    style.add('FONTNAME', (5, i), (5, i), 'Helvetica-Bold')
                    
                    # Keterangan column with warning styling
                    if len(row) > 6 and row[6]:
                        style.add('BACKGROUND', (6, i), (6, i), colors.HexColor('#FED7D7'))  # Light red highlight
                        style.add('TEXTCOLOR', (6, i), (6, i), colors.HexColor('#C53030'))  # Dark red text
                        style.add('FONTNAME', (6, i), (6, i), 'Helvetica-Bold')
                
                # Enhanced MANDOR row styling
                elif len(row) > 3 and hasattr(row[3], 'text') and 'MANDOR' in str(row[3].text):
                    style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F0FFF4'))  # Light green background
                    style.add('TEXTCOLOR', (5, i), (5, i), colors.HexColor('#38A169'))  # Professional green
                    style.add('FONTNAME', (5, i), (5, i), 'Helvetica-Bold')
                
                # Enhanced ASISTEN row styling
                elif len(row) > 3 and hasattr(row[3], 'text') and 'ASISTEN' in str(row[3].text):
                    style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F0F9FF'))  # Light blue background
                    style.add('TEXTCOLOR', (5, i), (5, i), colors.HexColor('#3182CE'))  # Professional blue
                    style.add('FONTNAME', (5, i), (5, i), 'Helvetica-Bold')
                
                # Empty separator rows
                elif all(not str(cell).strip() for cell in row):
                    style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#EDF2F7'))  # Light separator
                    style.add('TOPPADDING', (0, i), (-1, i), 3)
                    style.add('BOTTOMPADDING', (0, i), (-1, i), 3)
            
            table.setStyle(style)
            story.append(table)
            
            story.append(Spacer(1, 20))
            
            # Enhanced explanation section with modern styling
            explanation_title_style = ParagraphStyle(
                'ExplanationTitle',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=colors.HexColor('#2D3748'),
                spaceBefore=15,
                spaceAfter=10,
                fontName='Helvetica-Bold'
            )
            
            explanation_style = ParagraphStyle(
                'Explanation',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#4A5568'),
                spaceBefore=5,
                spaceAfter=5,
                leftIndent=20,
                bulletIndent=10,
                alignment=0
            )
            
            # Main explanation section
            explanation_title = Paragraph("PENJELASAN LAPORAN KINERJA", explanation_title_style)
            story.append(explanation_title)
            
            explanations = [
                "<b>KERANI:</b> % transaksi yang sudah diverifikasi (ada duplikat TRANSNO dengan P1/P5) dari total yang ia buat. Angka dalam kurung menunjukkan jumlah transaksi terverifikasi.",
                "<b>MANDOR/ASISTEN:</b> % transaksi yang ia buat per total Kerani di divisi tersebut (warna hijau).",
                "<b>SUMMARY:</b> % verifikasi keseluruhan divisi (Total Transaksi Kerani Terverifikasi / Total Transaksi Kerani). Angka dalam kurung menunjukkan jumlah transaksi Kerani yang terverifikasi.",
                "<b>GRAND TOTAL:</b> % verifikasi keseluruhan untuk semua estate yang dipilih (Total Semua Transaksi Kerani Terverifikasi / Total Semua Transaksi Kerani). Angka dalam kurung menunjukkan jumlah total transaksi Kerani yang terverifikasi.",
                "<b>Jumlah Transaksi:</b> Untuk SUMMARY dan GRAND TOTAL hanya menghitung transaksi Kerani (tanpa Asisten/Mandor)."
            ]
            
            for explanation_text in explanations:
                explanation_para = Paragraph(f"• {explanation_text}", explanation_style)
                story.append(explanation_para)
            
            story.append(Spacer(1, 15))
            
            # Enhanced differences explanation
            differences_title = Paragraph("⚠️ KETERANGAN PERBEDAAN INPUT (INDIKATOR KINERJA)", explanation_title_style)
            story.append(differences_title)
            
            differences_explanations = [
                "<b>Metodologi:</b> Untuk setiap transaksi KERANI yang terverifikasi, sistem menghitung jumlah field yang berbeda antara input KERANI dan input MANDOR/ASISTEN.",
                "<b>Field yang dibandingkan:</b> RIPEBCH, UNRIPEBCH, BLACKBCH, ROTTENBCH, LONGSTALKBCH, RATDMGBCH, LOOSEFRUIT.",
                "<b>Format:</b> 'X perbedaan (Y%)' dimana Y% = (X perbedaan / Jumlah transaksi terverifikasi) × 100.",
                "<b>Interpretasi:</b> Semakin banyak perbedaan, semakin besar kemungkinan ada ketidakakuratan dalam input data."
            ]
            
            for diff_text in differences_explanations:
                diff_para = Paragraph(f"• {diff_text}", explanation_style)
                story.append(diff_para)
            
            # Add footer with generation info
            story.append(Spacer(1, 20))
            
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#718096'),
                alignment=1,
                spaceBefore=10
            )
            
            footer_text = f"""📅 Laporan dibuat pada: {datetime.now().strftime('%d %B %Y, %H:%M:%S')} | 
            🔄 Sistem Analisis Real-time | 🏢 PT. Rebinmas Jaya"""
            
            footer = Paragraph(footer_text, footer_style)
            story.append(footer)
            
            # Build PDF
            doc.build(story)
            
            return filepath
            
        except Exception as e:
            self.log_message(f"Error creating PDF: {str(e)}")
            return None
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.results_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.results_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_results(self):
        self.results_text.delete(1.0, tk.END)
    
    def open_output_folder(self):
        output_dir = "reports"
        if os.path.exists(output_dir):
            os.startfile(output_dir)

def main():
    root = tk.Tk()
    app = MultiEstateFFBAnalysisGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()