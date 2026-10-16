import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Early Warning System Performa Mahasiswa",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Early Warning System: Prediksi Performa & Risiko Akademik Mahasiswa")
st.markdown("Purwarupa sistem berbasis *Machine Learning* (Random Forest / XGBoost) untuk mendeteksi potensi keterlambatan studi mahasiswa berdasarkan analisis gaya hidup (*student lifestyle*).")

# Sidebar Navigasi Menu
menu = st.sidebar.selectbox("Pilih Menu Utama", ["Beranda", "Prediksi Mandiri Mahasiswa", "Tentang Dataset & Fitur"])

# Fungsi untuk memuat model machine learning (.pkl)
@st.cache_resource
def load_model():
    # Pastikan file model .pkl sudah di-upload ke repository GitHub Anda
    model_path = 'model_rf.pkl' # Ganti dengan 'model_xgb.pkl' jika menggunakan XGBoost
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
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Algoritma Utama", value="Random Forest & XGBoost")
    with col2:
        st.metric(label="Variabel Analisis", value="7 Fitur Gaya Hidup")
    with col3:
        st.metric(label="Target Sistem", value="Mitigasi Risiko Akademik")

elif menu == "Prediksi Mandiri Mahasiswa":
    st.subheader("Formulir Evaluasi Gaya Hidup & Prediksi Risiko")
    st.write("Silakan masukkan parameter gaya hidup mahasiswa di bawah ini untuk melihat hasil analisis risiko prediktif:")

    if model is None:
        st.warning("⚠️ File model machine learning (`model_rf.pkl` atau `model_xgb.pkl`) belum ditemukan di repository GitHub Anda. Harap unggah file `.pkl` hasil pelatihan Google Colab ke dalam repository proyek ini.")
    else:
        # Form Input menggunakan Grid 2 Kolom
        col1, col2 = st.columns(2)
        
        with col1:
            study_hour = st.number_input("Jam Belajar per Hari (Study Hours)", min_value=0.0, max_value=24.0, value=4.0, step=0.5)
            extracurricular = st.number_input("Jam Ekstrakurikuler per Hari", min_value=0.0, max_value=24.0, value=1.0, step=0.5)
            sleep_hour = st.number_input("Jam Tidur per Hari (Sleep Hours)", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
            social_hour = st.number_input("Jam Sosialisasi per Hari", min_value=0.0, max_value=24.0, value=2.0, step=0.5)
            
        with col2:
            physical_activity = st.number_input("Jam Aktivitas Fisik per Hari", min_value=0.0, max_value=24.0, value=1.0, step=0.5)
            gpa = st.number_input("Indeks Prestasi Kumulatif / GPA Terakhir", min_value=0.0, max_value=4.0, value=3.25, step=0.01)
            stress_level = st.slider("Tingkat Stres (Skala 1 s.d. 5)", min_value=1, max_value=5, value=2)

        # Tombol Prediksi
        if st.button("Jalankan Analisis & Prediksi Risiko", type="primary"):
            # Menyusun data ke dalam DataFrame sesuai urutan fitur pelatihan model
            input_data = pd.DataFrame([[
                study_hour, 
                extracurricular, 
                sleep_hour, 
                social_hour, 
                physical_activity, 
                gpa, 
                stress_level
            ]], columns=[
                'Study_hour_per_day', 
                'Extracurricular_Hours_Per_Day', 
                'Sleep_Hours_Per_Day', 
                'Social_Hours_Per_Day', 
                'Physical_Activity_Hours_Per_Day', 
                'GPA', 
                'Stress_Level'
            ])
            
            # Melakukan prediksi aman
            try:
                prediction = model.predict(input_data)
                prediction_proba = model.predict_proba(input_data)
                
                st.markdown("---")
                st.subheader("Hasil Analisis Sistem:")
                
                # Asumsi label: 0 = Aman / Lulus Tepat Waktu, 1 = Berisiko Tinggi
                if prediction[0] == 1:
                    st.error("⚠️ **Status: BERISIKO TINGGI (Potensi Keterlambatan Studi / Penurunan Performa)**")
                    st.warning("**Rekomendasi Tindakan:** Mahasiswa disarankan segera melakukan konseling akademik dengan dosen wali, mengevaluasi manajemen waktu belajar, serta mengelola tingkat stres.")
                else:
                    st.success("✅ **Status: AMAN (Berpotensi Lulus Tepat Waktu dengan Performa Baik)**")
                    st.info("**Rekomendasi Tindakan:** Pertahankan pola gaya hidup seimbang, tingkatkan konsistensi belajar, dan jaga kesehatan fisik serta mental.")
                
                # Menampilkan probabilitas keyakinan model menggunakan st.dataframe()
                st.write("---")
                st.write("📊 **Tingkat Keyakinan Model (*Confidence Score*):**")
                confidence_df = pd.DataFrame(prediction_proba, columns=['Probabilitas Aman', 'Probabilitas Berisiko'])
                st.dataframe(confidence_df, use_container_width=True)
                
            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses prediksi: {e}")

elif menu == "Tentang Dataset & Fitur":
    st.subheader("Informasi Variabel Dataset *Student Lifestyle*")
    st.write("Sistem ini dilatih menggunakan 7 fitur utama yang merepresentasikan kebiasaan sehari-hari mahasiswa:")
    
    features_info = pd.DataFrame({
        "Nama Fitur": [
            "study_hour_per_day", 
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
            "Tingkat stres yang dirasakan (Skala 1 s.d. 5)"
        ]
    })
    st.dataframe(features_info, use_container_width=True)
