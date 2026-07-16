import os
import streamlit as st
from groq import Groq

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Smart Career Path SMKN 1 Kasreman", page_icon="🎓", layout="centered")

st.title("🎓 Smart Career Path")
st.subheader("Asisten Konseling Karier Virtual SMKN 1 Kasreman")
st.write("Sistem AI Multi-Agent untuk analisis kompetensi nilai kejuruan dan kesiapan kerja siswa.")
st.markdown("---")

# 2. PENGATURAN API KEY GROQ
if "GROQ_API_KEY" in os.environ:
    st.sidebar.success("🔑 Groq API Key terdeteksi dengan aman di Sistem.")
else:
    # Backup input box jika lupa disetel di cloud (opsional)
    api_key_input = st.sidebar.text_input("Masukkan Groq API Key Anda:", type="password")
    if api_key_input:
        os.environ["GROQ_API_KEY"] = api_key_input

# 3. FORM INPUT DATA SISWA INTERAKTIF
st.header("📋 Input Data Siswa")
nama_siswa = st.text_input("Nama Lengkap Siswa:", placeholder="Contoh: Muhammad Reyhan")
pekerjaan_impian = st.text_input("Pekerjaan Impian / Posisi Industri yang Diincar:", placeholder="Contoh: Junior Web Developer (Fokus Backend)")

st.write("Masukkan Nilai Mata Pelajaran Produktif/Kejuruan (Skala 1-100):")

col1, col2 = st.columns(2)
with col1:
    nilai_web = st.number_input("Pemrograman Web & Perangkat Bergerak:", min_value=0, max_value=100, value=80)
    nilai_uml = st.number_input("Pemodelan Perangkat Lunak (UML):", min_value=0, max_value=100, value=80)
with col2:
    nilai_db = st.number_input("Basis Data (SQL):", min_value=0, max_value=100, value=80)
    nilai_design = st.number_input("Desain Grafis / UI-UX Dasar:", min_value=0, max_value=100, value=80)

nilai_pkk = st.number_input("Produk Kreatif & Kewirausahaan (PKK):", min_value=0, max_value=100, value=80)

# 4. EKSEKUSI MULTI-AGENT PIPELINE
if st.button("🚀 Mulai Analisis Karier Saya", type="primary"):
    
    if not os.environ.get("GROQ_API_KEY"):
        st.error("Maaf, API Key Groq belum diatur. Silakan masukkan di sidebar atau Advanced Settings.")
    elif not nama_siswa or not pekerjaan_impian:
        st.warning("Mohon isi Nama Siswa dan Pekerjaan Impian terlebih dahulu.")
    else:
        with st.spinner("Tim AI sedang berdiskusi menganalisis kompetensimu... Mohon tunggu..."):
            try:
                # Inisialisasi Groq Client sesuai Panduan Dokumentasi Resmi
                client = Groq(
                    api_key=os.environ.get("GROQ_API_KEY"),
                )
                
                MODEL_NAME = "llama-3.3-70b-versatile" 

                data_siswa_smk = f"""
                Nama Siswa: {nama_siswa}
                Nilai Mata Pelajaran Produktif:
                - Pemrograman Web dan Perangkat Bergerak: {nilai_web}
                - Pemodelan Perangkat Lunak (UML): {nilai_uml}
                - Basis Data: {nilai_db}
                - Desain Grafis / UI-UX Dasar: {nilai_design}
                - Produk Kreatif dan Kewirausahaan (PKK): {nilai_pkk}
                """

                # ---- AGENT 1: Analis Rapor ----
                prompt_agent_1 = f"Anda adalah Guru Produktif Senior SMK. Analisis data nilai ini:\n{data_siswa_smk}\nTentukan secara spesifik KEUNGGULAN utama kompetensi siswa dan KELEMAHAN/kekurangan kompetensi siswa. Berikan laporan ringkas Markdown."
                chat_completion_1 = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt_agent_1,
                        }
                    ],
                    model=MODEL_NAME,
                )
                hasil_agent_1 = chat_completion_1.choices[0].message.content

                # ---- AGENT 2: HRD Matcher ----
                prompt_agent_2 = f"Anda adalah HRD Profesional perusahaan IT. Baca profil kompetensi siswa ini:\n{hasil_agent_1}\nBandingkan profil tersebut dengan ekspektasi umum industri untuk posisi: '{pekerjaan_impian}'. Berikan perkiraan Persentase Kecocokan (Match Rate dalam %) dan daftar GAP SKILL secara detail."
                chat_completion_2 = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt_agent_2,
                        }
                    ],
                    model=MODEL_NAME,
                )
                hasil_agent_2 = chat_completion_2.choices[0].message.content

                # ---- AGENT 3: Mentor Belajar ----
                prompt_agent_3 = f"Anda adalah seorang Mentor IT / Instruksional Desainer Pembelajaran Digital. Berikut adalah daftar GAP SKILL siswa untuk posisi '{pekerjaan_impian}':\n{hasil_agent_2}\nTugas Anda adalah menyusun rekomendasi topik pembelajaran spesifik dan menyarankan kata kunci (keyword) pencarian video tutorial YouTube atau kursus online yang tepat untuk menambal masing-masing kekurangan tersebut."
                chat_completion_3 = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt_agent_3,
                        }
                    ],
                    model=MODEL_NAME,
                )
                hasil_agent_3 = chat_completion_3.choices[0].message.content

                # ---- AGENT 4: Guru BK Virtual ----
                prompt_agent_4 = f"""Anda adalah seorang Guru Bimbingan Konseling (BK) yang sangat suportif di SMKN 1 Kasreman. Merangkum seluruh hasil analisis berikut menjadi satu Laporan Konseling Karier Akhir untuk siswa bernama {nama_siswa} yang mengincar posisi '{pekerjaan_impian}'.
                Data:
                - Agent 1: {hasil_agent_1}
                - Agent 2: {hasil_agent_2}
                - Agent 3: {hasil_agent_3}
                Susun laporan dengan struktur: 1. PENGANTAR, 2. POTRET KOMPETENSI ANDA, 3. ANALISIS KESIAPAN DUNIA KERJA, 4. RENCANA AKSI MANDIRI, 5. KATA-KATA MOTIVASI PENUTUP."""
                
                chat_completion_4 = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt_agent_4,
                        }
                    ],
                    model=MODEL_NAME,
                )
                hasil_akhir_bk = chat_completion_4.choices[0].message.content

                # Tampilkan hasil akhir ke layar web
                st.success("Analisis Selesai!")
                st.markdown("---")
                st.header("📊 Hasil Analisis Konseling Karier")
                st.markdown(hasil_akhir_bk)

            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses data: {str(e)}")
