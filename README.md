# Early-Warning-System-Prediksi-Performa-Akademik-Tingkat-Stres-Mahasiswa

# 🎓 Early Warning System: Prediksi Performa Akademik & Tingkat Stres Mahasiswa

Proyek penelitian *machine learning* ini dikembangkan sebagai bagian dari tahapan pra-skripsi hingga skripsi. Sistem ini dirancang sebagai **Early Warning System (Sistem Peringatan Dini)** untuk mendeteksi secara proaktif tingkat stres dan potensi risiko akademik mahasiswa berdasarkan faktor gaya hidup sehari-hari serta pencapaian akademik (IPK).

---

## 🚀 Fitur Utama
1. **Data Preprocessing & Cleaning**: Pemeriksaan *missing values*, pemisahan fitur dan variabel target, serta *encoding* label kategorikal secara otomatis.
2. **Feature Selection (Random Forest Importance)**: Menganalisis atribut gaya hidup mana yang paling dominan memengaruhi kondisi atau performa mahasiswa melalui visualisasi tingkat kepentingan fitur (*feature importance*).
3. **Model Machine Learning Ensemble**: Mengimplementasikan dan membandingkan dua algoritma klasifikasi tangguh:
   - **Random Forest Classifier**
   - **XGBoost Classifier**
4. **Evaluasi Performa Komprehensif**: Pengukuran metrik evaluasi meliputi *Accuracy*, *Precision*, *Recall*, dan *F1-Score*, serta visualisasi *Confusion Matrix* berdampingan untuk perbandingan performa model.
5. **Interactive Dashboard (Streamlit)**: Antarmuka web interaktif yang memungkinkan pemantauan atau evaluasi mandiri bagi dosen pembimbing maupun mahasiswa.

---

## 📊 Atribut Dataset & Fitur
Fitur input ($X$) yang digunakan dalam analisis meliputi:
* `Study_Hours_Per_Day`: Durasi waktu belajar per hari (jam)
* `Extracurricular_Hours_Per_Day`: Durasi kegiatan ekstrakurikuler per hari (jam)
* `Sleep_Hours_Per_Day`: Durasi waktu tidur per hari (jam)
* `Social_Hours_Per_Day`: Durasi bersosialisasi per hari (jam)
* `Physical_Activity_Hours_Per_Day`: Durasi aktivitas fisik per hari (jam)
* `GPA`: Indeks Prestasi Kumulatif (IPK) terakhir

Variabel Target ($y$):
* `Stress_Level`: Tingkat stres atau status risiko akademik mahasiswa.

---

## 🛠️ Pustaka (Libraries) yang Digunakan
Proyek ini dibangun menggunakan bahasa pemograman Python dengan pustaka-pustaka berikut:
* **Manipulasi & Analisis Data**: `pandas`, `numpy`
* **Visualisasi Data**: `matplotlib`, `seaborn`
* **Machine Learning**: `scikit-learn` (Random Forest, *Train-Test Split*, *Label Encoder*, Metrik Evaluasi), `xgboost`
* **Penyimpanan Model**: `joblib`
* **Deployment / Web App**: `streamlit`

---

## ⚙️ Cara Menjalankan Proyek

### 1. Prasyarat & Instalasi Pustaka
Pastikan Anda telah memasang pustaka yang dibutuhkan dengan menjalankan perintah berikut di terminal atau lingkungan Google Colab:
```bash
pip install pandas numpy matplotlib seaborn streamlit joblib scikit-learn xgboost 
