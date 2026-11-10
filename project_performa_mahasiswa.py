import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import os
from datetime import datetime
import hashlib
from fpdf import FPDF

# ==========================================
# 1. KONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Early Warning System - Performa Mahasiswa",
    page_icon="🎓",
    layout="wide"
)

# Fungsi Hash Password SHA-256
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# Inisialisasi Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'nama_lengkap' not in st.session_state:
    st.session_state.nama_lengkap = ""
if 'user_role' not in st.session_state:
    st.session_state.user_role = ""

# Database Akun Lokal (CSV)
USER_DB = 'users_db.csv'

def load_user_db():
    if os.path.exists(USER_DB):
        df = pd.read_csv(USER_DB)
        if 'nama' in df.columns:
            df['nama'] = df['nama'].fillna('Pengguna')
        return df
    else:
        df_default = pd.DataFrame([
            {"nama": "Administrator", "username": "admin", "password": make_hash("admin123"), "role": "Administrator"},
            {"nama": "Tim BK", "username": "bk", "password": make_hash("bk123"), "role": "Bimbingan Konseling"},
            {"nama": "Zahra Mahasiswa", "username": "zahra", "password": make_hash("zahra123"), "role": "Mahasiswa"}
        ])
        df_default.to_csv(USER_DB, index=False)
        return df_default

# Fungsi Pemetaan Kategori GPA
def map_gpa_category(val):
    if pd.isna(val):
        return "-"
    try:
        fval = float(val)
        if fval < 2.50:
            return "1 - Sangat Rendah (< 2.50)"
        elif fval <= 2.76:
            return "2 - Rendah (2.50 - 2.76)"
        elif fval <= 3.00:
            return "3 - Sedang (2.76 - 3.00)"
        elif fval <= 3.50:
            return "4 - Tinggi (3.01 - 3.50)"
        else:
            return "5 - Sangat Tinggi (3.50 - 4.00)"
    except:
        return str(val)

# ==========================================
# 2. FUNGSI GENERATE LAPORAN PDF RESMI (KOLOM LEBIH LEBAR & JELAS)
# ==========================================
def generate_pdf_report(df):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Header Laporan
    pdf.set_font("Helvetica", 'B', 13)
    pdf.cell(0, 7, "LAPORAN REKAPITULASI MONITORING BIMBINGAN KONSELING (EWS)", ln=True, align='C')
    pdf.set_font("Helvetica", '', 8.5)
    pdf.cell(0, 5, f"Tanggal Cetak: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')} WIB | Early Warning System Mahasiswa", ln=True, align='C')
    pdf.ln(4)
    
    # Header Tabel (Total Lebar = 277 mm untuk A4 Landscape)
    pdf.set_font("Helvetica", 'B', 7)
    pdf.set_fill_color(230, 230, 230)
    
    col_widths = {
        'Nama': 22, 'User': 12, 'Waktu': 25, 'Dept': 20, 
        'Study': 7, 'Eskul': 7, 'Tidur': 7, 'Sosial': 7, 'Fisik': 7, 
        'GPA': 28, 'Stres': 15, 'Masalah': 13, 'Feedback': 30, 
        'Status': 20, 'Keterangan': 60
    }
    
    pdf.cell(col_widths['Nama'], 6, "Nama Mahasiswa", border=1, fill=True)
    pdf.cell(col_widths['User'], 6, "Username", border=1, fill=True)
    pdf.cell(col_widths['Waktu'], 6, "Timestamp", border=1, fill=True)
    pdf.cell(col_widths['Dept'], 6, "Departemen", border=1, fill=True)
    pdf.cell(col_widths['Study'], 6, "Study", border=1, fill=True, align='C')
    pdf.cell(col_widths['Eskul'], 6, "Eskul", border=1, fill=True, align='C')
    pdf.cell(col_widths['Tidur'], 6, "Tidur", border=1, fill=True, align='C')
    pdf.cell(col_widths['Sosial'], 6, "Sosial", border=1, fill=True, align='C')
    pdf.cell(col_widths['Fisik'], 6, "Fisik", border=1, fill=True, align='C')
    pdf.cell(col_widths['GPA'], 6, "GPA (Kategori)", border=1, fill=True, align='C')
    pdf.cell(col_widths['Stres'], 6, "Tingkat Stres", border=1, fill=True)
    pdf.cell(col_widths['Masalah'], 6, "Kategori", border=1, fill=True)
    pdf.cell(col_widths['Feedback'], 6, "Feedback Mhs", border=1, fill=True)
    pdf.cell(col_widths['Status'], 6, "Status Risiko", border=1, fill=True)
    pdf.cell(col_widths['Keterangan'], 6, "Rekomendasi Tindakan BK", border=1, fill=True, ln=True)
    
    # Isi Baris Tabel
    pdf.set_font("Helvetica", '', 6)
    
    stress_mapping = {
        1: "1 - Sangat Rendah",
        2: "2 - Rendah",
        3: "3 - Sedang",
        4: "4 - Tinggi",
        5: "5 - Sangat Tinggi"
    }
    
    for _, row in df.iterrows():
        nama = str(row.get('Nama_Mahasiswa', '-'))[:22]
        user = str(row.get('Username', '-'))[:14]
        waktu = str(row.get('Timestamp', '-'))[:19]
        dept = str(row.get('Department', '-'))[:22]
        
        study = str(row.get('Study_Hours', 0))
        eskul = str(row.get('Extracurricular_Hours', 0))
        tidur = str(row.get('Sleep_Hours', 0))
        sosial = str(row.get('Social_Hours', 0))
        fisik = str(row.get('Physical_Activity', 0))
        
        gpa_text = map_gpa_category(row.get('GPA', 0))[:30]
        
        raw_stres = row.get('Stress_Level', 3)
        if isinstance(raw_stres, (int, float)):
            stres = stress_mapping.get(int(raw_stres), str(raw_stres))
        else:
            stres = str(raw_stres)
        stres = stres[:18]
        
        masalah = str(row.get('Kategori_Masalah', '-'))[:14]
        feedback = str(row.get('Feedback', '-'))[:45]
        status = str(row.get('Prediction', '-'))[:16]
        keterangan = str(row.get('Keterangan', '-'))[:95]
        
        pdf.cell(col_widths['Nama'], 5.5, nama, border=1)
        pdf.cell(col_widths['User'], 5.5, user, border=1)
        pdf.cell(col_widths['Waktu'], 5.5, waktu, border=1)
        pdf.cell(col_widths['Dept'], 5.5, dept, border=1)
        pdf.cell(col_widths['Study'], 5.5, study, border=1, align='C')
        pdf.cell(col_widths['Eskul'], 5.5, eskul, border=1, align='C')
        pdf.cell(col_widths['Tidur'], 5.5, tidur, border=1, align='C')
        pdf.cell(col_widths['Sosial'], 5.5, sosial, border=1, align='C')
        pdf.cell(col_widths['Fisik'], 5.5, fisik, border=1, align='C')
        pdf.cell(col_widths['GPA'], 5.5, gpa_text, border=1, align='C')
        pdf.cell(col_widths['Stres'], 5.5, stres, border=1)
        pdf.cell(col_widths['Masalah'], 5.5, masalah, border=1)
        pdf.cell(col_widths['Feedback'], 5.5, feedback, border=1)
        pdf.cell(col_widths['Status'], 5.5, status, border=1)
        pdf.cell(col_widths['Keterangan'], 5.5, keterangan, border=1, ln=True)
        
    return pdf.output()

# ==========================================
# 3. AUTENTIKASI (LOGIN & REGISTRASI)
# ==========================================
if not st.session_state.logged_in:
    st.title("🎓 Early Warning System (EWS) - Performa & Risiko Akademik")
    st.markdown("---")
    
    tab_login, tab_register = st.tabs(["🔐 Masuk (Login)", "📝 Registrasi Akun Mahasiswa"])
    
    with tab_login:
        st.subheader("Silakan Masuk ke Akun Anda")
        login_user = st.text_input("Username", key="login_username")
        login_pass = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Masuk", type="primary"):
            users_df = load_user_db()
            hashed_pass = make_hash(login_pass)
            matched = users_df[(users_df['username'] == login_user) & (users_df['password'] == hashed_pass)]
            
            if not matched.empty:
                st.session_state.logged_in = True
                st.session_state.username = login_user
                nama_val = matched.iloc[0]['nama']
                if pd.isna(nama_val) or str(nama_val).strip() == "" or str(nama_val).lower() == "nan":
                    nama_val = "Tim BK" if matched.iloc[0]['role'] == "Bimbingan Konseling" else login_user
                st.session_state.nama_lengkap = nama_val
                st.session_state.user_role = matched.iloc[0]['role']
                st.success(f"Berhasil masuk sebagai {st.session_state.user_role}!")
                st.rerun()
            else:
                st.error("Username atau password salah!")

    with tab_register:
        st.subheader("Registrasi Akun Mandiri Mahasiswa")
        reg_nama = st.text_input("Nama Lengkap")
        reg_user = st.text_input("Buat Username Baru")
        reg_pass = st.text_input("Buat Password Baru", type="password")
        
        if st.button("Daftar Sekarang", type="secondary"):
            if reg_nama and reg_user and reg_pass:
                users_df = load_user_db()
                if reg_user in users_df['username'].values:
                    st.warning("Username sudah digunakan, silakan pilih yang lain.")
                else:
                    new_row = pd.DataFrame([{
                        "nama": reg_nama, 
                        "username": reg_user, 
                        "password": make_hash(reg_pass), 
                        "role": "Mahasiswa"
                    }])
                    users_df = pd.concat([users_df, new_row], ignore_index=True)
                    users_df.to_csv(USER_DB, index=False)
                    st.success("Registrasi berhasil! Silakan berpindah ke tab 'Masuk (Login)'.")
            else:
                st.warning("Mohon lengkapi seluruh kolom pendaftaran.")

else:
    # Navigasi Sidebar (RBAC)
    st.sidebar.title(f"Halo, {st.session_state.nama_lengkap}")
    st.sidebar.caption(f"Peran: **{st.session_state.user_role}**")
    st.sidebar.markdown("---")

    if st.session_state.user_role == "Mahasiswa":
        menu = st.sidebar.selectbox("Pilih Menu Utama", ["Beranda", "Prediksi Mandiri Mahasiswa", "Visualisasi & Analisis Data"])
    elif st.session_state.user_role == "Bimbingan Konseling":
        menu = st.sidebar.selectbox("Pilih Menu Utama", ["Beranda", "Monitoring Mahasiswa Berisiko", "Visualisasi & Analisis Data", "Tentang Dataset & Fitur"])
    else: # Administrator
        menu = st.sidebar.selectbox("Pilih Menu Utama", ["Beranda", "Monitoring Mahasiswa Berisiko", "Visualisasi & Analisis Data", "Tentang Dataset & Fitur"])

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Keluar (Logout)"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.nama_lengkap = ""
        st.session_state.user_role = ""
        st.rerun()

    # Memuat Model Machine Learning
    @st.cache_resource
    def load_model():
        model_path = 'model_rf.pkl' 
        if os.path.exists(model_path):
            return joblib.load(model_path)
        return None

    model = load_model()

    # ==========================================
    # MENU 1: BERANDA
    # ==========================================
    if menu == "Beranda":
        st.subheader("🎓 Selamat Datang di Dashboard Early Warning System (EWS)")
        st.write("Purwarupa sistem berbasis *Machine Learning* untuk memantau performa akademik dan tingkat risiko mahasiswa.")
        
        st.info("💡 **Panduan Penggunaan Sistem:**\n"
                "- **Mahasiswa:** Gunakan menu *Prediksi Mandiri Mahasiswa* untuk melakukan evaluasi mandiri dan mengirimkan konsultasi ke BK.\n"
                "- **Tim BK / Admin:** Gunakan menu *Monitoring Mahasiswa Berisiko* untuk merekap data, melihat detail rekomendasi, membaca keluhan, serta mengunduh laporan PDF resmi.")

    # ==========================================
    # MENU 2: PREDIKSI MANDIRI MAHASISWA
    # ==========================================
    elif menu == "Prediksi Mandiri Mahasiswa":
        st.subheader("📋 Formulir Evaluasi Gaya Hidup & Prediksi Risiko")
        st.write(f"Halo **{st.session_state.nama_lengkap}**, silakan masukkan parameter gaya hidup dan keluhan Anda di bawah ini:")

        if model is None:
            st.warning("⚠️ File model machine learning (`model_rf.pkl`) belum ditemukan di direktori Anda.")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                study_hour = st.number_input("Jam Belajar per Hari (Study Hours)", min_value=0.0, max_value=24.0, value=4.0, step=0.5)
                extracurricular = st.number_input("Jam Ekstrakurikuler per Hari", min_value=0.0, max_value=24.0, value=1.0, step=0.5)
                sleep_hour = st.number_input("Jam Tidur per Hari (Sleep Hours)", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
                social_hour = st.number_input("Jam Sosialisasi per Hari", min_value=0.0, max_value=24.0, value=2.0, step=0.5)
                
            with col2:
                physical_activity = st.number_input("Jam Aktivitas Fisik per Hari", min_value=0.0, max_value=24.0, value=1.0, step=0.5)
                
                gpa_option = st.selectbox(
                    "Rentang Indeks Prestasi Kumulatif / GPA",
                    options=[
                        (2.25, "1 - Sangat Rendah (< 2.50)"),
                        (2.65, "2 - Rendah (2.50 - 2.76)"),
                        (2.88, "3 - Sedang (2.76 - 3.00)"),
                        (3.25, "4 - Tinggi (3.01 - 3.50)"),
                        (3.75, "5 - Sangat Tinggi (3.50 - 4.00)")
                    ],
                    format_func=lambda x: x[1],
                    index=2
                )
                GPA = gpa_option[0]
                
                stress_option = st.selectbox(
                    "Tingkat Stres",
                    options=[
                        (1, "1 - Sangat Rendah"),
                        (2, "2 - Rendah"),
                        (3, "3 - Sedang"),
                        (4, "4 - Tinggi"),
                        (5, "5 - Sangat Tinggi")
                    ],
                    format_func=lambda x: x[1],
                    index=2
                )
                stress_level = stress_option[0]

            st.markdown("---")
            st.write("##### **Informasi Tambahan untuk Bimbingan Konseling (BK)**")
            
            col_fb1, col_fb2, col_fb3 = st.columns(3)
            with col_fb1:
                departemen = st.selectbox(
                    "Departemen / Program Studi", 
                    ["Teknik Informatika", "Sistem Informasi", "Teknik Industri", "Manajemen", "Akuntansi", "Ilmu Komunikasi", "Lainnya"]
                )
            with col_fb2:
                kategori_masalah = st.selectbox("Kategori Masalah Utama", ["Akademik", "Non Akademik"])
            with col_fb3:
                feedback_mhs = st.text_area("Feedback / Pesan untuk Tim BK (Opsional)", placeholder="Tuliskan keluhan atau hal yang ingin dikonsultasikan...")

            if st.button("Jalankan Analisis & Prediksi Risiko", type="primary"):
                input_data = pd.DataFrame([[
                    study_hour, 
                    extracurricular, 
                    sleep_hour, 
                    social_hour, 
                    physical_activity, 
                    GPA, 
                    stress_level
                ]], columns=[
                    'Study_Hours_Per_Day', 
                    'Extracurricular_Hours_Per_Day', 
                    'Sleep_Hours_Per_Day', 
                    'Social_Hours_Per_Day', 
                    'Physical_Activity_Hours_Per_Day', 
                    'GPA', 
                    'Stress_Level'
                ])
                
                try:
                    prediction = model.predict(input_data.values)
                    prediction_proba = model.predict_proba(input_data.values)
                    
                    pred_class = int(prediction[0])
                    class_map = {0: "Aman", 1: "Risiko Sedang", 2: "Berisiko Tinggi"}
                    status_str = class_map.get(pred_class, "Aman")

                    if status_str == "Berisiko Tinggi":
                        keterangan_tindakan = "Wajib segera menjadwalkan sesi konseling tatap muka dengan petugas BK untuk penanganan intensif."
                    elif status_str == "Risiko Sedang":
                        keterangan_tindakan = "Disarankan melakukan konsultasi preventif ke BK untuk evaluasi manajemen waktu dan penyesuaian gaya hidup."
                    else:
                        keterangan_tindakan = "Pertahankan pola gaya hidup seimbang, jaga konsistensi belajar, dan pertahankan waktu istirahat."

                    triggers = []
                    if sleep_hour < 6.0:
                        triggers.append(f"⏱️ **Durasi Tidur Kurang:** Hanya {sleep_hour} jam/hari.")
                    if study_hour < 2.0:
                        triggers.append(f"📚 **Jam Belajar Rendah:** Hanya {study_hour} jam/hari.")
                    elif study_hour > 10.0:
                        triggers.append(f"⚠️ **Beban Belajar Berlebih:** {study_hour} jam/hari.")
                    if stress_level >= 4:
                        triggers.append(f"🧠 **Tingkat Stres Tinggi:** Skor stres berada di angka {stress_level}/5.")
                    if GPA <= 2.50:
                        triggers.append(f"📉 **Indeks Prestasi (GPA):** Berada pada kategori rendah (< 2.50).")
                    if social_hour > 6.0:
                        triggers.append(f"🎉 **Waktu Sosialisasi Tinggi:** {social_hour} jam/hari.")
                    
                    if not triggers:
                        triggers.append("✨ Seluruh parameter gaya hidup berada dalam rentang yang seimbang dan sehat.")

                    # SIMPAN HASIL KE CSV
                    result_record = {
                        'Nama_Mahasiswa': st.session_state.nama_lengkap,
                        'Username': st.session_state.username,
                        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'Department': departemen,
                        'Study_Hours': study_hour,
                        'Extracurricular_Hours': extracurricular,
                        'Sleep_Hours': sleep_hour,
                        'Social_Hours': social_hour,
                        'Physical_Activity': physical_activity,
                        'GPA': GPA,
                        'Stress_Level': stress_level,
                        'Kategori_Masalah': kategori_masalah,
                        'Feedback': feedback_mhs if feedback_mhs else "-",
                        'Prediction': status_str,
                        'Keterangan': keterangan_tindakan
                    }
                    csv_file = 'student_predictions.csv'
                    df_record = pd.DataFrame([result_record])
                    if not os.path.exists(csv_file):
                        df_record.to_csv(csv_file, index=False)
                    else:
                        df_record.to_csv(csv_file, mode='a', header=False, index=False)

                    st.markdown("---")
                    st.subheader("📌 Hasil Analisis Sistem & Rekomendasi:")
                    
                    if status_str == "Berisiko Tinggi":
                        st.error("🚨 **Status: BERISIKO TINGGI (Potensi Keterlambatan Studi / Krisis Akademik)**")
                        st.warning(f"**Rekomendasi Tindakan:** {keterangan_tindakan}")
                    elif status_str == "Risiko Sedang":
                        st.warning("⚠️ **Status: RISIKO SEDANG (Perlu Perhatian & Penyesuaian Gaya Hidup)**")
                        st.info(f"**Rekomendasi Tindakan:** {keterangan_tindakan}")
                    else:
                        st.success("✅ **Status: AMAN (Berpotensi Lulus Tepat Waktu dengan Performa Baik)**")
                        st.info(f"**Rekomendasi Tindakan:** {keterangan_tindakan}")
                    
                    st.write("---")
                    st.write("🔍 **Penjelasan Faktor Pemicu Utama (Analisis Sistem):**")
                    for trig in triggers:
                        st.markdown(f"- {trig}")

                    st.write("---")
                    st.write("📊 **Visualisasi Tingkat Keyakinan Model (*Confidence Score Chart*):**")
                    
                    prob_values = prediction_proba[0]
                    if len(prob_values) >= 3:
                        chart_df = pd.DataFrame({
                            'Kategori Risiko': ["Aman", "Risiko Sedang", "Berisiko Tinggi"],
                            'Probabilitas': [prob_values[0], prob_values[1], prob_values[2]],
                            'Warna': ["#2ecc71", "#f39c12", "#e74c3c"]
                        })
                    else:
                        chart_df = pd.DataFrame({
                            'Kategori Risiko': ["Aman", "Berisiko Tinggi"],
                            'Probabilitas': [prob_values[0], prob_values[1]],
                            'Warna': ["#2ecc71", "#e74c3c"]
                        })
                    
                    fig_conf = px.bar(
                        chart_df,
                        x='Kategori Risiko',
                        y='Probabilitas',
                        text='Probabilitas',
                        template='plotly_dark',
                        category_orders={'Kategori Risiko': ["Aman", "Risiko Sedang", "Berisiko Tinggi"]}
                    )
                    fig_conf.update_traces(marker_color=chart_df['Warna'], texttemplate='%{text:.2f}', textposition='outside')
                    fig_conf.update_layout(showlegend=False, yaxis=dict(range=[0, 1.1]), margin=dict(t=30, b=20, l=20, r=20))
                    st.plotly_chart(fig_conf, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat memproses prediksi: {e}")

    # ==========================================
    # MENU 3: MONITORING MAHASISWA BERISIKO (BK / ADMIN)
    # ==========================================
    elif menu == "Monitoring Mahasiswa Berisiko":
        st.subheader("📊 Dashboard Bimbingan Konseling: Monitoring Mahasiswa Berisiko")
        st.write("Berikut adalah rekapitulasi data mahasiswa beserta rincian departemen, keluhan, dan rekomendasi tindakan:")

        csv_file = 'student_predictions.csv'
        df_submissions = pd.DataFrame()
        
        default_columns = [
            'Nama_Mahasiswa', 'Username', 'Timestamp', 'Department', 'Study_Hours', 
            'Extracurricular_Hours', 'Sleep_Hours', 'Social_Hours', 
            'Physical_Activity', 'GPA', 'Stress_Level', 
            'Kategori_Masalah', 'Feedback', 'Prediction', 'Keterangan'
        ]

        if os.path.exists(csv_file):
            try:
                df_submissions = pd.read_csv(csv_file)
                if 'Keterangan' not in df_submissions.columns:
                    df_submissions['Keterangan'] = 'Evaluasi rutin'
                if 'Department' not in df_submissions.columns:
                    df_submissions['Department'] = 'Umum / Lainnya'
            except Exception:
                os.remove(csv_file)
                df_submissions = pd.DataFrame(columns=default_columns)
        else:
            df_submissions = pd.DataFrame(columns=default_columns)

        if not df_submissions.empty:
            risk_filter = st.selectbox("Filter Berdasarkan Status Risiko:", ["Semua Data", "Berisiko Tinggi", "Risiko Sedang", "Aman"])
            if risk_filter != "Semua Data" and 'Prediction' in df_submissions.columns:
                df_filtered = df_submissions[df_submissions['Prediction'] == risk_filter].copy()
            else:
                df_filtered = df_submissions.copy()

            stress_mapping = {
                1: "1 - Sangat Rendah",
                2: "2 - Rendah",
                3: "3 - Sedang",
                4: "4 - Tinggi",
                5: "5 - Sangat Tinggi"
            }
            if 'Stress_Level' in df_filtered.columns:
                df_filtered['Stress_Level'] = df_filtered['Stress_Level'].map(stress_mapping).fillna(df_filtered['Stress_Level'])

            if 'GPA' in df_filtered.columns:
                df_filtered['GPA'] = df_filtered['GPA'].apply(map_gpa_category)

            # Tabel Interaktif dengan Lebar Kolom Fleksibel
            st.dataframe(
                df_filtered, 
                use_container_width=True,
                column_config={
                    "Keterangan": st.column_config.TextColumn("Keterangan Tindakan", width="large"),
                    "Feedback": st.column_config.TextColumn("Feedback Mahasiswa", width="medium"),
                    "Nama_Mahasiswa": st.column_config.TextColumn("Nama Mahasiswa", width="medium"),
                    "Department": st.column_config.TextColumn("Departemen", width="medium"),
                    "GPA": st.column_config.TextColumn("GPA (Kategori)", width="medium"),
                }
            )
            
            st.info(f"Total data terekam: {len(df_submissions)} mahasiswa. Tim BK dapat memfilter status risiko dan mengunduh laporan PDF resmi di bawah ini.")

            # FITUR UNDUH LAPORAN PDF
            st.markdown("---")
            st.subheader("📥 Unduh Laporan Rekapitulasi (PDF Resmi)")
            
            try:
                pdf_data = generate_pdf_report(df_filtered)
                st.download_button(
                    label="📄 Unduh Laporan Rekapitulasi BK (Format PDF)",
                    data=bytes(pdf_data),
                    file_name=f"Laporan_Monitoring_BK_{datetime.now().strftime('%Y-%m-%d')}.pdf",
                    mime="application/pdf",
                    help="Klik untuk mengunduh laporan PDF rapi berformat A4 Landscape untuk arsip BK atau lampiran skripsi."
                )
            except Exception as e:
                st.error(f"Gagal memproses file PDF: {e}. Pastikan modul 'fpdf2' sudah terinstall.")

            # MANAJEMEN HAPUS MULTI-DATA
            st.markdown("---")
            st.subheader("🗑️ Manajemen Hapus Data Rekaman")
            
            row_labels = []
            for i, row in df_submissions.iterrows():
                nama = row.get('Nama_Mahasiswa', 'Tanpa Nama')
                dept = row.get('Department', '-')
                waktu = row.get('Timestamp', '-')
                status = row.get('Prediction', '-')
                row_labels.append(f"Baris {i} | Nama: {nama} ({dept}) | Waktu: {waktu} | Status: {status}")
            
            df_submissions['Row_ID'] = row_labels
            
            selected_items = st.multiselect(
                "Pilih data yang ingin dihapus (bisa memilih lebih dari satu):",
                options=df_submissions['Row_ID'].tolist()
            )
            
            col_action1, col_action2 = st.columns(2)
            
            with col_action1:
                if st.button("Hapus Data Terpilih", type="primary"):
                    if selected_items:
                        indices_to_drop = []
                        for item in selected_items:
                            idx_str = item.split("|")[0].replace("Baris", "").strip()
                            indices_to_drop.append(int(idx_str))
                        
                        df_updated = df_submissions.drop(indices_to_drop).reset_index(drop=True)
                        if 'Row_ID' in df_updated.columns:
                            df_updated = df_updated.drop(columns=['Row_ID'])
                            
                        df_updated.to_csv(csv_file, index=False)
                        st.success(f"Berhasil menghapus {len(indices_to_drop)} data terpilih!")
                        st.rerun()
                    else:
                        st.warning("Pilih minimal satu data pada kotak di atas untuk dihapus.")
            
            with col_action2:
                if st.button("Hapus / Bersihkan Semua Data", type="secondary"):
                    empty_df = pd.DataFrame(columns=default_columns)
                    empty_df.to_csv(csv_file, index=False)
                    st.success("Semua riwayat data berhasil dibersihkan!")
                    st.rerun()
        else:
            st.info("Belum ada data pengisian formulir dari mahasiswa.")

    # ==========================================
    # MENU 4: VISUALISASI & ANALISIS DATA
    # ==========================================
    elif menu == "Visualisasi & Analisis Data":
        st.subheader("📈 Visualisasi & Analisis Data Keseluruhan")
        csv_file = 'student_predictions.csv'
        if os.path.exists(csv_file):
            df_all = pd.read_csv(csv_file)
            if not df_all.empty:
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    fig_status = px.pie(df_all, names='Prediction', title="Distribusi Status Risiko Mahasiswa", template='plotly_dark')
                    st.plotly_chart(fig_status, use_container_width=True)
                with col_v2:
                    if 'Department' in df_all.columns:
                        fig_dept = px.histogram(df_all, x='Department', color='Prediction', title="Sebaran Risiko per Departemen", template='plotly_dark')
                        st.plotly_chart(fig_dept, use_container_width=True)
            else:
                st.info("Belum cukup data untuk ditampilkan dalam grafik.")
        else:
            st.info("Belum ada file data riwayat prediksi.")

    # ==========================================
    # MENU 5: TENTANG DATASET & FITUR
    # ==========================================
    elif menu == "Tentang Dataset & Fitur":
        st.subheader("ℹ️ Tentang Sistem EWS Akademik")
        st.write("Purwarupa ini dikembangkan untuk mendukung penelitian skripsi dalam mengintegrasikan kuesioner mahasiswa dengan instrumen wawancara Bimbingan Konseling berbasis *Machine Learning*.")
        st.markdown("- **Model:** Random Forest Classifier\n- **Keamanan:** Encrypted SHA-256 Authentication & RBAC\n- **Fitur Utama:** Prediksi Mandiri, Analisis Pemicu Otomatis, Monitoring BK, Rekomendasi Tindakan, dan Ekspor Laporan PDF.")
