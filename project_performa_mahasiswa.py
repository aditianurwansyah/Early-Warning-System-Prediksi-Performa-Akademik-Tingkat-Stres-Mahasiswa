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
st.markdown("Purwarupa sistem berbasis *Machine Learning* untuk mendeteksi potensi keterlambatan studi mahasiswa berdasarkan analisis gaya hidup (*student lifestyle*).")

# Sidebar Navigasi Menu
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
        st.markdown("### 🤖 Algoritma Utama")
        st.info("**Random Forest & XGBoost**\n\nModel *Machine Learning* untuk klasifikasi tingkat risiko.")
        
    with col2:
        st.markdown("### 📊 Variabel Analisis")
        st.info("**7 Fitur Gaya Hidup**\n\nJam belajar, tidur, aktivitas fisik, sosialisasi, ekstrakurikuler, GPA, & tingkat stres.")
        
    with col3:
        st.markdown("### 🎯 Target Sistem")
        st.info("**Mitigasi Risiko Akademik**\n\nDeteksi dini potensi keterlambatan studi & penurunan performa mahasiswa.")
    
    st.markdown("---")

elif menu == "Prediksi Mandiri Mahasiswa":
    st.subheader("Formulir Evaluasi Gaya Hidup & Prediksi Risiko")
    st.write("Silakan masukkan parameter gaya hidup mahasiswa di bawah ini:")

    if model is None:
        st.warning("⚠️ File model machine learning (`model_rf.pkl`) belum ditemukan di repository GitHub Anda.")
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
                
                st.markdown("---")
                st.subheader("Hasil Analisis Sistem:")
                
                if prediction[0] == 1 or prediction[0] > 0:
                    st.error("⚠️ **Status: BERISIKO TINGGI (Potensi Keterlambatan Studi / Penurunan Performa)**")
                    st.warning("**Rekomendasi Tindakan:** Mahasiswa disarankan segera melakukan konseling akademik dengan dosen wali, mengevaluasi manajemen waktu belajar, serta mengelola tingkat stres.")
                else:
                    st.success("✅ **Status: AMAN (Berpotensi Lulus Tepat Waktu dengan Performa Baik)**")
                    st.info("**Rekomendasi Tindakan:** Pertahankan pola gaya hidup seimbang, tingkatkan konsistensi belajar, dan jaga kesehatan fisik serta mental.")
                
                # --- VISUALISASI GRAFIK BATANG UNTUK CONFIDENCE SCORE ---
                st.write("---")
                st.write("📊 **Visualisasi Tingkat Keyakinan Model (*Confidence Score Chart*):**")
                
                num_classes = prediction_proba.shape[1]
                col_names = [f"Kelas {i}" for i in range(num_classes)]
                
                # Membuat DataFrame untuk divisualisasikan
                chart_data = pd.DataFrame(prediction_proba, columns=col_names).T
                chart_data.columns = ["Probabilitas"]
                
                # Menampilkan Bar Chart interaktif bawaan Streamlit
                st.bar_chart(chart_data)
                
            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses prediksi: {e}")

elif menu == "Visualisasi & Analisis Data":
    st.subheader("📈 Visualisasi Statistik & Eksplorasi Fitur Dataset")
    st.write("Bagian ini menampilkan visualisasi grafik terpisah untuk parameter gaya hidup dan performa akademik mahasiswa.")
    
    # Dataset sampel untuk grafik
    chart_data = pd.DataFrame({
        'Kategori Risiko': ['Aman / Tepat Waktu', 'Berisiko Rendah', 'Berisiko Tinggi'],
        'Rata-Rata Jam Belajar': [5.5, 3.8, 2.1],
        'Rata-Rata GPA': [3.65, 3.05, 2.30]
    }).set_index('Kategori Risiko')
    
    # Membagi layout menjadi 2 kolom agar grafik tampil terpisah dan berdampingan
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("##### **Rata-Rata Jam Belajar per Hari**")
        # Hanya mengambil kolom Jam Belajar saja agar grafiknya berdiri sendiri
        st.bar_chart(chart_data[['Rata-Rata Jam Belajar']], color="#1f77b4")
        
    with col2:
        st.write("##### **Rata-Rata GPA (Indeks Prestasi)**")
        # Hanya mengambil kolom GPA saja agar grafiknya terpisah
        st.bar_chart(chart_data[['Rata-Rata GPA']], color="#ff7f0e")
    
    st.info("💡 Grafik di atas divisualisasikan secara dinamis untuk memberikan gambaran komparatif mengenai pola kebiasaan mahasiswa terhadap hasil akademik mereka.")

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
