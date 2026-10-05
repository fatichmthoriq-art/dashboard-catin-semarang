"""
Dashboard Sistem Informasi Calon Pengantin (Catin)
Capaian Intervensi PANSOS/DASHAT - Disdalduk KB Kota Semarang, 2025

Laporan MBKM - Inez Ajeng Puspita (25000123120031)
Peminatan Biostatistik dan Kependudukan, FKM Universitas Diponegoro

Cara menjalankan:
    pip install -r requirements.txt
    streamlit run app.py
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

# ---------------------------------------------------------------------------
# 1. PENGATURAN HALAMAN DAN WARNA
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Dashboard Catin Kota Semarang", layout="wide")

WARNA = {
    "utama": "#2a78d6",      # biru - seri tunggal
    "sorot": "#eb6834",      # oranye - penanda prioritas / di atas median
    "abu": "#a8a7a1",        # pembanding (target, kategori lain)
    "naik": "#0ca30c",       # status baik
    "tetap": "#fab219",      # status waspada
    "turun": "#d03b3b",      # status kritis
    "teks": "#52514e",
    "grid": "#e1e0d9",
}
FONT = dict(family="system-ui, -apple-system, Segoe UI, sans-serif", size=13, color=WARNA["teks"])


def gaya_grafik(fig, tinggi=460):
    """Tampilan grafik yang seragam: latar bersih, grid tipis, tanpa garis tepi."""
    fig.update_layout(
        height=tinggi, font=FONT, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=20, t=30, b=10), hoverlabel=dict(font_size=13),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(showgrid=True, gridcolor=WARNA["grid"], zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    return fig


def angka(x, d=0):
    """Format angka gaya Indonesia: 206.916 dan 7,29."""
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


# ---------------------------------------------------------------------------
# 2. DATA
#    Sumber: Tabel 3 Jumlah PUS menurut umur kawin pertama (Pendataan Keluarga
#    s.d. 2025) dan Laporan Intervensi PANSOS/DASHAT 2025, Disdalduk KB Kota
#    Semarang. Ganti bagian ini jika data diperbarui.
# ---------------------------------------------------------------------------
@st.cache_data
def muat_data():
    pus = pd.DataFrame([
        # kode, kecamatan, PUS, perempuan<19, laki-laki<25
        ("01", "Semarang Tengah", 4143, 327, 1227),
        ("02", "Semarang Utara", 14036, 751, 7888),
        ("03", "Semarang Timur", 5864, 595, 2089),
        ("04", "Gayamsari", 7687, 802, 2807),
        ("05", "Genuk", 19962, 1715, 9575),
        ("06", "Pedurungan", 23631, 1479, 6709),
        ("07", "Semarang Selatan", 5926, 353, 2082),
        ("08", "Candisari", 8648, 564, 2762),
        ("09", "Gajahmungkur", 6301, 403, 1762),
        ("10", "Tembalang", 28054, 1923, 10664),
        ("11", "Banyumanik", 16136, 766, 5968),
        ("12", "Gunungpati", 14077, 1592, 5358),
        ("13", "Semarang Barat", 16735, 952, 6626),
        ("14", "Mijen", 11722, 1219, 4382),
        ("15", "Ngaliyan", 19680, 1241, 7961),
        ("16", "Tugu", 4314, 395, 1501),
    ], columns=["kode", "kecamatan", "pus", "p_lt19", "l_lt25"])

    catin = pd.DataFrame([
        # kecamatan, jumlah terintervensi, %BB naik, %BB tetap, %BB turun
        ("Banyumanik", 15, 46.7, 33.3, 20.0), ("Candisari", 36, 50.0, 44.4, 5.6),
        ("Gajahmungkur", 17, 94.1, 5.9, 0.0), ("Gayamsari", 35, 94.3, 5.7, 0.0),
        ("Genuk", 84, 66.7, 21.4, 11.9), ("Gunungpati", 71, 81.7, 15.5, 2.8),
        ("Mijen", 21, 85.7, 9.5, 4.8), ("Ngaliyan", 48, 93.8, 4.2, 2.1),
        ("Pedurungan", 17, 76.5, 23.5, 0.0), ("Semarang Barat", 38, 81.6, 18.4, 0.0),
        ("Semarang Selatan", 17, 82.4, 17.6, 0.0), ("Semarang Tengah", 73, 83.6, 6.8, 9.6),
        ("Semarang Timur", 73, 78.1, 20.5, 1.4), ("Semarang Utara", 21, 71.4, 0.0, 28.6),
        ("Tembalang", 52, 88.5, 9.6, 1.9), ("Tugu", 26, 88.5, 7.7, 3.8),
    ], columns=["kecamatan", "n_catin", "pct_naik", "pct_tetap", "pct_turun"])

    df = pus.merge(catin, on="kecamatan")
    # rekonstruksi jumlah dari persentase (total kota: 511 / 98 / 35)
    df["bb_naik"] = (df.n_catin * df.pct_naik / 100).round().astype(int)
    df["bb_turun"] = (df.n_catin * df.pct_turun / 100).round().astype(int)
    df["bb_tetap"] = df.n_catin - df.bb_naik - df.bb_turun
    df["pct_p_lt19"] = df.p_lt19 / df.pus * 100
    df["pct_l_lt25"] = df.l_lt25 / df.pus * 100
    df["rasio"] = df.n_catin / df.p_lt19 * 100  # catin terintervensi per 100 PUS kawin < 19 th

    # kuadran prioritas berbasis median kota (dihitung dari 16 kecamatan)
    med_dini, med_rasio = df.pct_p_lt19.median(), df.rasio.median()
    def kuadran(r):
        tinggi = r.pct_p_lt19 > med_dini
        rendah = r.rasio <= med_rasio
        if tinggi and rendah:
            return "I - Prioritas"
        if tinggi:
            return "II - Pertahankan"
        if rendah:
            return "III - Pantau"
        return "IV - Evaluasi efektivitas"
    df["kuadran"] = df.apply(kuadran, axis=1)

    tren = pd.DataFrame({"tahun": ["2024", "2025"], "target": [410, 610], "realisasi": [422, 644]})
    return df, tren, med_dini, med_rasio


df_all, tren, MED_DINI, MED_RASIO = muat_data()

# ---------------------------------------------------------------------------
# 3. FILTER (sidebar)
# ---------------------------------------------------------------------------
st.sidebar.header("Filter")
pilih_kec = st.sidebar.multiselect(
    "Kecamatan", sorted(df_all.kecamatan), default=sorted(df_all.kecamatan),
    help="Kosongkan lalu pilih kecamatan tertentu untuk fokus.")
pilih_kuad = st.sidebar.multiselect(
    "Kuadran prioritas", sorted(df_all.kuadran.unique()), default=sorted(df_all.kuadran.unique()))
df = df_all[df_all.kecamatan.isin(pilih_kec) & df_all.kuadran.isin(pilih_kuad)].copy()

st.sidebar.markdown("---")
st.sidebar.caption(
    "Sumber: Pendataan Keluarga s.d. 2025 dan Laporan Intervensi PANSOS/DASHAT 2025, "
    "Disdalduk KB Kota Semarang. Diolah oleh Inez Ajeng Puspita (MBKM FKM UNDIP).")

if df.empty:
    st.warning("Tidak ada kecamatan yang cocok dengan filter. Ubah pilihan di sidebar.")
    st.stop()

# ---------------------------------------------------------------------------
# 4. JUDUL DAN INDIKATOR UTAMA
# ---------------------------------------------------------------------------
st.title("Dashboard Calon Pengantin dan Intervensi PANSOS/DASHAT")
st.caption(f"Kota Semarang, 2025 · menampilkan {len(df)} dari 16 kecamatan")

tot_pus, tot_dini = df.pus.sum(), df.p_lt19.sum()
tot_catin, tot_naik = df.n_catin.sum(), df.bb_naik.sum()
k1, k2, k3, k4 = st.columns(4)
k1.metric("Pasangan Usia Subur (PUS)", angka(tot_pus))
k2.metric("Perempuan kawin pertama < 19 th", f"{angka(tot_dini / tot_pus * 100, 2)}%",
          help=f"{angka(tot_dini)} PUS")
if len(df) == 16:
    k3.metric("Catin terintervensi", angka(tot_catin), f"{angka(tot_catin / 610 * 100, 1)}% dari target 610")
else:
    k3.metric("Catin terintervensi", angka(tot_catin))
k4.metric("Catin dengan BB naik", f"{angka(tot_naik / tot_catin * 100, 1)}%",
          help=f"{angka(tot_naik)} catin (laporan resmi membulatkan 79,4%)")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Umur kawin pertama", "Capaian intervensi", "Kuadran prioritas", "Uji statistik", "Data"])

# ---------------------------------------------------------------------------
# TAB 1 - PROFIL UMUR KAWIN PERTAMA
# ---------------------------------------------------------------------------
with tab1:
    st.subheader("Persentase PUS perempuan dengan umur kawin pertama < 19 tahun")
    d = df.sort_values("pct_p_lt19")
    warna = [WARNA["sorot"] if v > MED_DINI else WARNA["utama"] for v in d.pct_p_lt19]
    fig = go.Figure(go.Bar(
        x=d.pct_p_lt19, y=d.kecamatan, orientation="h", marker_color=warna,
        text=[angka(v, 2) + "%" for v in d.pct_p_lt19], textposition="outside",
        customdata=d[["p_lt19", "pus"]],
        hovertemplate="<b>%{y}</b><br>%{x:.2f}%<br>%{customdata[0]:,} dari %{customdata[1]:,} PUS<extra></extra>"))
    fig.add_vline(x=7.29, line_dash="dash", line_color=WARNA["teks"],
                  annotation_text="Kota 7,29%", annotation_position="top")
    fig.update_xaxes(title="% PUS perempuan kawin pertama < 19 tahun", range=[0, 13])
    st.plotly_chart(gaya_grafik(fig, 520), use_container_width=True)
    st.caption(f"Oranye = di atas median kota ({angka(MED_DINI, 2)}%). "
               "Arahkan kursor ke batang untuk melihat jumlah absolut.")

    c1, c2 = st.columns(2)
    top_abs = df.nlargest(5, "p_lt19")[["kecamatan", "p_lt19"]]
    c1.markdown("**Jumlah absolut terbanyak**")
    c1.dataframe(top_abs.rename(columns={"kecamatan": "Kecamatan", "p_lt19": "Perempuan kawin < 19 th"}),
                 hide_index=True, use_container_width=True)
    top_l = df.nlargest(5, "pct_l_lt25")[["kecamatan", "pct_l_lt25"]].round(2)
    c2.markdown("**Laki-laki kawin pertama < 25 tahun (%) tertinggi**")
    c2.dataframe(top_l.rename(columns={"kecamatan": "Kecamatan", "pct_l_lt25": "%"}),
                 hide_index=True, use_container_width=True)

# ---------------------------------------------------------------------------
# TAB 2 - CAPAIAN INTERVENSI
# ---------------------------------------------------------------------------
with tab2:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Target dan realisasi")
        fig = go.Figure()
        fig.add_bar(name="Target", x=tren.tahun, y=tren.target, marker_color=WARNA["abu"],
                    text=tren.target, textposition="outside")
        fig.add_bar(name="Realisasi", x=tren.tahun, y=tren.realisasi, marker_color=WARNA["utama"],
                    text=tren.realisasi, textposition="outside")
        fig.update_layout(barmode="group", bargap=0.35, bargroupgap=0.08)
        fig.update_yaxes(title="Jumlah catin", showgrid=True, gridcolor=WARNA["grid"], range=[0, 760])
        fig.update_xaxes(showgrid=False)
        st.plotly_chart(gaya_grafik(fig, 420), use_container_width=True)
        st.caption("Capaian 2024: 102,9% · 2025: 105,6% (hitung ulang; laporan resmi 105,8%).")

    with c2:
        st.subheader("Perubahan berat badan catin per kecamatan")
        d = df.sort_values("pct_naik")
        fig = go.Figure()
        for kolom, label, w in [("pct_naik", "BB naik", WARNA["naik"]),
                                ("pct_tetap", "BB tetap", WARNA["tetap"]),
                                ("pct_turun", "BB turun", WARNA["turun"])]:
            fig.add_bar(name=label, y=d.kecamatan, x=d[kolom], orientation="h", marker_color=w,
                        marker_line=dict(color="white", width=1.5),
                        customdata=d[["n_catin"]],
                        hovertemplate="<b>%{y}</b><br>" + label + ": %{x:.1f}%<br>n = %{customdata[0]}<extra></extra>")
        fig.update_layout(barmode="stack", legend_traceorder="normal")
        fig.update_xaxes(title="% catin terintervensi", range=[0, 100])
        st.plotly_chart(gaya_grafik(fig, 520), use_container_width=True)

    st.markdown("**Kategori luaran per kecamatan**")
    kat = df[["kecamatan", "n_catin", "pct_naik"]].sort_values("pct_naik").copy()
    kat["kategori"] = pd.cut(kat.pct_naik, [-1, 69.99, 84.99, 101], labels=["Perlu evaluasi", "Cukup", "Baik"])
    st.dataframe(kat.rename(columns={"kecamatan": "Kecamatan", "n_catin": "Terintervensi",
                                     "pct_naik": "% BB naik", "kategori": "Kategori"}),
                 hide_index=True, use_container_width=True)
    st.caption("Kategori: < 70% perlu evaluasi; 70–84,9% cukup; ≥ 85% baik.")

# posisi label agar nama kecamatan yang berdekatan tidak bertumpuk
POSISI_LABEL = {"Semarang Barat": "middle left", "Ngaliyan": "bottom center",
                "Gajahmungkur": "top right", "Semarang Selatan": "top left", "Tembalang": "bottom center"}

# ---------------------------------------------------------------------------
# TAB 3 - KUADRAN PRIORITAS
# ---------------------------------------------------------------------------
with tab3:
    st.subheader("Beban perkawinan usia muda vs rasio intervensi catin")
    prioritas = df.kuadran.str.startswith("I -")
    fig = go.Figure()
    for nama, mask, w in [("Kuadran I (prioritas)", prioritas, WARNA["sorot"]),
                          ("Kuadran lain", ~prioritas, WARNA["utama"])]:
        d = df[mask]
        fig.add_scatter(
            name=nama, x=d.pct_p_lt19, y=d.rasio, mode="markers+text", text=d.kecamatan,
            textposition=[POSISI_LABEL.get(k, "top center") for k in d.kecamatan], textfont=dict(size=11),
            marker=dict(size=(d.n_catin ** 0.5) * 3.2 + 6, color=w, line=dict(color="white", width=2)),
            customdata=d[["n_catin", "pct_naik", "kuadran"]],
            hovertemplate="<b>%{text}</b><br>Kawin < 19 th: %{x:.2f}%<br>Rasio: %{y:.2f} per 100"
                          "<br>Catin terintervensi: %{customdata[0]}<br>BB naik: %{customdata[1]}%"
                          "<br>Kuadran %{customdata[2]}<extra></extra>")
    fig.add_vline(x=MED_DINI, line_dash="dot", line_color=WARNA["teks"])
    fig.add_hline(y=MED_RASIO, line_dash="dot", line_color=WARNA["teks"])
    fig.update_yaxes(type="log", title="Catin terintervensi per 100 PUS kawin < 19 th (skala log)",
                     tickvals=[1, 2, 5, 10, 20], ticktext=["1", "2", "5", "10", "20"],
                     showgrid=True, gridcolor=WARNA["grid"])
    fig.update_xaxes(title="% PUS perempuan kawin pertama < 19 tahun")
    st.plotly_chart(gaya_grafik(fig, 560), use_container_width=True)
    st.caption(f"Garis putus-putus = median kota ({angka(MED_DINI, 2)}% dan {angka(MED_RASIO, 2)} per 100). "
               "Ukuran lingkaran sebanding dengan jumlah catin terintervensi.")

    arah = {"I - Prioritas": "Tambah target dan penjangkauan aktif catin",
            "II - Pertahankan": "Pertahankan cakupan; perbaiki mutu bila luaran rendah",
            "III - Pantau": "Pemantauan; evaluasi luaran yang rendah",
            "IV - Evaluasi efektivitas": "Evaluasi efektivitas pelaksanaan"}
    ringkas = (df.groupby("kuadran").kecamatan.apply(lambda s: ", ".join(sorted(s))).reset_index())
    ringkas["Arah kebijakan"] = ringkas.kuadran.map(arah)
    st.dataframe(ringkas.rename(columns={"kuadran": "Kuadran", "kecamatan": "Kecamatan"}),
                 hide_index=True, use_container_width=True)
    st.info("Kuadran dihitung dari median 16 kecamatan, sehingga tidak berubah saat filter dipakai.")

# ---------------------------------------------------------------------------
# TAB 4 - UJI STATISTIK
# ---------------------------------------------------------------------------
with tab4:
    st.subheader("Korelasi rank Spearman antarkecamatan")
    if len(df) < 5:
        st.warning("Pilih minimal 5 kecamatan agar korelasi bermakna untuk dihitung.")
    else:
        pasangan = [
            ("% kawin < 19 th", "pct_p_lt19", "Jumlah catin terintervensi", "n_catin"),
            ("Jumlah kawin < 19 th", "p_lt19", "Jumlah catin terintervensi", "n_catin"),
            ("% kawin < 19 th", "pct_p_lt19", "Rasio per 100", "rasio"),
            ("% kawin < 19 th", "pct_p_lt19", "% BB naik", "pct_naik"),
            ("Jumlah catin terintervensi", "n_catin", "% BB naik", "pct_naik"),
        ]
        hasil = []
        for lx, x, ly, y in pasangan:
            rho, p = stats.spearmanr(df[x], df[y])
            hasil.append({"Variabel X": lx, "Variabel Y": ly, "ρ": round(rho, 3), "p": round(p, 3),
                          "Kesimpulan (α = 0,05)": "Bermakna" if p < 0.05 else "Tidak bermakna"})
        st.dataframe(pd.DataFrame(hasil), hide_index=True, use_container_width=True)
        st.caption(f"n = {len(df)} kecamatan. Hasil untuk 16 kecamatan sama dengan Tabel 14 laporan.")

    st.subheader("Chi-square: BB naik vs tidak naik antarkecamatan")
    tabel = pd.DataFrame({"naik": df.bb_naik, "tidak": df.n_catin - df.bb_naik}).values
    if len(df) >= 2:
        chi, p, dof, exp = stats.chi2_contingency(tabel)
        c1, c2, c3 = st.columns(3)
        c1.metric("χ²", angka(chi, 2))
        c2.metric("db", dof)
        c3.metric("p", "< 0,001" if p < 0.001 else angka(p, 3))
        kecil = int((exp < 5).sum())
        if kecil:
            st.caption(f"{kecil} sel memiliki frekuensi harapan < 5; konfirmasi dengan uji Monte Carlo/Exact.")

# ---------------------------------------------------------------------------
# TAB 5 - DATA
# ---------------------------------------------------------------------------
with tab5:
    st.subheader("Data per kecamatan")
    tampil = df[["kode", "kecamatan", "pus", "p_lt19", "pct_p_lt19", "l_lt25", "pct_l_lt25",
                 "n_catin", "bb_naik", "bb_tetap", "bb_turun", "pct_naik", "rasio", "kuadran"]].copy()
    tampil[["pct_p_lt19", "pct_l_lt25", "rasio"]] = tampil[["pct_p_lt19", "pct_l_lt25", "rasio"]].round(2)
    tampil.columns = ["Kode", "Kecamatan", "PUS", "Perempuan < 19 th", "% perempuan < 19 th",
                      "Laki-laki < 25 th", "% laki-laki < 25 th", "Catin terintervensi",
                      "BB naik", "BB tetap", "BB turun", "% BB naik", "Rasio per 100", "Kuadran"]
    st.dataframe(tampil, hide_index=True, use_container_width=True)
    st.download_button("Unduh data (CSV)", tampil.to_csv(index=False).encode("utf-8"),
                       "data_catin_kecamatan_2025.csv", "text/csv")

    st.subheader("Catatan kualitas data")
    st.dataframe(pd.DataFrame([
        ("Akurasi", "Capaian 2025 tertulis 105,8%; hasil hitung 644/610 = 105,6%"),
        ("Metadata", "Judul tabel catin per kecamatan pada laporan tertulis \"BADUTA\""),
        ("Metadata", "Kolom wilayah pada Tabel 3 PUS tertulis \"Kabupaten\""),
        ("Akurasi entri", "Kader terkadang kurang teliti saat memasukkan data"),
        ("Konsistensi", "Data catin dimasukkan dua kali (Elsimil dan Primadona)"),
        ("Kelengkapan", "Rekap hanya memuat persentase; BB awal-akhir per catin belum tersedia"),
    ], columns=["Dimensi", "Temuan"]), hide_index=True, use_container_width=True)
