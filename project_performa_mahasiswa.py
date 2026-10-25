import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import plotly.express as px
import hashlib
from datetime import datetime

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Early Warning System Bimbingan Konseling Mahasiswa",
    page_icon="https://cdn-icons-png.flaticon.com/512/8716/8716565.png",
    layout="wide"
)

# -----------------------------------------------------------------------------
# FITUR KEAMANAN: Fungsi Enkripsi Password (SHA-256)
# -----------------------------------------------------------------------------
def hash_password(password):
    """Mengenkripsi password menggunakan SHA-256 agar aman."""
    return hashlib.sha256(password.encode()).hexdigest()

# Inisialisasi Database Pengguna Sederhana (File CSV atau State)
USER_DB_FILE = 'users_db.csv'

def load_users():
    if os.path.exists(USER_DB_FILE):
        return pd.read_csv(USER_DB_FILE)
    else:
        # Default awal jika file belum ada (Role: BK, Admin, Mahasiswa)
        default_data = pd.DataFrame([
            {"username": "bk", "password": hash_password("bk123"), "role": "Bimbingan Konseling", "nama_lengkap": "Tim BK Kampus"},
            {"username": "admin", "password": hash_password("admin123"), "role": "Administrator", "nama_lengkap": "Admin Sistem"},
            {"username": "an", "password": hash_password("mhs123"), "role": "Mahasiswa", "nama_lengkap": "An"},
            {"username": "zahra", "password": hash_password("mhs123"), "role": "Mahasiswa", "nama_lengkap": "Zahra"}
        ])
        default_data.to_csv(USER_DB_FILE, index=False)
        return default_data

# -----------------------------------------------------------------------------
# INISIALISASI SESSION STATE
# -----------------------------------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'nama_lengkap' not in st.session_state:
    st.session_state.nama_lengkap = None

# -----------------------------------------------------------------------------
# FORM LOGIN & REGISTRASI
# -----------------------------------------------------------------------------
def auth_system():
    st.markdown("<h2 style='text-align: center;'> Sistem Keamanan Early Warning System</h2>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Masuk (Login)", "Daftar Akun Baru (Mahasiswa)"])
    
    df_users = load_users()
    
    with tab1:
        st.markdown("<p style='text-align: center;'>Silakan masuk menggunakan akun terdaftar.</p>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                username_input = st.text_input("Username").strip().lower()
                password_input = st.text_input("Password", type="password")
                submit_button = st.form_submit_button("Masuk", type="primary", use_container_width=True)
                
                if submit_button:
                    hashed_pwd = hash_password(password_input)
                    user_match = df_users[(df_users['username'] == username_input) & (df_users['password'] == hashed_pwd)]
                    
                    if not user_match.empty:
                        st.session_state.logged_in = True
                        st.session_state.username = username_input
                        st.session_state.user_role = user_match.iloc[0]['role']
                        st.session_state.nama_lengkap = user_match.iloc[0]['nama_lengkap']
                        st.success("Login berhasil! Memuat sistem...")
                        st.rerun()
                    else:
                        st.error(" Username atau Password salah!")

    with tab2:
        st.markdown("<p style='text-align: center;'>Pendaftaran khusus untuk akun Mahasiswa baru.</p>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("register_form"):
                reg_nama = st.text_input("Nama Lengkap (Contoh: An, Zahra)")
                reg_username = st.text_input("Buat Username (huruf kecil)").strip().lower()
                reg_password = st.text_input("Buat Password", type="password")
                reg_submit = st.form_submit_button("Daftar Sekarang", use_container_width=True)
                
                if reg_submit:
                    if not reg_nama or not reg_username or not reg_password:
                        st.warning("Semua kolom wajib diisi!")
                    elif reg_username in df_users['username'].values:
                        st.error("Username sudah terdaftar, gunakan username lain.")
                    else:
                        new_user = pd.DataFrame([{
                            "username": reg_username,
                            "password": hash_password(reg_password),
                            "role": "Mahasiswa",
                            "nama_lengkap": reg_nama
                        }])
                        df_updated = pd.concat([df_users, new_user], ignore_index=True)
                        df_updated.to_csv(USER_DB_FILE, index=False)
                        st.success("Registrasi berhasil! Silakan pindah ke tab 'Masuk (Login)' untuk masuk.")

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = None
    st.session_state.nama_lengkap = None
    st.rerun()

# -----------------------------------------------------------------------------
# JIKA BELUM LOGIN
# -----------------------------------------------------------------------------
if not st.session_state.logged_in:
    auth_system()
else:
    # -------------------------------------------------------------------------
    # JIKA SUDAH LOGIN: Tampilkan Dashboard Utama & Panel Keamanan
    # -------------------------------------------------------------------------
    
    # Sidebar Informasi Pengguna Dinamis (Nama Asli: An / Zahra / dll)
    st.sidebar.markdown(f" **Pengguna:** `{st.session_state.nama_lengkap}`")
    st.sidebar.markdown(f" **Peran:** `{st.session_state.user_role}`")
    
    if st.sidebar.button("Logout / Keluar", type="secondary"):
        logout()
        
    st.sidebar.markdown("---")

    st.title("Early Warning System: Prediksi Performa & Risiko Akademik Mahasiswa")
    st.markdown("Purwarupa sistem berbasis *Machine Learning* untuk mendeteksi potensi tingkat stres mahasiswa berdasarkan analisis gaya hidup (*student lifestyle*).")

    # -------------------------------------------------------------------------
    # PENGATURAN MENU UTAMA BERDASARKAN PERAN (RBAC - Role Based Access Control)
    # -------------------------------------------------------------------------
    if st.session_state.user_role == "Mahasiswa":
        menu = st.sidebar.selectbox("Pilih Menu Utama", ["Beranda", "Prediksi Mandiri Mahasiswa", "Visualisasi & Analisis Data"])
    elif st.session_state.user_role == "Bimbingan Konseling":
        menu = st.sidebar.selectbox("Pilih Menu Utama", ["Beranda", "Monitoring Mahasiswa Berisiko", "Visualisasi & Analisis Data", "Tentang Dataset & Fitur"])
    else: # Administrator
        menu = st.sidebar.selectbox("Pilih Menu Utama", ["Beranda", "Monitoring Mahasiswa Berisiko", "Visualisasi & Analisis Data", "Tentang Dataset & Fitur"])

    # Fungsi untuk memuat model machine learning (.pkl)
    @st.cache_resource
    def load_model():
        model_path = 'model_rf.pkl' 
        if os.path.exists(model_path):
            return joblib.load(model_path)
        return None

    model = load_model()

    if menu == "Beranda":
        st.subheader("Selamat Datang di Dashboard Pemantauan Akademik")
        st.write("""
        Sistem Peringatan Dini (*Early Warning System*) ini dirancang untuk membantu tim Bimbingan Konseling (BK) dan institusi 
        dalam melakukan identifikasi dini terhadap mahasiswa yang rentan mengalami penurunan performa akademik 
        atau keterlambatan studi secara proaktif.
        """)
        
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### Algoritma Utama")
            st.info("**Random Forest & XGBoost**\n\nModel *Machine Learning* untuk klasifikasi tingkat risiko.")
            
        with col2:
            st.markdown("### Variabel Analisis")
            st.info("**7 Fitur Gaya Hidup**\n\nJam belajar, tidur, aktivitas fisik, sosialisasi, ekstrakurikuler, GPA, & tingkat stres.")
            
        with col3:
            st.markdown("### Target Sistem")
            st.info("**Mitigasi Risiko Akademik**\n\nDeteksi dini potensi keterlambatan studi & penurunan performa mahasiswa.")
        
        st.markdown("---")

    elif menu == "Prediksi Mandiri Mahasiswa":
        st.subheader("Formulir Evaluasi Gaya Hidup & Prediksi Risiko")
        st.write(f"Halo **{st.session_state.nama_lengkap}**, silakan masukkan parameter gaya hidup Anda di bawah ini:")

        if model is None:
            st.warning(" File model machine learning (`model_rf.pkl`) belum ditemukan di direktori Anda.")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                study_hour = st.number_input("Jam Belajar per Hari (Study Hours)", min_value=0.0, max_value=24.0, value=4.0, step=0.5)
                extracurricular = st.number_input("Jam Ekstrakurikuler per Hari", min_value=0.0, max_value=24.0, value=1.0, step=0.5)
                sleep_hour = st.number_input("Jam Tidur per Hari (Sleep Hours)", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
                social_hour = st.number_input("Jam Sosialisasi per Hari", min_value=0.0, max_value=24.0, value=2.0, step=0.5)
                
            with col2:
                physical_activity = st.number_input("Jam Aktivitas Fisik per Hari", min_value=0.0, max_value=24.0, value=1.0, step=0.5)
                gpa = st.number_input("Indeks Prestasi Kumulatif / GPA Terakhir", min_value=0.0, max_value=4.0, value=3.25, step=0.01)
                
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

            if st.button("Jalankan Analisis & Prediksi Risiko", type="primary"):
                input_data = pd.DataFrame([[
                    study_hour, 
                    extracurricular, 
                    sleep_hour, 
                    social_hour, 
                    physical_activity, 
                    gpa, 
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
                    
                    is_risky = (prediction[0] == 1 or prediction[0] > 0)
                    status_str = "Berisiko Tinggi" if is_risky else "Aman"

                    # SIMPAN HASIL KE CSV DENGAN TIMESTAMP REAL-TIME LOKAL
                    result_record = {
                        'Nama_Mahasiswa': st.session_state.nama_lengkap,
                        'Username': st.session_state.username,
                        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # Real-time timestamp
                        'GPA': gpa,
                        'Study_Hours': study_hour,
                        'Stress_Level': stress_level,
                        'Prediction': status_str
                    }
                    csv_file = 'student_predictions.csv'
                    df_record = pd.DataFrame([result_record])
                    if not os.path.exists(csv_file):
                        df_record.to_csv(csv_file, index=False)
                    else:
                        df_record.to_csv(csv_file, mode='a', header=False, index=False)

                    st.markdown("---")
                    st.subheader("Hasil Analisis Sistem:")
                    
                    if is_risky:
                        st.error(" **Status: BERISIKO TINGGI (Potensi Keterlambatan Studi / Penurunan Performa)**")
                        st.warning("**Rekomendasi Tindakan:** Mahasiswa disarankan segera melakukan konseling di ruang BK, mengevaluasi manajemen waktu belajar, serta mengelola tingkat stres.")
                    else:
                        st.success(" **Status: AMAN (Berpotensi Lulus Tepat Waktu dengan Performa Baik)**")
                        st.info("**Rekomendasi Tindakan:** Pertahankan pola gaya hidup seimbang, tingkatkan konsistensi belajar, dan jaga kesehatan fisik serta mental.")
                    
                    # Visualisasi Confidence Score
                    st.write("---")
                    st.write(" **Visualisasi Tingkat Keyakinan Model (*Confidence Score Chart*):**")
                    num_classes = prediction_proba.shape[1]
                    col_names = [f"Kelas {i}" for i in range(num_classes)]
                    chart_data = pd.DataFrame(prediction_proba, columns=col_names).T
                    chart_data.columns = ["Probabilitas"]
                    st.bar_chart(chart_data)
                    
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat memproses prediksi: {e}")

    elif menu == "Monitoring Mahasiswa Berisiko":
        st.subheader(" Dashboard Bimbingan Konseling: Monitoring Mahasiswa Berisiko")
        st.write("Berikut adalah rekapitulasi data mahasiswa yang telah mengisi *Formulir Evaluasi Gaya Hidup & Prediksi Risiko*:")

        csv_file = 'student_predictions.csv'
        if os.path.exists(csv_file):
            df_submissions = pd.read_csv(csv_file)
            
            # Filter berdasarkan status risiko
            risk_filter = st.selectbox("Filter Berdasarkan Status Risiko:", ["Semua Data", "Berisiko Tinggi", "Aman"])
            if risk_filter == "Berisiko Tinggi":
                df_filtered = df_submissions[df_submissions['Prediction'] == "Berisiko Tinggi"]
            elif risk_filter == "Aman":
                df_filtered = df_submissions[df_submissions['Prediction'] == "Aman"]
            else:
                df_filtered = df_submissions

            st.dataframe(df_filtered, use_container_width=True)
            st.info(f"Total data terekam: {len(df_submissions)} mahasiswa. Tim BK dapat memprioritaskan bimbingan bagi mahasiswa yang berstatus **Berisiko Tinggi**.")

            # FITUR HAPUS DATA (Diberikan untuk Admin / BK)
            st.markdown("---")
            st.write(" **Manajemen Hapus Data Rekaman:**")
            index_to_delete = st.number_input("Pilih indeks baris data yang ingin dihapus (lihat tabel di atas)", min_value=0, max_value=max(0, len(df_submissions)-1), step=1)
            if st.button("Hapus Baris Data Terpilih", type="secondary"):
                if not df_submissions.empty:
                    df_submissions = df_submissions.drop(index_to_delete).reset_index(drop=True)
                    df_submissions.to_csv(csv_file, index=False)
                    st.success(f"Data pada indeks ke-{index_to_delete} berhasil dihapus!")
                    st.rerun()
        else:
            st.info("Belum ada data pengisian formulir dari mahasiswa. Data akan muncul di sini setelah mahasiswa melakukan prediksi mandiri.")

    elif menu == "Visualisasi & Analisis Data":
        st.subheader(" Visualisasi Statistik & Eksplorasi Fitur Dataset")
        st.write("Bagian ini menampilkan grafik interaktif beranimasi untuk perbandingan parameter gaya hidup terhadap performa akademik mahasiswa.")
        
        chart_data = pd.DataFrame({
            'Kategori Risiko': ['Aman / Tepat Waktu', 'Berisiko Rendah', 'Berisiko Tinggi'],
            'Rata-Rata Jam Belajar': [5.5, 3.8, 2.1],
            'Rata-Rata GPA': [3.65, 3.05, 2.30]
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("##### **Rata-Rata Jam Belajar per Hari**")
            fig_study = px.bar(
                chart_data, 
                x='Kategori Risiko', 
                y='Rata-Rata Jam Belajar',
                color='Kategori Risiko',
                text='Rata-Rata Jam Belajar',
                template='plotly_dark'
            )
            fig_study.update_traces(texttemplate='%{text:.1f} Jam', textposition='outside')
            fig_study.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_study, use_container_width=True)
            
        with col2:
            st.write("##### **Rata-Rata GPA (Indeks Prestasi)**")
            fig_gpa = px.bar(
                chart_data, 
                x='Kategori Risiko', 
                y='Rata-Rata GPA',
                color='Kategori Risiko',
                text='Rata-Rata GPA',
                template='plotly_dark'
            )
            fig_gpa.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig_gpa.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_gpa, use_container_width=True)
        
        st.info(" Grafik di atas divisualisasikan secara dinamis untuk memberikan gambaran komparatif mengenai pola kebiasaan mahasiswa terhadap hasil akademik mereka.")

    elif menu == "Tentang Dataset & Fitur":
        st.subheader(" Informasi Variabel Dataset *Student Lifestyle*")
        st.write("Sistem ini dilatih menggunakan 7 fitur utama yang merepresentasikan kebiasaan sehari-hari mahasiswa:")
        
        features_info = pd.DataFrame({
            "Nama Fitur": [
                "Study_Hours_Per_Day", 
                "Extracurricular_Hours_Per_Day", 
                "Sleep_Hours_Per_Day", 
                "Social_Hours_Per_Day", 
                "Physical_Activity_Hours_Per_Day", 
                "GPA", 
                "Stress_Level"
            ],
            "Deskripsi": [
                "Durasi rata-rata waktu belajar mandiri dan kuliah dalam sehari (Jam)",
                "Durasi waktu untuk kegiatan organisasi / ekstrakurikuler dalam sehari (Jam)",
                "Durasi waktu istirahat tidur dalam sehari (Jam)",
                "Durasi waktu bersosialisasi dan rekreasi dalam sehari (Jam)",
                "Durasi waktu olahraga atau aktivitas fisik dalam sehari (Jam)",
                "Nilai Indeks Prestasi Kumulatif mahasiswa",
                "Tingkat stres: 1 (Sangat Rendah), 2 (Rendah), 3 (Sedang), 4 (Tinggi), 5 (Sangat Tinggi)"
            ]
        })
        st.dataframe(features_info, use_container_width=True)
