import os
import streamlit as st
from groq import Groq
from kompetensi import KOMPETENSI_KESTA  # Impor modul kompetensi ringkas

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
    api_key_input = st.sidebar.text_input("Masukkan Groq API Key Anda:", type="password")
    if api_key_input:
        os.environ["GROQ_API_KEY"] = api_key_input

# 3. FORM INPUT DATA SISWA INTERAKTIF
st.header("📋 Input Data Siswa")
nama_siswa = st.text_input("Nama Lengkap Siswa:", placeholder="Contoh: Muhammad Reyhan")
pekerjaan_impian = st.text_input("Pekerjaan Impian / Target Karier:", placeholder="Contoh: Junior Backend Developer")

st.markdown("---")
st.subheader("📚 Transkrip Nilai Mata Pelajaran")
st.write("Masukkan nilai mata pelajaran sesuai rapor (Format angka desimal, contoh: 80.45):")

# Daftar 16 Mata Pelajaran Resmi SMK (Kurikulum Merdeka)
mapel_list = [
    ("Pendidikan Agama Islam dan Budi Pekerti", "PAIBP"),
    ("Pendidikan Pancasila", "Pancasila"),
    ("Bahasa Indonesia", "B_Indo"),
    ("Pendidikan Jasmani, Olahraga, dan Kesehatan", "PJOK"),
    ("Sejarah", "Sejarah"),
    ("Seni Budaya", "Seni_Budaya"),
    ("Matematika", "MTK"),
    ("Bahasa Inggris", "B_Inggris"),
    ("Informatika", "Informatika"),
    ("Projek Ilmu Pengetahuan Alam dan Sosial (IPAS)", "PIPAS"),
    ("Dasar-Dasar Program Keahlian", "Dasar_Keahlian"),
    ("Konsentrasi Keahlian", "Konsentrasi_Keahlian"),
    ("Projek Kreatif dan Kewirausahaan (PKK)", "PKK"),
    ("Praktik Kerja Lapangan (PKL)", "PKL"),
    ("Komputer Grafis", "Komputer_Grafis"),
    ("Bahasa dan Sastra Jawa", "B_Jawa")
]

# Tampilkan Widget Input Nilai dalam 2 Kolom Rapi
col1, col2 = st.columns(2)
dict_nilai_input = {}

for idx, (label_formal, key) in enumerate(mapel_list):
    # Selang-seling masukkan ke kolom 1 dan kolom 2
    target_col = col1 if idx % 2 == 0 else col2
    with target_col:
        val = st.number_input(
            label=f"{label_formal}:",
            min_value=0.0,
            max_value=100.0,
            value=80.0,
            step=0.1,
            format="%.2f",
            key=key
        )
        dict_nilai_input[label_formal] = val

st.markdown("---")

# 4. EKSEKUSI MULTI-AGENT PIPELINE
if st.button("🚀 Mulai Analisis Karier Saya", type="primary"):
    
    if not os.environ.get("GROQ_API_KEY"):
        st.error("Maaf, API Key Groq belum diatur. Silakan masukkan di sidebar atau Advanced Settings.")
    elif not nama_siswa or not pekerjaan_impian:
        st.warning("Mohon isi Nama Lengkap Siswa dan Pekerjaan Impian terlebih dahulu.")
    else:
        with st.spinner("Tim AI sedang berdiskusi menganalisis kompetensimu... Mohon tunggu..."):
            try:
                # Inisialisasi Groq Client sesuai Panduan Dokumentasi Resmi
                client = Groq(
                    api_key=os.environ.get("GROQ_API_KEY"),
                )
                
                MODEL_NAME = "llama-3.3-70b-versatile" 

                # Merangkai 16 nilai mata pelajaran menjadi teks terstruktur
                teks_nilai_mapel = ""
                for label_formal, nilai_val in dict_nilai_input.items():
                    teks_nilai_mapel += f"- {label_formal}: {nilai_val:.2f}\n"

                # Merangkai Rincian Standar Kompetensi dari modul kompetensi.py
                teks_kompetensi = ""
                for mata_pelajaran, daftar_poin in KOMPETENSI_KESTA.items():
                    teks_kompetensi += f"\n📌 {mata_pelajaran}:\n"
                    for poin in daftar_poin:
                        teks_kompetensi += f"  * {poin}\n"

                data_siswa_smk = f"""
                Nama Siswa: {nama_siswa}
                Transkrip Nilai Mata Pelajaran:
                {teks_nilai_mapel}

                Cakupan Standar Kompetensi Pembelajaran Kejuruan:
                {teks_kompetensi}
                """

                # ---- AGENT 1: Analis Rapor ----
                prompt_agent_1 = f"""Anda adalah Guru Produktif Senior SMK. Analisis data transkrip nilai siswa ini:
                {data_siswa_smk}

                Tugas Anda:
                1. Analisis seluruh nilai mata pelajaran.
                2. Khusus untuk mata pelajaran 'Dasar-Dasar Program Keahlian' dan 'Konsentrasi Keahlian', kaitkan capaian nilainya dengan cakupan standar kompetensi pembelajaran kejuruan yang disediakan.
                3. Jika nilainya tinggi (misal >= 80), uraikan poin-poin kompetensi yang telah dikuasai dengan baik. Jika kurang, sebutkan poin kompetensi yang masih perlu ditingkatkan.
                4. Berikan laporan ringkas dan terstruktur dalam format Markdown."""

                chat_completion_1 = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_agent_1}],
                    model=MODEL_NAME,
                )
                hasil_agent_1 = chat_completion_1.choices[0].message.content

                # ---- AGENT 2: HRD Matcher ----
                prompt_agent_2 = f"""Anda adalah HRD Profesional perusahaan IT. Baca profil kompetensi siswa ini:
                {hasil_agent_1}

                Tugas Anda untuk posisi pekerjaan impian '{pekerjaan_impian}':
                1. Jabarkan DAFTAR EKSPEKTASI UMUM INDUSTRI (persyaratan teknis/soft skills yang umum dicari pasar industri untuk posisi tersebut).
                2. Berikan perkiraan PERSENTASE KECOCOKAN (Match Rate dalam %) antara profil siswa dengan ekspektasi industri.
                3. Rincikan daftar GAP SKILL (kekurangan/kekosongan kompetensi siswa) secara detail.
                4. Berikan KETERANGAN / DISCLAIMER penting bahwa data ekspektasi ini bersifat umum (general), karena setiap perusahaan atau proses rekrutmen dapat memberikan kriteria dan kualifikasi yang berbeda-beda.
                
                Sajikan dalam format Markdown yang rapi."""
                
                chat_completion_2 = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_agent_2}],
                    model=MODEL_NAME,
                )
                hasil_agent_2 = chat_completion_2.choices[0].message.content

                # ---- AGENT 3: Mentor Belajar ----
                prompt_agent_3 = f"Anda adalah seorang Mentor IT / Instruksional Desainer Pembelajaran Digital. Berikut adalah daftar GAP SKILL siswa untuk posisi '{pekerjaan_impian}':\n{hasil_agent_2}\nTugas Anda adalah menyusun rekomendasi topik pembelajaran spesifik dan menyarankan kata kunci (keyword) pencarian video tutorial YouTube atau kursus online yang tepat untuk menambal masing-masing kekurangan tersebut."
                chat_completion_3 = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_agent_3}],
                    model=MODEL_NAME,
                )
                hasil_agent_3 = chat_completion_3.choices[0].message.content

                # ---- AGENT 4: Guru BK Virtual ----
                prompt_agent_4 = f"""Anda adalah seorang Guru Bimbingan Konseling (BK) yang sangat suportif di SMKN 1 Kasreman. Merangkum seluruh hasil analisis berikut menjadi satu Laporan Konseling Karier Akhir untuk siswa bernama {nama_siswa} yang mengincar posisi '{pekerjaan_impian}'.
                
                Data Rapor Siswa:
                {teks_nilai_mapel}
                
                Data Analisis Tim:
                - Agent 1 (Rapor & Standar Kompetensi): {hasil_agent_1}
                - Agent 2 (Kesiapan Kerja & Ekspektasi Industri): {hasil_agent_2}
                - Agent 3 (Rencana Belajar): {hasil_agent_3}
                
                Susun laporan dengan struktur:
                1. PENGANTAR
                2. POTRET KOMPETENSI ANDA (Wajib sertakan kembali tabel/daftar 16 nilai mata pelajaran input di atas secara rapi, lalu berikan rangkuman singkat kelebihan & kekurangan rapor berdasarkan pencapaian unit kompetensi).
                3. ANALISIS KESIAPAN DUNIA KERJA (Jabarkan Ekspektasi Umum Pasar Industri untuk posisi '{pekerjaan_impian}', Match Rate, Gap Skill, serta cantumkan Keterangan/Catatan bahwa standar rekrutmen bersifat general dan dapat bervariasi di tiap perusahaan).
                4. RENCANA AKSI MANDIRI
                5. KATA-KATA MOTIVASI PENUTUP."""
                
                chat_completion_4 = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_agent_4}],
                    model=MODEL_NAME,
                )
                hasil_akhir_bk = chat_completion_4.choices[0].message.content

                # Tampilkan hasil akhir ke layar web Streamlit
                st.success("Analisis Selesai!")
                st.markdown("---")
                st.header("📊 Hasil Analisis Konseling Karier")
                st.markdown(hasil_akhir_bk)

            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses data: {str(e)}")
