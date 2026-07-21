import os
import streamlit as st
from groq import Groq
from mapel import MAPEL_PER_JURUSAN
from kompetensi import KOMPETENSI_PER_JURUSAN

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

# Dropdown Pilihan Jurusan
jurusan_pilihan = st.selectbox(
    "Pilih Jurusan / Program Keahlian:",
    options=list(MAPEL_PER_JURUSAN.keys()),
    help="Form nilai mata pelajaran akan menyesuaikan dengan jurusan yang dipilih."
)

pekerjaan_impian = st.text_input(
    "Pekerjaan Impian / Target Karier:", 
    placeholder="Contoh: Junior Backend Developer (TKJ) atau Junior Accountant / Tax Officer (AKL)"
)

st.markdown("---")
st.subheader(f"📚 Transkrip Nilai - Jurusan {jurusan_pilihan}")
st.write("Masukkan nilai mata pelajaran sesuai rapor (Format angka desimal, contoh: 80.45):")

# Ambil daftar mapel dinamis sesuai jurusan yang dipilih
current_mapel_list = MAPEL_PER_JURUSAN[jurusan_pilihan]

# Tampilkan Widget Input Nilai dalam 2 Kolom Rapi
col1, col2 = st.columns(2)
dict_nilai_input = {}

for idx, (label_formal, key) in enumerate(current_mapel_list):
    target_col = col1 if idx % 2 == 0 else col2
    with target_col:
        val = st.number_input(
            label=f"{label_formal}:",
            min_value=0.0,
            max_value=100.0,
            value=80.0,
            step=0.1,
            format="%.2f",
            key=f"{jurusan_pilihan}_{key}"  # Key unik per jurusan
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
                client = Groq(
                    api_key=os.environ.get("GROQ_API_KEY"),
                )
                
                MODEL_NAME = "llama-3.3-70b-versatile" 

                # Merangkai nilai mata pelajaran yang diinputkan
                teks_nilai_mapel = ""
                for label_formal, nilai_val in dict_nilai_input.items():
                    teks_nilai_mapel += f"- {label_formal}: {nilai_val:.2f}\n"

                # Ambil modul kompetensi yang sesuai dengan jurusan pilihan siswa
                kompetensi_jurusan = KOMPETENSI_PER_JURUSAN[jurusan_pilihan]
                
                teks_kompetensi = ""
                for mata_pelajaran, daftar_poin in kompetensi_jurusan.items():
                    teks_kompetensi += f"\n📌 {mata_pelajaran}:\n"
                    for poin in daftar_poin:
                        teks_kompetensi += f"  * {poin}\n"

                data_siswa_smk = f"""
                Nama Siswa: {nama_siswa}
                Jurusan / Program Keahlian: {jurusan_pilihan}
                
                Transkrip Nilai Mata Pelajaran:
                {teks_nilai_mapel}

                Cakupan Standar Kompetensi Pembelajaran Kejuruan & Praktik Lapangan ({jurusan_pilihan}):
                {teks_kompetensi}
                """

                # ---- AGENT 1: Analis Rapor ----
                prompt_agent_1 = f"""Anda adalah Guru Produktif Senior SMK untuk Jurusan {jurusan_pilihan}. Analisis data transkrip nilai siswa ini:
                {data_siswa_smk}

                Tugas Anda:
                1. Analisis seluruh nilai mata pelajaran.
                2. Khusus mata pelajaran kejuruan produktif dan Praktik Kerja Lapangan (PKL), kaitkan capaian nilainya dengan cakupan standar kompetensi yang disediakan untuk jurusan {jurusan_pilihan}.
                3. Jika nilainya tinggi (misal >= 80), uraikan poin-poin kompetensi yang telah dikuasai dengan baik. Jika kurang, sebutkan poin kompetensi yang masih perlu ditingkatkan.
                4. Berikan laporan ringkas dan terstruktur dalam format Markdown."""

                chat_completion_1 = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_agent_1}],
                    model=MODEL_NAME,
                )
                hasil_agent_1 = chat_completion_1.choices[0].message.content

                # ---- AGENT 2: HRD Matcher ----
                prompt_agent_2 = f"""Anda adalah HRD Profesional di industri yang relevan dengan posisi '{pekerjaan_impian}' dan latar belakang jurusan '{jurusan_pilihan}'. Baca profil kompetensi siswa ini:
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
                prompt_agent_3 = f"Anda adalah seorang Mentor Profesional / Instruksional Desainer Pembelajaran Digital. Berikut adalah daftar GAP SKILL siswa jurusan '{jurusan_pilihan}' untuk posisi '{pekerjaan_impian}':\n{hasil_agent_2}\nTugas Anda adalah menyusun rekomendasi topik pembelajaran spesifik dan menyarankan kata kunci (keyword) pencarian video tutorial YouTube atau kursus online yang tepat untuk menambal masing-masing kekurangan tersebut."
                chat_completion_3 = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_agent_3}],
                    model=MODEL_NAME,
                )
                hasil_agent_3 = chat_completion_3.choices[0].message.content

                # ---- AGENT 4: Guru BK Virtual ----
                prompt_agent_4 = f"""Anda adalah seorang Guru Bimbingan Konseling (BK) yang sangat suportif di SMKN 1 Kasreman. Merangkum seluruh hasil analisis berikut menjadi satu Laporan Konseling Karier Akhir untuk siswa bernama {nama_siswa} (Jurusan {jurusan_pilihan}) yang mengincar posisi '{pekerjaan_impian}'.
                
                Data Rapor Siswa:
                {teks_nilai_mapel}
                
                Data Analisis Tim:
                - Agent 1 (Rapor & Standar Kompetensi): {hasil_agent_1}
                - Agent 2 (Kesiapan Kerja & Ekspektasi Industri): {hasil_agent_2}
                - Agent 3 (Rencana Belajar): {hasil_agent_3}
                
                Susun laporan dengan struktur:
                1. PENGANTAR
                2. POTRET KOMPETENSI ANDA (Wajib sertakan kembali tabel/daftar 16 nilai mata pelajaran input di atas secara rapi, lalu berikan rangkuman singkat kelebihan & kekurangan rapor berdasarkan pencapaian unit kompetensi kejuruan dan PKL jurusan {jurusan_pilihan}).
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
