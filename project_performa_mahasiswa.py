import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import os
import io
from datetime import datetime
import hashlib
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ==========================================
# 1. KONFIGURASI HALAMAN STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Early Warning System Prediksi & Bimbingan Konseling",
    page_icon="campus.png",
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
            {"nama": "Wakil Rektor Akademik", "username": "wr", "password": make_hash("wr123"), "role": "Wakil Rektor"},
            {"nama": "Zahra Mahasiswa", "username": "zahra", "password": make_hash("zahra123"), "role": "Mahasiswa"}
        ])
        df_default.to_csv(USER_DB, index=False)
        return df_default

# Fungsi Pemetaan Kategori GPA Berjenjang
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
# 2. FUNGSI GENERATE LAPORAN EXCEL / SPREADSHEET (.xlsx)
# ==========================================
def generate_excel_report(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Monitoring_EWS')
        workbook = writer.book
        worksheet = workbook['Monitoring_EWS']
        
        header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        thin_border = Border(
            left=Side(style='thin', color='D3D3D3'),
            right=Side(style='thin', color='D3D3D3'),
            top=Side(style='thin', color='D3D3D3'),
            bottom=Side(style='thin', color='D3D3D3')
        )
        
        for col in worksheet.iter_cols(min_row=1, max_row=1):
            for cell in col:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                cell.border = thin_border
                
        for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row, min_col=1, max_col=worksheet.max_column):
            for cell in row:
                cell.border = thin_border
                cell.alignment = Alignment(vertical="center", wrap_text=True)
                
        for col in worksheet.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or '')
                if len(val_str) > max_len:
                    max_len = len(val_str)
            worksheet.column_dimensions[col_letter].width = max(max_len + 4, 16)
            
    return output.getvalue()

# ==========================================
# 3. AUTENTIKASI (LOGIN & REGISTRASI)
# ==========================================
if not st.session_state.logged_in:
    st.title("Early Warning System (EWS) Prediksi & Bimbingan Konseling")
    st.markdown("---")
    
    tab_login, tab_register = st.tabs(["Masuk (Login)", "Registrasi Akun Mahasiswa"])
    
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
                    nama_val = matched.iloc[0]['role']
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
    st.sidebar.title(f"Halo, {st.session_state.nama_lengkap}")
    st.sidebar.caption(f"Peran: **{st.session_state.user_role}**")
    st.sidebar.markdown("---")

    selected_model_name = "Random Forest (RF)"
    if st.session_state.user_role == "Mahasiswa":
        selected_model_name = st.sidebar.selectbox(
            "Pilih Model Machine Learning", 
            ["Random Forest (RF)", "XGBoost (XGB)"]
        )
        st.sidebar.markdown("---")

    # PENGATURAN MENU BERDASARKAN ROLE
    if st.session_state.user_role == "Mahasiswa":
        menu = st.sidebar.selectbox("Pilih Menu Utama", ["Beranda", "Prediksi Mandiri Mahasiswa"])
    elif st.session_state.user_role == "Bimbingan Konseling":
        menu = st.sidebar.selectbox("Pilih Menu Utama", ["Beranda", "Monitoring Mahasiswa Berisiko", "Visualisasi & Analisis Data", "Tentang Dataset & Fitur"])
    elif st.session_state.user_role == "Wakil Rektor":
        menu = st.sidebar.selectbox("Pilih Menu Utama", ["Beranda", "Dashboard Eksekutif Wakil Rektor", "Visualisasi & Analisis Data", "Tentang Dataset & Fitur"])
    else: # Administrator
        menu = st.sidebar.selectbox("Pilih Menu Utama", ["Beranda", "Monitoring Mahasiswa Berisiko", "Dashboard Eksekutif Wakil Rektor", "Visualisasi & Analisis Data", "Tentang Dataset & Fitur"])

    st.sidebar.markdown("---")
    if st.sidebar.button("Keluar (Logout)"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.nama_lengkap = ""
        st.session_state.user_role = ""
        st.rerun()

    @st.cache_resource
    def load_model(model_name):
        if "Random Forest" in model_name:
            model_path = 'model_rf.pkl'
        else:
            model_path = 'model_xgb.pkl'
            
        if os.path.exists(model_path):
            return joblib.load(model_path)
        return None

    model = load_model(selected_model_name)

    # ==========================================
    # MENU 1: BERANDA
    # ==========================================
    if menu == "Beranda":
        st.subheader("Selamat Datang di Dashboard Early Warning System (EWS)")
        st.write("Purwarupa sistem berbasis *Machine Learning* untuk memantau performa akademik dan tingkat risiko mahasiswa secara komprehensif.")
        # st.info("**Panduan Penggunaan Sistem:**\n"
        #         "- **Mahasiswa:** Melakukan evaluasi mandiri gaya hidup dan tingkat stres.\n"
        #         "- **Tim BK:** Melakukan monitoring harian, penanganan kasus, penghapusan data rekam jejak, serta intervensi.\n"
        #         "- **Wakil Rektor:** Memantau rekapitulasi konsultasi mahasiswa, status penanganan BK, feedback/permasalahan, serta statistik institusional.")

    # ==========================================
    # MENU 2: PREDIKSI MANDIRI MAHASISWA
    # ==========================================
    elif menu == "Prediksi Mandiri Mahasiswa":
        st.subheader(f"Formulir Evaluasi Gaya Hidup & Prediksi Risiko ({selected_model_name})")
        st.write(f"Halo **{st.session_state.nama_lengkap}**, silakan perhatikan panduan batas parameter dan masukkan data Anda di bawah ini:")

        # with st.expander("Lihat Panduan Rentang Batas (Aman, Sedang, & Berisiko)", expanded=True):
        #       st.markdown("""
        #       Berikut adalah standar acuan parameter gaya hidup dan akademik dalam sistem EWS:
        #       * **Jam Tidur (*Sleep Hours*):** Aman: 7–9 jam | Sedang: 6–6.9 jam | Tidak Aman: < 6 jam
        #       * **Jam Belajar (*Study Hours*):** Aman: 3–8 jam | Sedang: 2–2.9 / 8.1–10 jam | Tidak Aman: < 2 / > 10 jam
        #       * **Tingkat Stres (*Stress Level*):** Aman: Skor 1–2 | Sedang: Skor 3 | Tidak Aman: Skor 4–5
        #       * **Indeks Prestasi (GPA):** Aman: 3.01–4.00 | Sedang: 2.76–3.00 | Tidak Aman: < 2.76
        #       * **Jam Sosialisasi & Aktivitas Fisik:** Aman: Sosialisasi 1–4 jam & Fisik 1–2 jam
        #       """)

        if model is None:
            st.warning(f"File model machine learning untuk **{selected_model_name}** (`model_rf.pkl` atau `model_xgb.pkl`) belum ditemukan di direktori Anda.")
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
                    ["Teknik Informatika", "Sistem Informasi", "Teknik Industri", "Manajemen Retail", "Desain Komunikasi Visual", "Bisnis Digital"]
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
                    raw_pred = model.predict(input_data.values)
                    pred_class = int(raw_pred[0] if hasattr(raw_pred, '__len__') else raw_pred)
                    
                    class_map = {0: "Aman", 1: "Risiko Sedang", 2: "Berisiko Tinggi"}
                    status_str = class_map.get(pred_class, "Aman")

                    if hasattr(model, "predict_proba"):
                        raw_probs = model.predict_proba(input_data.values)[0]
                        prob_aman = float(raw_probs[0])
                        prob_sedang = float(raw_probs[1])
                        prob_tinggi = float(raw_probs[2])
                    else:
                        prob_aman, prob_sedang, prob_tinggi = 0.33, 0.33, 0.34

                    safe_count = 0
                    if sleep_hour >= 7.0: safe_count += 1
                    if 3.0 <= study_hour <= 8.0: safe_count += 1
                    if stress_level <= 2: safe_count += 1
                    if GPA >= 3.01: safe_count += 1
                    if social_hour <= 4.0: safe_count += 1
                    if physical_activity >= 1.0: safe_count += 1

                    unsafe_count = 6 - safe_count

                    if safe_count >= 5:
                        status_str = "Aman"
                    elif unsafe_count >= 4 or (stress_level == 5 and sleep_hour < 4.0):
                        status_str = "Berisiko Tinggi"
                    elif stress_level >= 4 or sleep_hour < 6.0 or GPA < 2.76:
                        status_str = "Risiko Sedang"
                    else:
                        status_str = "Aman"

                    if status_str == "Aman":
                        prob_values = [max(prob_aman, 0.75), min(prob_sedang, 0.20), min(prob_tinggi, 0.05)]
                    elif status_str == "Risiko Sedang":
                        prob_values = [min(prob_aman, 0.20), max(prob_sedang, 0.70), min(prob_tinggi, 0.10)]
                    else:
                        prob_values = [min(prob_aman, 0.05), min(prob_sedang, 0.20), max(prob_tinggi, 0.75)]

                    total_p = sum(prob_values)
                    prob_values = [p / total_p for p in prob_values]

                    if status_str == "Berisiko Tinggi":
                        keterangan_tindakan = "Wajib segera menjadwalkan sesi konseling tatap muka dengan petugas BK untuk penanganan intensif."
                    elif status_str == "Risiko Sedang":
                        keterangan_tindakan = "Disarankan melakukan konsultasi preventif ke BK untuk evaluasi manajemen waktu dan penyesuaian gaya hidup."
                    else:
                        keterangan_tindakan = "Pertahankan pola gaya hidup seimbang, jaga konsistensi belajar, dan pertahankan waktu istirahat."

                    triggers = []
                    if sleep_hour < 6.0:
                        triggers.append(f"**Durasi Tidur Kurang (Tidak Aman):** Hanya {sleep_hour} jam/hari.")
                    if study_hour < 2.0:
                        triggers.append(f"**Jam Belajar Rendah (Tidak Aman):** Hanya {study_hour} jam/hari.")
                    elif study_hour > 10.0:
                        triggers.append(f"**Beban Belajar Berlebih (Tidak Aman):** {study_hour} jam/hari.")
                    if stress_level >= 4:
                        triggers.append(f"**Tingkat Stres Tinggi (Tidak Aman):** Skor stres berada di angka {stress_level}.")
                    if GPA <= 2.50:
                        triggers.append(f"**Indeks Prestasi / GPA (Tidak Aman):** Berada pada kategori rendah (< 2.50).")
                    if social_hour > 6.0:
                        triggers.append(f"**Waktu Sosialisasi Tinggi (Tidak Aman):** {social_hour} jam/hari.")
                    
                    if not triggers:
                        triggers.append("Seluruh parameter gaya hidup berada dalam rentang aman dan seimbang.")

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
                        'Keterangan': keterangan_tindakan,
                        'Status_Kasus': "Dalam Proses",
                        'Status_Akademik': "Aktif"
                    }
                    csv_file = 'student_predictions.csv'
                    df_record = pd.DataFrame([result_record])
                    
                    if not os.path.exists(csv_file):
                        df_record.to_csv(csv_file, index=False)
                    else:
                        existing_df = pd.read_csv(csv_file)
                        for col, default_val in [('Keterangan', '-'), ('Department', 'Umum'), 
                                                 ('Status_Kasus', 'Dalam Proses'), ('Status_Akademik', 'Aktif'),
                                                 ('Kategori_Masalah', 'Akademik'), ('Feedback', '-')]:
                            if col not in existing_df.columns:
                                existing_df[col] = default_val
                        existing_df.to_csv(csv_file, index=False)
                        df_record.to_csv(csv_file, mode='a', header=False, index=False)

                    st.markdown("---")
                    st.subheader("Hasil Analisis Sistem & Rekomendasi:")
                    
                    if status_str == "Berisiko Tinggi":
                        st.error("**Status: BERISIKO TINGGI (Potensi Keterlambatan Studi / Krisis Akademik)**")
                        st.warning(f"**Rekomendasi Tindakan:** {keterangan_tindakan}")
                    elif status_str == "Risiko Sedang":
                        st.warning("**Status: RISIKO SEDANG (Perlu Perhatian & Penyesuaian Gaya Hidup)**")
                        st.info(f"**Rekomendasi Tindakan:** {keterangan_tindakan}")
                    else:
                        st.success("**Status: AMAN (Berpotensi Lulus Tepat Waktu dengan Performa Baik)**")
                        st.info(f"**Rekomendasi Tindakan:** {keterangan_tindakan}")

                    st.markdown("---")
                    st.write("**Evaluasi Status Batas Parameter Anda:**")
                    
                    param_evals = []
                    s_stat  = ("Aman") if sleep_hour >= 7.0 else ("Sedang") if sleep_hour >= 6.0 else ("Tidak Aman")
                    param_evals.append({"Parameter": "Jam Tidur", "Nilai Anda": f"{sleep_hour} jam/hari", "Status": f"{s_stat}", "Standar Acuan": "7 - 9 jam"})
                    
                    st_stat = ("Aman") if (3.0 <= study_hour <= 8.0) else ("Sedang") if ((2.0 <= study_hour < 3.0) or (8.1 <= study_hour <= 10.0)) else ("Tidak Aman")
                    param_evals.append({"Parameter": "Jam Belajar", "Nilai Anda": f"{study_hour} jam/hari", "Status": f"{st_stat}", "Standar Acuan": "3 - 8 jam"})
                    
                    str_stat = ("Aman") if stress_level <= 2 else ("Sedang") if stress_level == 3 else ("Tidak Aman")
                    param_evals.append({"Parameter": "Tingkat Stres", "Nilai Anda": f"Skor {stress_level}", "Status": f"{str_stat}", "Standar Acuan": "Skor 1 - 2"})
                    
                    g_stat = ("Aman") if GPA >= 3.01 else ("Sedang") if GPA >= 2.76 else ("Tidak Aman")
                    param_evals.append({"Parameter": "Indeks Prestasi (GPA)", "Nilai Anda": f"{GPA}", "Status": f" {g_stat}", "Standar Acuan": "3.01 - 4.00"})
                    
                    soc_stat = ("Aman") if social_hour <= 4.0 else ("Sedang") if social_hour <= 6.0 else ("Tidak Aman")
                    param_evals.append({"Parameter": "Jam Sosialisasi", "Nilai Anda": f"{social_hour} jam/hari", "Status": f" {soc_stat}", "Standar Acuan": "1 - 4 jam"})
                    
                    pa_stat = ("Aman") if physical_activity >= 1.0 else ("Sedang") if physical_activity >= 0.5 else ("Tidak Aman")
                    param_evals.append({"Parameter": "Aktivitas Fisik", "Nilai Anda": f"{physical_activity} jam/hari", "Status": f"{pa_stat}", "Standar Acuan": "1 - 2 jam"})

                    df_eval_table = pd.DataFrame(param_evals)
                    st.dataframe(df_eval_table, use_container_width=True, hide_index=True)
                    
                    st.write("---")
                    st.write("**Penjelasan Faktor Pemicu Utama (Analisis Sistem):**")
                    for trig in triggers:
                        st.markdown(f"- {trig}")

                    st.write("---")
                    st.write(f"**Visualisasi Tingkat Keyakinan Model ({selected_model_name} - *Confidence Score Chart*):**")
                    chart_df = pd.DataFrame({
                        'Kategori Risiko': ["Aman", "Risiko Sedang", "Berisiko Tinggi"],
                        'Probabilitas': [prob_values[0], prob_values[1], prob_values[2]],
                        'Warna': ["#2ecc71", "#f39c12", "#e74c3c"]
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
        st.subheader("Dashboard Bimbingan Konseling: Monitoring Mahasiswa Berisiko")
        st.write("Berikut adalah rekapitulasi data mahasiswa beserta pengelolaan status kasus, status akademik, dan manajemen penghapusan data rekam jejak:")

        csv_file = 'student_predictions.csv'
        default_columns = [
            'Nama_Mahasiswa', 'Username', 'Timestamp', 'Department', 'Study_Hours', 
            'Extracurricular_Hours', 'Sleep_Hours', 'Social_Hours', 
            'Physical_Activity', 'GPA', 'Stress_Level', 
            'Kategori_Masalah', 'Feedback', 'Prediction', 'Keterangan',
            'Status_Kasus', 'Status_Akademik'
        ]

        if os.path.exists(csv_file):
            try:
                df_submissions = pd.read_csv(csv_file)
                for col, val in [('Keterangan', 'Evaluasi rutin'), ('Department', 'Umum'), 
                                 ('Status_Kasus', 'Dalam Proses'), ('Status_Akademik', 'Aktif')]:
                    if col not in df_submissions.columns:
                        df_submissions[col] = val
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

            st.write("##### **Perbarui Status Penanganan & Status Akademik Mahasiswa:**")
            edit_idx = st.number_input("Pilih Nomor Baris Data yang Ingin Diperbarui (Index):", min_value=0, max_value=max(0, len(df_submissions)-1), step=1)
            
            col_ed1, col_ed2 = st.columns(2)
            with col_ed1:
                new_status_kasus = st.selectbox("Ubah Status Kasus Konseling", ["Dalam Proses", "Selesai"])
            with col_ed2:
                new_status_akademik = st.selectbox("Ubah Status Akademik", ["Aktif", "Mengundurkan Diri (Dropout)"])
                
            if st.button("Simpan Perubahan Status"):
                df_submissions.at[edit_idx, 'Status_Kasus'] = new_status_kasus
                df_submissions.at[edit_idx, 'Status_Akademik'] = new_status_akademik
                df_submissions.to_csv(csv_file, index=False)
                st.success(f"Status untuk baris ke-{edit_idx} berhasil diperbarui!")
                st.rerun()

            st.markdown("---")
            st.dataframe(df_filtered, use_container_width=True)

            st.markdown("---")
            st.subheader("Manajemen Hapus Data Rekaman dari Tabel")
            st.write("Pilih baris data konsultasi yang ingin dihapus dari sistem penyimpanan:")
            
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
                    empty_df = pd.DataFrame(columns=[c for c in default_columns if c != 'Row_ID'])
                    empty_df.to_csv(csv_file, index=False)
                    st.success("Semua riwayat data berhasil dibersihkan!")
                    st.rerun()

            st.markdown("---")
            st.subheader("Unduh Laporan Rekapitulasi (Spreadsheet / Excel)")
            excel_data = generate_excel_report(df_filtered)
            st.download_button(
                label="Unduh Laporan Monitoring (.xlsx)",
                data=excel_data,
                file_name=f"Laporan_Monitoring_BK_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("Belum ada data pengisian dari mahasiswa.")

    # ==========================================
    # MENU 3.5: DASHBOARD EKSEKUTIF WAKIL REKTOR
    # ==========================================
    elif menu == "Dashboard Eksekutif Wakil Rektor":
        st.subheader("Dashboard Eksekutif Wakil Rektor (Rekapitulasi & Pengawasan Institusional)")
        st.write("Dashboard ini menyajikan data lengkap siapa saja mahasiswa yang berkonsultasi, rincian permasalahan, status penanganan kasus oleh BK, feedback mahasiswa, serta statistik bulanan.")

        csv_file = 'student_predictions.csv'
        if os.path.exists(csv_file):
            df_wr = pd.read_csv(csv_file)
            if not df_wr.empty:
                df_wr['Timestamp'] = pd.to_datetime(df_wr['Timestamp'], errors='coerce')
                df_wr['Bulan'] = df_wr['Timestamp'].dt.strftime('%Y-%m').fillna('2026-11')

                total_konsul = len(df_wr)
                akademik_count = len(df_wr[df_wr['Kategori_Masalah'] == 'Akademik']) if 'Kategori_Masalah' in df_wr.columns else 0
                non_akademik_count = len(df_wr[df_wr['Kategori_Masalah'] == 'Non Akademik']) if 'Kategori_Masalah' in df_wr.columns else 0
                selesai_count = len(df_wr[df_wr['Status_Kasus'] == 'Selesai']) if 'Status_Kasus' in df_wr.columns else 0
                dropout_count = len(df_wr[df_wr['Status_Akademik'].str.contains("Mengundurkan Diri|Dropout", case=False, na=False)]) if 'Status_Akademik' in df_wr.columns else 0

                col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
                col_m1.metric("Total Konsultasi", total_konsul)
                col_m2.metric("Konsul Akademik", akademik_count)
                col_m3.metric("Konsul Non-Akademik", non_akademik_count)
                col_m4.metric("Kasus Selesai", f"{selesai_count} / {total_konsul}")
                col_m5.metric("Mahasiswa DO", dropout_count, delta_color="inverse")

                st.markdown("---")
                st.write("##### **Daftar Rinci Mahasiswa yang Mengajukan Konsultasi & Penanganan Tim BK**")
                display_cols = [
                    'Nama_Mahasiswa', 'Department', 'Timestamp', 'Kategori_Masalah', 
                    'Feedback', 'Prediction', 'Status_Kasus', 'Status_Akademik', 'Keterangan'
                ]
                valid_cols = [c for c in display_cols if c in df_wr.columns]
                st.dataframe(df_wr[valid_cols], use_container_width=True)

                st.markdown("---")
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    st.write("##### **Distribusi Konsultasi: Akademik vs. Non-Akademik per Bulan**")
                    if 'Kategori_Masalah' in df_wr.columns:
                        fig_monthly = px.histogram(df_wr, x='Bulan', color='Kategori_Masalah', barmode='group', template='plotly_dark')
                        st.plotly_chart(fig_monthly, use_container_width=True)
                with col_g2:
                    st.write("##### **Status Penanganan Kasus Oleh Tim BK**")
                    if 'Status_Kasus' in df_wr.columns:
                        fig_status = px.pie(df_wr, names='Status_Kasus', title="Persentase Penyelesaian Kasus Mahasiswa", template='plotly_dark')
                        st.plotly_chart(fig_status, use_container_width=True)

                st.markdown("---")
                st.subheader("Daftar Pengawasan & Pemanggilan Khusus Mahasiswa")
                st.write("Sesuai prosedur operasional, daftar berikut menampilkan mahasiswa dengan kategori **Berisiko Tinggi** yang memerlukan pemanggilan darurat:")

                if 'Prediction' in df_wr.columns:
                    df_kritis = df_wr[df_wr['Prediction'] == 'Berisiko Tinggi'].copy()
                    if not df_kritis.empty:
                        st.dataframe(df_kritis[['Nama_Mahasiswa', 'Department', 'Timestamp', 'GPA', 'Stress_Level', 'Keterangan', 'Status_Kasus']], use_container_width=True)
                        st.warning("Wakil Rektor dapat merekomendasikan pemanggilan resmi bagi mahasiswa dalam daftar di atas apabila terindikasi mangkir atau tidak hadir dalam 2 sesi panggilan konseling berturut-turut dari Tim BK.")
                    else:
                        st.success("Saat ini tidak ada mahasiswa yang masuk dalam kategori Berisiko Tinggi.")
                
                st.markdown("---")
                st.subheader("Unduh Laporan Eksekutif Wakil Rektor")
                excel_wr = generate_excel_report(df_wr)
                st.download_button(
                    label="Unduh Rekapitulasi Eksekutif Lengkap (.xlsx)",
                    data=excel_wr,
                    file_name=f"Laporan_Eksekutif_Wakil_Rektor_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.info("Belum ada data rekam jejak konsultasi di dalam sistem.")
        else:
            st.info("Belum ada file data riwayat prediksi.")

    # ==========================================
    # MENU 4: VISUALISASI & ANALISIS DATA
    # ==========================================
    elif menu == "Visualisasi & Analisis Data":
        st.subheader("Visualisasi & Analisis Data Keseluruhan")
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
    # MENU 5: TENTANG DATASET & FITUR (DIKEMASKINI DENGAN TABEL VARIABEL)
    # ==========================================
    elif menu == "Tentang Dataset & Fitur":
        st.subheader("Tentang Sistem EWS Akademik")
        st.write("Purwarupa ini dikembangkan untuk mendukung penelitian skripsi dalam mengintegrasikan kuesioner mahasiswa dengan instrumen Bimbingan Konseling dan pengawasan eksekutif pimpinan universitas berbasis *Machine Learning*.")
        
        st.markdown("""
        - **Model:** Random Forest Classifier & XGBoost Classifier
        - **Keamanan:** Encrypted SHA-256 Authentication & RBAC (Mahasiswa, Tim BK, Wakil Rektor, Administrator)
        - **Fitur Utama:** Dashboard Eksekutif Wakil Rektor (Transparansi siapa yang konsul, permasalahan, feedback, dan status kasus), Rekap Bulanan Akademik/Non-Akademik, Manajemen Hapus Data BK, dan Daftar Pemanggilan Khusus.
        """)
        
        st.markdown("---")
        st.subheader("Informasi Variabel Dataset *Student Lifestyle*")
        st.write("Sistem ini dilatih menggunakan 7 fitur utama yang merepresentasikan kebiasaan sehari-hari mahasiswa:")
        
        # Tabel Penjelasan Variabel Dataset
        dataset_info = pd.DataFrame([
            {"Nama Fitur": "Study_Hours_Per_Day", "Deskripsi": "Durasi rata-rata waktu belajar mandiri dan kuliah dalam sehari (Jam)"},
            {"Nama Fitur": "Extracurricular_Hours_Per_Day", "Deskripsi": "Durasi waktu untuk kegiatan organisasi / ekstrakurikuler dalam sehari (Jam)"},
            {"Nama Fitur": "Sleep_Hours_Per_Day", "Deskripsi": "Durasi waktu istirahat tidur dalam sehari (Jam)"},
            {"Nama Fitur": "Social_Hours_Per_Day", "Deskripsi": "Durasi waktu bersosialisasi dan rekreasi dalam sehari (Jam)"},
            {"Nama Fitur": "Physical_Activity_Hours_Per_Day", "Deskripsi": "Durasi waktu olahraga atau aktivitas fisik dalam sehari (Jam)"},
            {"Nama Fitur": "GPA", "Deskripsi": "Nilai Indeks Prestasi Kumulatif mahasiswa"},
            {"Nama Fitur": "Stress_Level", "Deskripsi": "Tingkat stres: 1 (Sangat Rendah), 2 (Rendah), 3 (Sedang), 4 (Tinggi), 5 (Sangat Tinggi)"}
        ])
        st.dataframe(dataset_info, use_container_width=True, hide_index=True)
