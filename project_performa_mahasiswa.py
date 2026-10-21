import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import plotly.express as px

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Early Warning System Performa Mahasiswa",
    page_icon="https://cdn-icons-png.flaticon.com/512/8716/8716565.png",
    layout="wide"
)

# -----------------------------------------------------------------------------
# FITUR KEAMANAN: Inisialisasi State Autentikasi
# -----------------------------------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None

# Kredensial pengguna sederhana
USERS = {
    "dosen": {"password": "dosen123", "role": "Dosen / Pengelola Akademik"},
    "admin": {"password": "admin123", "role": "Administrator"},
    "mahasiswa": {"password": "mhs123", "role": "Mahasiswa"}
}

def login_form():
    st.markdown("<h2 style='text-align: center;'> Login Sistem Early Warning</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Silakan masuk menggunakan akun terdaftar untuk mengakses dashboard analitik.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username_input = st.text_input("Username").strip().lower()
            password_input = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Masuk", type="primary", use_container_width=True)
            
            if submit_button:
                if username_input in USERS and USERS[username_input]["password"] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.username = username_input
                    st.session_state.user_role = USERS[username_input]["role"]
                    st.success("Login berhasil! Memuat sistem...")
                    st.rerun()
                else:
                    st.error(" Username atau Password tidak valid!")

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = None
    st.rerun()

# -----------------------------------------------------------------------------
# JIKA BELUM LOGIN: Tampilkan Halaman Login
# -----------------------------------------------------------------------------
if not st.session_state.logged_in:
    login_form()
else:
    # -------------------------------------------------------------------------
    # JIKA SUDAH LOGIN: Tampilkan Dashboard Utama & Panel Keamanan
    # -------------------------------------------------------------------------
    
    # Sidebar Informasi Pengguna & Tombol Logout
    st.sidebar.markdown(f" **Pengguna:** `{st.session_state.username.upper()}`")
    st.sidebar.markdown(f" **Peran:** `{st.session_state.user_role}`")
    
    if st.sidebar.button(" Logout / Keluar", type="secondary"):
        logout()
        
    st.sidebar.markdown("---")

    st.title(" Early Warning System: Prediksi Performa & Risiko Akademik Mahasiswa")
    st.markdown("Purwarupa sistem berbasis *Machine Learning* untuk mendeteksi potensi keterlambatan studi mahasiswa berdasarkan analisis gaya hidup (*student lifestyle*).")

    # -------------------------------------------------------------------------
    # PENGATURAN MENU UTAMA (HANYA SATU SELECTBOX BERDASARKAN PERAN)
    # -------------------------------------------------------------------------
    if st.session_state.user_role == "Mahasiswa":
        menu = st.sidebar.selectbox("Pilih Menu Utama", ["Beranda", "Visualisasi & Analisis Data"])
    else:
        menu = st.sidebar.selectbox("Pilih Menu Utama", ["Beranda", "Prediksi Mandiri Mahasiswa", "Visualisasi & Analisis Data", "Tentang Dataset & Fitur"])

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
        Sistem Peringatan Dini (*Early Warning System*) ini dirancang untuk membantu dosen pembimbing dan institusi 
        dalam melakukan identifikasi dini terhadap mahasiswa yang rentan mengalami penurunan performa akademik 
        atau keterlambatan studi secara proaktif.
        """)
        
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("###  Algoritma Utama")
            st.info("**Random Forest & XGBoost**\n\nModel *Machine Learning* untuk klasifikasi tingkat risiko.")
            
        with col2:
            st.markdown("###  Variabel Analisis")
            st.info("**7 Fitur Gaya Hidup**\n\nJam belajar, tidur, aktivitas fisik, sosialisasi, ekstrakurikuler, GPA, & tingkat stres.")
            
        with col3:
            st.markdown("###  Target Sistem")
            st.info("**Mitigasi Risiko Akademik**\n\nDeteksi dini potensi keterlambatan studi & penurunan performa mahasiswa.")
        
        st.markdown("---")

    elif menu == "Prediksi Mandiri Mahasiswa":
        st.subheader("Formulir Evaluasi Gaya Hidup & Prediksi Risiko")
        st.write("Silakan masukkan parameter gaya hidup mahasiswa di bawah ini:")

        if model is None:
            st.warning(" File model machine learning (`model_rf.pkl`) belum ditemukan di repository GitHub Anda.")
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
                    # Menyimpan hasil ke file CSV agar bisa dilihat oleh Dosen
result_record = {
    'Username': st.session_state.username,
    'Timestamp': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
    'GPA': gpa,
    'Study_Hours': study_hour,
    'Stress_Level': stress_level,
    'Prediction': "Berisiko Tinggi" if (prediction[0] == 1 or prediction[0] > 0) else "Aman"
}
# Simpan ke CSV (append mode)
csv_file = 'student_predictions.csv'
df_record = pd.DataFrame([result_record])
if not os.path.exists(csv_file):
    df_record.to_csv(csv_file, index=False)
else:
    df_record.to_csv(csv_file, mode='a', header=False, index=False)
                    st.markdown("---")
                    st.subheader("Hasil Analisis Sistem:")
                    
                    if prediction[0] == 1 or prediction[0] > 0:
                        st.error(" **Status: BERISIKO TINGGI (Potensi Keterlambatan Studi / Penurunan Performa)**")
                        st.warning("**Rekomendasi Tindakan:** Mahasiswa disarankan segera melakukan konseling akademik dengan dosen wali, mengevaluasi manajemen waktu belajar, serta mengelola tingkat stres.")
                    else:
                        st.success(" **Status: AMAN (Berpotensi Lulus Tepat Waktu dengan Performa Baik)**")
                        st.info("**Rekomendasi Tindakan:** Pertahankan pola gaya hidup seimbang, tingkatkan konsistensi belajar, dan jaga kesehatan fisik serta mental.")
                    
                    # --- VISUALISASI GRAFIK BATANG UNTUK CONFIDENCE SCORE ---
                    st.write("---")
                    st.write(" **Visualisasi Tingkat Keyakinan Model (*Confidence Score Chart*):**")
                    
                    num_classes = prediction_proba.shape[1]
                    col_names = [f"Kelas {i}" for i in range(num_classes)]
                    
                    chart_data = pd.DataFrame(prediction_proba, columns=col_names).T
                    chart_data.columns = ["Probabilitas"]
                    
                    st.bar_chart(chart_data)
                    
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat memproses prediksi: {e}")

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
        st.subheader("Informasi Variabel Dataset *Student Lifestyle*")
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
