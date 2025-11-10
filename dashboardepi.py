import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# KONFIGURASI DASHBOARD
# ==============================
st.set_page_config(page_title="Dashboard Epidemiologi", layout="wide")

# --- Custom CSS biar sidebar clean dan modern
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #003566;
        }
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] a, 
        [data-testid="stSidebar"] label {
            color: white !important;
        }
        /* Tombol umum */
        [data-testid="stSidebar"] .stButton>button {
            background-color: transparent;
            color: #ffffff;
            border: 1px solid #ffffff33;
            border-radius: 10px;
            width: 100%;
            text-align: left;
            font-weight: 500;
            margin-top: 5px;
        }
        [data-testid="stSidebar"] .stButton>button:hover {
            background-color: #ffc300;
            color: #ffffff;
            font-weight: 600;
            transform: scale(1.02);
        }
        /* Tombol Home khusus */
        .home-btn {
            background-color: #ffc300 !important;
            color: #000 !important;
            font-weight: 700 !important;
            border: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# ==============================
# SIDEBAR BUTTON NAVIGATION
# ==============================
menu = ["Home", "Deskripsi Penyakit", "Ukuran Epidemiologi", "Tren Kasus", "Tentang Penelitian"]

# default halaman
if "selected" not in st.session_state:
    st.session_state["selected"] = "Home"

# Tombol Home dibuat beda
if st.sidebar.button("🏠 Home", key="home", help="Kembali ke halaman utama", use_container_width=True):
    st.session_state["selected"] = "Home"
st.markdown(
    """<style>
        div[data-testid="stSidebar"] div[data-testid="stButton"]:has(button[kind="secondary"]) button {
            background-color: #ffc300 !important;
            color: #000 !important;
            font-weight: 700 !important;
            border: none !important;
        }
    </style>""",
    unsafe_allow_html=True
)

# Tombol lain
for item in menu[1:]:
    if st.sidebar.button(f"{'🫁' if 'Deskripsi Penyakit' in item else '🔗' if 'Ukuran Epidemiologi' in item else '📈' if 'Tren' in item else '🧾'} {item}",
                         key=item, use_container_width=True):
        st.session_state["selected"] = item

# Halaman aktif
selected = st.session_state["selected"]

# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_data():
    df = pd.read_excel("datatbc_jabar_2024.xlsx")
    df["prevalensi_per_100k"] = (df["kasus_2024"] / df["populasi_2024"]) * 100000
    return df

df = load_data()

# ==============================
# PAGE CONTENT
# ==============================
if selected == "Home":
    st.title("Dashboard Kasus TBC — Jawa Barat (2024)")
    st.caption("Sumber data: Dinkes Jawa Barat & BPS 2024 | Analisis per kabupaten/kota")

    # --- Load data
    @st.cache_data
    def load_data():
        df = pd.read_excel("datatbc_jabar_2024.xlsx")
        df["prevalensi_per_100k"] = (df["kasus_2024"] / df["populasi_2024"]) * 100000
        return df

    df = load_data()

    # --- Statistik ringkas
    total_kasus = int(df["kasus_2024"].sum())
    mean_kasus = round(df["kasus_2024"].mean(), 1)
    median_kasus = int(df["kasus_2024"].median())
    range_kasus = f"{df['kasus_2024'].min()} – {df['kasus_2024'].max()}"
    top10 = df.sort_values("kasus_2024", ascending=False).head(10)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Kasus TBC (2024)", f"{total_kasus:,}")
    col2.metric("Rata-rata Kasus per Kabupaten/Kota", f"{mean_kasus:,.0f}")
    col3.metric("Median Kasus", f"{median_kasus:,}")
    col4.metric("Rentang Kasus", range_kasus)

    st.markdown("---")

    # --- Top 10 kabupaten
    st.subheader("Top 10 Kabupaten/Kota dengan Kasus Tertinggi (2024)")
    st.dataframe(
        top10[["kabupaten", "kasus_2024", "populasi_2024", "prevalensi_per_100k"]]
        .rename(columns={
            "kabupaten": "Kabupaten/Kota",
            "kasus_2024": "Kasus 2024",
            "populasi_2024": "Populasi",
            "prevalensi_per_100k": "Prevalensi per 100k"
        }),
        hide_index=True,
        use_container_width=True
    )

    # --- Bar chart kasus per kabupaten
    st.subheader("Distribusi Kasus TBC per Kabupaten/Kota")
    fig_bar = px.bar(
        df.sort_values("kasus_2024", ascending=False),
        x="kabupaten", y="kasus_2024",
        labels={"kabupaten": "Kabupaten/Kota", "kasus_2024": "Jumlah Kasus"},
        title="Kasus TBC 2024 per Kabupaten/Kota",
        color="kasus_2024", color_continuous_scale="Reds"
    )
    fig_bar.update_layout(xaxis_tickangle=-45, height=450)
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- Histogram distribusi
    st.subheader(" Distribusi Kasus (Histogram)")
    fig_hist = px.histogram(
        df, x="kasus_2024",
        nbins=10,
        title="Sebaran Jumlah Kasus antar Kabupaten/Kota",
        labels={"kasus_2024": "Kasus per Kabupaten/Kota"},
        color_discrete_sequence=["#2E86C1"]
    )
    fig_hist.update_layout(height=400)
    st.plotly_chart(fig_hist, use_container_width=True)

    # PETA PREVALENSI TBC
    import streamlit as st
    from PIL import Image

    st.subheader("Peta Persebaran Prevalensi TBC di Jawa Barat (2024)")

    # Load gambar
    image = Image.open("leafletshp.png")

    # Tampilkan di dashboard
    st.image(image, caption="Peta Prevalensi TBC Jawa Barat 2024", use_container_width=True)


elif selected == "Deskripsi Penyakit":
    st.title("Deskripsi Penyakit TBC")
    st.markdown("""
    ### Definisi
    **Tuberkulosis (TBC)** adalah penyakit **kronis menular** yang disebabkan oleh bakteri *Mycobacterium tuberculosis*. Penyakit ini dapat menyerang berbagai organ tubuh, namun **paru-paru** merupakan organ yang paling sering terinfeksi (*tuberkulosis paru*). Di tingkat global, TBC masih menjadi salah satu **penyakit menular dengan angka kejadian tinggi** dan tantangan besar bagi kesehatan masyarakat.

    ---

    ### Mekanisme Penularan
    TBC umumnya **menular melalui udara**. Ketika penderita TBC aktif **batuk atau bersin**, mereka dapat memercikkan **lendir atau dahak** yang mengandung bakteri *Mycobacterium tuberculosis* ke udara. Orang lain yang menghirup udara tersebut dapat tertular dan berpotensi mengembangkan penyakit ini.

    ---

    ### Gejala Umum
    **1. Gejala TBC aktif di paru-paru:**
    - Batuk parah selama ≥ 3 minggu  
    - Nyeri di dada  
    - Batuk darah atau dahak bercampur darah  

    **2. Gejala umum TBC aktif:**
    - Kelelahan dan lemah tubuh  
    - Penurunan berat badan  
    - Hilang nafsu makan  
    - Demam dan menggigil  
    - Keringat berlebih di malam hari  

    **3. Gejala TBC di luar paru-paru (tergantung organ):**
    - Pembengkakan kelenjar getah bening pada TBC kelenjar  
    - Kencing berdarah pada TBC ginjal 
    - Nyeri punggung pada TBC tulang belakang 
    - Sakit kepala dan kejang pada TBC otak
    - Sakit perut hebat pada TBC usus 

    ---

    ### Faktor Risiko
    - Daya tahan tubuh yang rendah  
    - Lingkungan padat dan ventilasi buruk  
    - Kontak erat dengan penderita TBC aktif  
    - Kondisi medis lainnya seperti HIV/AIDS 
    - Kondisi gizi buruk atau kelaparan  
    - Penggunaan obat-obatan tertentu yang menekan sistem imun  
    - Kebersihan diri dan sanitasi yang kurang baik

    ---

    ### Referensi
    1. Pusat Nasional Penanggulangan TBC, “UMUM_PNPK revisi” (2021), … [link](https://www.tbindonesia.or.id/wp-content/uploads/2021/06/UMUM_PNPK_revisi.pdf)  
    2. Jurnal Global Health Science, “…” (2021) … [link](https://jurnal.globalhealthsciencegroup.com/index.php/JPPP/article/download/1270/998/)  
    3. Alodokter, “Proses Terjadinya Penularan TBC” … [link](https://www.alodokter.com/proses-terjadinya-penularan-tbc)  
    4. CDC, “Signs & Symptoms of Tuberculosis” … [link](https://www.cdc.gov/tb/signs-symptoms/index.html)  
    5. Halodoc, “Faktor Risiko Alami TBC yang Terjadi di Usia Muda” … [link](https://www.halodoc.com/artikel/faktor-risiko-alami-tbc-yang-terjadi-di-usia-muda?srsltid=AfmBOormrXZ4m42UjtNNopy_JPmNehIrRjeq0ZUmVQCrCHnB2ioOwVi0)  

    """)


elif selected == "Ukuran Epidemiologi":
    st.title("📊 Ukuran Epidemiologi — Frekuensi & Asosiasi")

    # ==============================
    # 1️⃣ PREVALENSI (Ukuran Frekuensi)
    # ==============================
    st.subheader(" Ukuran Frekuensi — Prevalensi")

    st.markdown("""
    **Definisi:**  
    Prevalensi menggambarkan proporsi individu dalam populasi yang menderita penyakit pada suatu waktu tertentu.  
    Dalam konteks ini, dihitung sebagai jumlah kasus TBC per 100.000 penduduk pada tahun 2024 di Jawa Barat.

    **Rumus:**  
    """)
    st.latex(r"\text{Prevalensi} = \frac{\text{Kasus TBC (baru+lama)}}{\text{Populasi}}")

    # --- Hitung prevalensi provinsi secara keseluruhan
    total_kasus = df["kasus_2024"].sum()
    total_populasi = df["populasi_2024"].sum()
    prevalensi_rasio = total_kasus / total_populasi
    prevalensi_per_100k = prevalensi_rasio * 100000
    prevalensi_persen = prevalensi_rasio * 100

    # --- Tampilkan hasil
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Prevalensi TBC (per 100.000 penduduk)", f"{prevalensi_per_100k:,.2f}")
    with col2:
        st.metric("Prevalensi TBC (%)", f"{prevalensi_persen:.4f}%")

    # --- Dataframe prevalensi per kabupaten/kota
    st.dataframe(
        df[["kabupaten", "kasus_2024", "populasi_2024", "prevalensi_per_100k"]]
        .rename(columns={
            "kabupaten": "Kabupaten/Kota",
            "kasus_2024": "Kasus TBC",
            "populasi_2024": "Populasi",
            "prevalensi_per_100k": "Prevalensi per 100k"
        }),
        hide_index=True,
        use_container_width=True
    )

    # --- Interpretasi singkat prevalensi
    st.markdown(f"""
    ### Interpretasi Hasil
    Nilai prevalensi TBC di Provinsi Jawa Barat tahun 2024 adalah **{prevalensi_per_100k:,.2f} per 100.000 penduduk**
    atau setara dengan **{prevalensi_persen:.4f}%** dari total populasi. Artinya, dari setiap 100.000 penduduk, terdapat sekitar **{prevalensi_per_100k/100000*100:.4f}%**
    yang tercatat sebagai penderita TBC. Nilai ini menunjukkan bahwa beban penyakit TBC di Jawa Barat masih cukup tinggi,
    sehingga perlu dilakukan pemantauan dan intervensi kesehatan masyarakat secara berkelanjutan.
    """)

    st.markdown("---")

    # ==============================
    # 2️⃣ UKURAN ASOSIASI
    # ==============================
    st.subheader(" Ukuran Asosiasi — PR dan POR")

    st.markdown("""
    **Pengertian Singkat:**  
    Ukuran asosiasi digunakan untuk menggambarkan hubungan antara **paparan (exposure)** dan **penyakit (outcome)**.  
    Dalam konteks ini, paparan yang dianalisis adalah **kepadatan penduduk** terhadap **kejadian TBC**.

    - **Prevalence Ratio (PR):** membandingkan proporsi penderita TBC antara wilayah dengan kepadatan tinggi dan rendah.  
    - **Prevalence Odds Ratio (POR):** membandingkan peluang (odds) terjadinya TBC antara dua kelompok tersebut.
    """)

    # --- Tabel 2x2: Kepadatan Penduduk vs TBC
    data_asosiasi = {
        "Kepadatan Wilayah": ["Tinggi (X > Rata-rata)", "Rendah (X < Rata-rata)", "Total"],
        "TBC (+)": [67968, 156830, 224798],
        "TBC (−)": [10406262, 39714130, 50120392],
        "Total": [10474230, 39870960, 50345190]
    }

    df_asosiasi = pd.DataFrame(data_asosiasi)
    st.dataframe(df_asosiasi, hide_index=True, use_container_width=True)

    # --- Ringkasan hasil ukuran asosiasi (pakai hasil hitungan yang sudah diberikan)
    st.markdown("### Ringkasan Hasil Ukuran Asosiasi")

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Prevalence Ratio (PR)", value="1.65")
    with col2:
        st.metric(label="Prevalence Odds Ratio (POR)", value="1.65")

    # --- Rumus matematis
    st.markdown("**Rumus yang digunakan:**")
    st.latex(r"PR = \frac{\frac{a}{a + b}}{\frac{c}{c + d}}")
    st.latex(r"POR = \frac{a \times d}{b \times c}")

    # --- Interpretasi hasil
    st.markdown("""
    ### Interpretasi Hasil
    Hasil analisis menunjukkan bahwa nilai Prevalence Ratio (PR) sebesar 1,65, yang berarti penduduk yang tinggal di wilayah dengan kepadatan tinggi memiliki risiko sekitar 1,65 kali lebih besar untuk terpapar Tuberkulosis (TBC) dibandingkan dengan penduduk di wilayah yang kurang padat. Nilai **Prevalence Odds Ratio (POR)** juga sebesar **1,65**, menunjukkan bahwa peluang terjadinya TBC pada wilayah berpenduduk padat sekitar **1,65 kali lebih tinggi** dibandingkan wilayah berpenduduk jarang. Nilai PR dan POR yang lebih besar dari satu menandakan adanya **hubungan positif antara kepadatan penduduk dan risiko TBC**, di mana peningkatan kepadatan cenderung diikuti oleh meningkatnya kasus TBC.
    """)

elif selected == "Tren Kasus":
    st.title("Tren Kasus TBC — Jawa Barat (2022–2024)")
    st.caption("Sumber data: Dinkes Jawa Barat | Jumlah kasus TBC per tahun di tingkat kabupaten/kota")

    # --- Load Data Tren (clean version)
    @st.cache_data
    def load_trend_data():
        import re

        df_trend_wide = pd.read_excel("kasus_tbc_jabar.xlsx", header=0)
        df_trend_wide.columns = df_trend_wide.columns.map(lambda x: str(x).strip())

        # Rename kolom kabupaten
        for candidate in ["Kabupaten/Kota", "Kabupaten", "kabupaten", "Kota/Kabupaten"]:
            if candidate in df_trend_wide.columns:
                df_trend_wide = df_trend_wide.rename(columns={candidate: "kabupaten"})
                break

        # Deteksi kolom tahun seperti "Tahun 2022"
        tahun_cols = [c for c in df_trend_wide.columns if re.search(r"\d{4}", c)]

        # Mapping kolom → angka tahun (ekstrak 4 digit)
        col_to_year = {c: re.search(r"(\d{4})", c).group(1) for c in tahun_cols}

        # Long format
        df_trend_long = pd.melt(
            df_trend_wide,
            id_vars=["kabupaten"],
            value_vars=list(col_to_year.keys()),
            var_name="tahun_label",
            value_name="kasus"
        )

        # Ambil angka tahunnya, pastikan tipe string
        df_trend_long["tahun"] = df_trend_long["tahun_label"].str.extract(r"(\d{4})")
        df_trend_long["tahun"] = df_trend_long["tahun"].astype(str)
        df_trend_long["kabupaten"] = df_trend_long["kabupaten"].astype(str).str.strip()
        df_trend_long["kasus"] = pd.to_numeric(df_trend_long["kasus"], errors="coerce")

        df_trend_long = df_trend_long.sort_values(["kabupaten", "tahun"]).reset_index(drop=True)
        return df_trend_wide, df_trend_long, col_to_year

    # Load data
    df_trend_wide, df_trend_long, col_to_year = load_trend_data()

    # --- Dropdown filter kabupaten
    kab_filter = st.selectbox(
        "Pilih Kabupaten/Kota untuk melihat tren spesifik:",
        ["Semua Kabupaten/Kota"] + list(df_trend_wide["kabupaten"].unique())
    )

    # --- Total provinsi per tahun
    total_per_year = df_trend_long.groupby("tahun", as_index=False)["kasus"].sum()
    total_per_year["tahun"] = total_per_year["tahun"].astype(int)  # pastikan integer, bukan float
    total_per_year = total_per_year.sort_values("tahun")

    st.subheader(" Total Kasus TBC Provinsi Jawa Barat per Tahun")
    fig_total = px.line(
        total_per_year, x="tahun", y="kasus", markers=True,
        title="Total Kasus TBC (2022–2024)",
        labels={"tahun": "Tahun", "kasus": "Jumlah Kasus"},
        line_shape="linear"
    )
    fig_total.update_traces(line_color="#e63946", line_width=3)
    fig_total.update_layout(
        height=400,
        xaxis=dict(tickmode="linear", tick0=2022, dtick=1)  # tampilkan tahun bulat
    )
    st.plotly_chart(fig_total, use_container_width=True)

    # --- Grafik tren per kabupaten
    st.subheader(" Tren Kasus per Kabupaten/Kota (2022–2024)")

    if kab_filter == "Semua Kabupaten/Kota":
        fig_kab = px.line(
            df_trend_long,
            x="tahun", y="kasus", color="kabupaten",
            labels={"tahun": "Tahun", "kasus": "Jumlah Kasus", "kabupaten": "Kabupaten/Kota"},
            title="Perubahan Kasus TBC per Kabupaten/Kota",
            line_shape="linear"
        )
    else:
        df_filtered = df_trend_long[df_trend_long["kabupaten"] == kab_filter]
        fig_kab = px.line(
            df_filtered,
            x="tahun", y="kasus", color="kabupaten", markers=True,
            title=f"Tren Kasus TBC — {kab_filter}",
            labels={"tahun": "Tahun", "kasus": "Jumlah Kasus"}
        )

    fig_kab.update_layout(
        legend_title_text="Kabupaten/Kota",
        height=550,
        xaxis=dict(tickmode="linear", tick0=2022, dtick=1)
    )
    st.plotly_chart(fig_kab, use_container_width=True)

    # --- Persentase perubahan 2022–2024
    st.subheader("Persentase Perubahan Kasus (2022 → 2024)")

    # Cari kolom asli untuk 2022–2024
    import numpy as np
    col_2022 = next((orig for orig, y in col_to_year.items() if y == "2022"), None)
    col_2023 = next((orig for orig, y in col_to_year.items() if y == "2023"), None)
    col_2024 = next((orig for orig, y in col_to_year.items() if y == "2024"), None)

    # Numerik
    for c in [col_2022, col_2023, col_2024]:
        if c and c in df_trend_wide.columns:
            df_trend_wide[c] = pd.to_numeric(df_trend_wide[c], errors="coerce")

    # Persentase perubahan 
    df_trend_wide["% Perubahan (2022–2024)"] = np.where(
        df_trend_wide[col_2022] > 0,
        (df_trend_wide[col_2024] - df_trend_wide[col_2022]) / df_trend_wide[col_2022] * 100,
        np.nan
    )

    df_rank = df_trend_wide.sort_values("% Perubahan (2022–2024)", ascending=False)
    rename_map = {
        col_2022: "Tahun 2022",
        col_2023: "Tahun 2023",
        col_2024: "Tahun 2024"
    }

    st.dataframe(
        df_rank[["kabupaten", col_2022, col_2023, col_2024, "% Perubahan (2022–2024)"]]
        .rename(columns=rename_map),
        hide_index=True,
        use_container_width=True
    )

    

elif selected == "Tentang Penelitian":
    st.title("ℹ️ Tentang Penelitian")

    st.markdown("""
    ## Dashboard Kasus TBC — Jawa Barat (2024)

    **Judul:**  
    *Analisis Epidemiologi Kasus Tuberkulosis di Provinsi Jawa Barat Tahun 2024*

    **Disusun oleh:**  
    - 👩‍🎓 Ghaitsa Shafiyyah  
    - 👩‍🎓 Gina Kustiana  
    - 👨‍🎓 Charles Joshua Nathaniel Waruwu  

    **Dosen Pembimbing:** Dr. I Gede Nyoman Mindra Jaya, M.Si  
    **Institusi:** Universitas Padjadjaran  
    **Tahun:** 2025  

    ---

    ### Tujuan Penelitian
    Penelitian ini bertujuan untuk menyajikan **analisis deskriptif** kasus Tuberkulosis (TBC) di tingkat kabupaten/kota
    Provinsi Jawa Barat, termasuk ukuran frekuensi penyakit (*prevalensi per 100.000 penduduk*), ukur
    serta tren kasus selama tahun **2022–2024**.

    ---

    ### Sumber Data
    - **Dinas Kesehatan Provinsi Jawa Barat** — Data kasus TBC tahun 2022–2024  
    - **BPS Kabupaten Bandung** — Jumlah Penduduk menurut Kabupaten/Kota di Provinsi Jawa Barat (2024) 
    ---

    ### Metodologi Singkat
    - **Desain penelitian:** Cross-sectional
    - **Unit analisis:** Kabupaten/Kota  
    - **Periode analisis:** Tahun 2024  
    
    ---
                
    ### Acknowledgement
    Penyusunan dashboard ini turut dibantu oleh **ChatGPT (OpenAI, model GPT-5)** dalam proses penulisan kode dan perancangan visualisasi. Seluruh hasil akhir telah diperiksa, disunting, dan disesuaikan oleh penulis.
                
    ---

    ### Hak Cipta & Lisensi
    Dashboard ini dibuat untuk keperluan **akademik dan edukasi**.  
    Seluruh data bersumber dari **publikasi resmi instansi pemerintah**.  

    © 2025 — *Ghaitsa Shafiyyah, Gina Kustiana, Charles Joshua Nathaniel Waruwu*.  
    
    
    
    """)