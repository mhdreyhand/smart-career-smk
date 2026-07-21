import os
import streamlit as st
from groq import Groq
from kompetensi import KOMPETENSI_KESTA # Impor modul ringkas tadi

# ... [Bagian Konfigurasi Streamlit & Input Data Siswa tetap sama] ...

# ==========================================
# 🚀 EKSEKUSI MULTI-AGENT PIPELINE
# ==========================================
if st.button("🚀 Mulai Analisis Karier Saya", type="primary"):
    
    if not os.environ.get("GROQ_API_KEY"):
        st.error("Maaf, API Key Groq belum diatur.")
    elif not nama_siswa or not pekerjaan_impian:
        st.warning("Mohon isi Nama Lengkap Siswa dan Pekerjaan Impian terlebih dahulu.")
    else:
        with st.spinner("Tim AI sedang berdiskusi menganalisis kompetensimu... Mohon tunggu..."):
            try:
                client = Groq(
                    api_key=os.environ.get("GROQ_API_KEY"),
                )
                
                MODEL_NAME = "llama-3.3-70b-versatile" 

                # 1. Rangkai Nilai Mata Pelajaran
                teks_nilai_mapel = ""
                for label_formal, nilai_val in dict_nilai_input.items():
                    teks_nilai_mapel += f"- {label_formal}: {nilai_val}\n"

                # 2. Rangkai Rincian Kompetensi Ringkas
                teks_kompetensi = ""
                for mata_pelajaran, daftar_poin in KOMPETENSI_KESTA.items():
                    teks_kompetensi += f"\n📌 {mata_pelajaran}:\n"
                    for poin in daftar_poin:
                        teks_kompetensi += f"  * {poin}\n"

                # 3. Gabungkan ke Data Siswa
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

                # ... [Proses Agent 2, Agent 3, dan Agent 4 tetap sama] ...
