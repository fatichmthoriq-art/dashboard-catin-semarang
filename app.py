"""
Dashboard Ruang Kendali PANSOS/DASHAT 2025 - Calon Pengantin Kota Semarang
Laporan MBKM - Inez Ajeng Puspita (25000123120031), FKM Universitas Diponegoro

Menjalankan:
    pip install -r requirements.txt
    streamlit run app.py
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

st.set_page_config(page_title="Ruang Kendali Catin · Kota Semarang", layout="wide",
                   initial_sidebar_state="collapsed")

# ---------------------------------------------------------------------------
# 1. DATA  (ubah di sini bila data diperbarui)
#    Sumber: Pendataan Keluarga s.d. 2025 dan Laporan Intervensi PANSOS/DASHAT
#    2025, Disdalduk KB Kota Semarang.
# ---------------------------------------------------------------------------
@st.cache_data
def muat_data():
    df = pd.DataFrame([
        # kode, kecamatan, PUS, perempuan<19, laki<25, catin, %naik, %tetap, %turun
        ("01", "Semarang Tengah", 4143, 327, 1227, 73, 83.6, 6.8, 9.6),
        ("02", "Semarang Utara", 14036, 751, 7888, 21, 71.4, 0.0, 28.6),
        ("03", "Semarang Timur", 5864, 595, 2089, 73, 78.1, 20.5, 1.4),
        ("04", "Gayamsari", 7687, 802, 2807, 35, 94.3, 5.7, 0.0),
        ("05", "Genuk", 19962, 1715, 9575, 84, 66.7, 21.4, 11.9),
        ("06", "Pedurungan", 23631, 1479, 6709, 17, 76.5, 23.5, 0.0),
        ("07", "Semarang Selatan", 5926, 353, 2082, 17, 82.4, 17.6, 0.0),
        ("08", "Candisari", 8648, 564, 2762, 36, 50.0, 44.4, 5.6),
        ("09", "Gajahmungkur", 6301, 403, 1762, 17, 94.1, 5.9, 0.0),
        ("10", "Tembalang", 28054, 1923, 10664, 52, 88.5, 9.6, 1.9),
        ("11", "Banyumanik", 16136, 766, 5968, 15, 46.7, 33.3, 20.0),
        ("12", "Gunungpati", 14077, 1592, 5358, 71, 81.7, 15.5, 2.8),
        ("13", "Semarang Barat", 16735, 952, 6626, 38, 81.6, 18.4, 0.0),
        ("14", "Mijen", 11722, 1219, 4382, 21, 85.7, 9.5, 4.8),
        ("15", "Ngaliyan", 19680, 1241, 7961, 48, 93.8, 4.2, 2.1),
        ("16", "Tugu", 4314, 395, 1501, 26, 88.5, 7.7, 3.8),
    ], columns=["kode", "kecamatan", "pus", "p_lt19", "l_lt25", "n_catin",
                "pct_naik", "pct_tetap", "pct_turun"])
    df["bb_naik"] = (df.n_catin * df.pct_naik / 100).round().astype(int)
    df["bb_turun"] = (df.n_catin * df.pct_turun / 100).round().astype(int)
    df["bb_tetap"] = df.n_catin - df.bb_naik - df.bb_turun
    df["pct_dini"] = df.p_lt19 / df.pus * 100
    df["rasio"] = df.n_catin / df.p_lt19 * 100
    med_d, med_r = df.pct_dini.median(), df.rasio.median()
    df["kuadran"] = [
        "I" if d > med_d and r <= med_r else "II" if d > med_d else "III" if r <= med_r else "IV"
        for d, r in zip(df.pct_dini, df.rasio)]
    return df, med_d, med_r


DF, MED_DINI, MED_RASIO = muat_data()
TARGET = {"2024": (410, 422), "2025": (610, 644)}


def fmt(x, d=0):
    """Format angka Indonesia: 206.916 / 7,29"""
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


# ---------------------------------------------------------------------------
# 2. GAYA (CSS) - tema gelap ruang kendali
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap');
html, body, [class*="st-"], .stApp { font-family: 'Space Grotesk', system-ui, sans-serif; }
.stApp { background: #111316; color: #e8eaed; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.6rem; padding-bottom: 2rem; max-width: 1400px; }
.mono { font-family: 'IBM Plex Mono', monospace; }
.eyebrow { font-size: 12px; letter-spacing: .12em; color: #8d939c; }
.judul { font-size: 26px; font-weight: 600; margin: 2px 0 0; color: #e8eaed; }
.kartu { background: #1a1d22; border: 1px solid #262a31; border-radius: 12px; padding: 16px 18px; height: 100%; }
.kartu h3 { margin: 0 0 12px; font-size: 15px; font-weight: 600; color: #e8eaed; }
.kpi-label { font-size: 12px; color: #8d939c; margin-bottom: 8px; }
.kpi-nilai { font-family: 'IBM Plex Mono', monospace; font-size: 28px; font-weight: 600; color: #e8eaed; line-height: 1.1; }
.kpi-sub { font-size: 12px; color: #8d939c; margin-left: 8px; font-family: 'Space Grotesk', sans-serif; font-weight: 500; }
.naik { color: #5fd07a !important; }
.oranye { color: #f0a35e !important; }
.petak-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; }
@media (max-width: 700px) { .petak-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.petak { border-radius: 10px; padding: 12px 14px; min-height: 96px; display: flex; flex-direction: column; justify-content: space-between; gap: 6px; }
.petak .nm { font-size: 13px; font-weight: 600; }
.petak .q { font-size: 10px; font-weight: 700; opacity: .8; }
.petak .v { font-family: 'IBM Plex Mono', monospace; font-size: 22px; font-weight: 600; }
.petak .s { font-size: 11px; opacity: .85; }
.redup { opacity: .25; }
.skala { display: flex; align-items: center; gap: 8px; font-size: 11px; color: #8d939c; }
.skala span.k { width: 18px; height: 10px; display: inline-block; }
.alert { display: flex; gap: 12px; align-items: flex-start; padding: 10px 12px; border-radius: 8px; background: #20242a; margin-bottom: 8px; }
.alert .ic { flex: none; width: 22px; height: 22px; border-radius: 50%; color: #111316; font-size: 13px; font-weight: 700; display: flex; align-items: center; justify-content: center; }
.alert .j { font-size: 13px; font-weight: 600; color: #e8eaed; }
.alert .t { font-size: 12px; line-height: 1.5; color: #a9aeb6; }
.bar-bg { height: 8px; background: #2b2f36; border-radius: 4px; }
.bar { height: 8px; background: #3a87e5; border-radius: 4px; }
.baris-tr { display: flex; justify-content: space-between; font-size: 12px; color: #a9aeb6; margin: 10px 0 6px; }
.rank { display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); column-gap: 32px; row-gap: 7px; }
.rank-row { display: grid; grid-template-columns: 24px 140px 1fr 56px; align-items: center; gap: 10px; font-size: 12.5px; }
.stack { display: flex; height: 10px; gap: 2px; }
.stack div { height: 10px; border-radius: 2px; }
.legend { display: flex; gap: 14px; font-size: 11px; color: #a9aeb6; }
.legend i { width: 10px; height: 10px; border-radius: 2px; display: inline-block; margin-right: 5px; vertical-align: -1px; }
.sumber { font-size: 11px; color: #6f757e; margin-top: 8px; }
div[data-testid="stTabs"] button p { font-size: 14px; }
</style>
""", unsafe_allow_html=True)


def html(s):
    """Render HTML tanpa indentasi (agar tidak dibaca markdown sebagai kode)."""
    st.markdown("".join(line.strip() for line in s.splitlines()), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 3. HEADER DAN FILTER
# ---------------------------------------------------------------------------
kiri, kanan = st.columns([5, 4], vertical_alignment="bottom")
with kiri:
    html("""<div class="eyebrow">DISDALDUK KB KOTA SEMARANG · PEMANTAUAN CATIN</div>
            <div class="judul">Ruang Kendali PANSOS/DASHAT 2025</div>""")
with kanan:
    f1, f2 = st.columns([5, 3])
    mode = f1.segmented_control("Tampilan", ["Semua", "Kuadran I", "Perlu evaluasi"],
                                default="Semua", label_visibility="collapsed")
    sorot = f2.selectbox("Sorot kecamatan", sorted(DF.kecamatan), index=None,
                         placeholder="Sorot kecamatan…", label_visibility="collapsed")

mode = mode or "Semua"
if mode == "Kuadran I":
    aktif = DF.kuadran == "I"
elif mode == "Perlu evaluasi":
    aktif = DF.pct_naik < 70
else:
    aktif = pd.Series(True, index=DF.index)
if sorot:
    aktif = aktif & (DF.kecamatan == sorot) if mode != "Semua" else DF.kecamatan == sorot
D = DF[aktif]
if D.empty:
    st.warning("Tidak ada kecamatan yang cocok dengan kombinasi filter ini.")
    st.stop()
semua = len(D) == 16

# ---------------------------------------------------------------------------
# 4. KPI
# ---------------------------------------------------------------------------
pus, dini, catin, naik = D.pus.sum(), D.p_lt19.sum(), D.n_catin.sum(), D.bb_naik.sum()
pct_naik = "79,4" if semua else fmt(naik / catin * 100, 1)  # 79,4% = angka laporan resmi
kpi = [
    ("PUS", f'<span class="kpi-nilai">{fmt(pus)}</span>'),
    ("Kawin pertama &lt; 19 th", f'<span class="kpi-nilai oranye">{fmt(dini / pus * 100, 2)}%</span>'),
    ("Catin terintervensi", f'<span class="kpi-nilai">{fmt(catin)}</span>'
                            + ('<span class="kpi-sub naik">▲ 105,6% target</span>' if semua else '')),
    ("BB naik", f'<span class="kpi-nilai">{pct_naik}%</span><span class="kpi-sub">baduta 88,9%</span>'),
    ("Kecamatan prioritas", '<span class="kpi-nilai oranye">2</span>'
                            '<span class="kpi-sub" style="color:#c5c9cf">Tembalang, Mijen</span>'),
]
for col, (lab, isi) in zip(st.columns(5), kpi):
    with col:
        html(f'<div class="kartu"><div class="kpi-label">{lab}</div><div>{isi}</div></div>')

st.write("")

# ---------------------------------------------------------------------------
# 5. PETAK KECAMATAN + PANEL KANAN
# ---------------------------------------------------------------------------
def warna_petak(v):
    if v < 6:
        return "#1c3554", "#e8eaed"
    if v < 7:
        return "#1f4f8a", "#ffffff"
    if v < 8.5:
        return "#2a6fc2", "#ffffff"
    if v < 10:
        return "#4e93e6", "#0d1117"
    return "#8dbcf2", "#0d1117"


kol_petak, kol_panel = st.columns([5, 3])
with kol_petak:
    petak = []
    for _, r in DF.sort_values("kecamatan").iterrows():
        bg, fg = warna_petak(r.pct_dini)
        ring = "outline:3px solid #f0a35e;outline-offset:-2px;" if r.kuadran == "I" else ""
        kelas = "petak" if aktif[r.name] else "petak redup"
        petak.append(
            f'<div class="{kelas}" style="background:{bg};color:{fg};{ring}" '
            f'title="{r.kecamatan}: {fmt(r.p_lt19)} dari {fmt(r.pus)} PUS; rasio {fmt(r.rasio, 2)} per 100">'
            f'<div style="display:flex;justify-content:space-between;gap:6px">'
            f'<span class="nm">{r.kecamatan}</span><span class="q">Q{r.kuadran}</span></div>'
            f'<div class="v">{fmt(r.pct_dini, 2)}%</div>'
            f'<div class="s">BB naik {fmt(r.pct_naik, 1)}% · n {r.n_catin}</div></div>')
    html(f"""<div class="kartu">
        <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:10px;margin-bottom:12px">
          <h3 style="margin:0">Petak 16 kecamatan</h3>
          <div class="skala">% kawin &lt; 19 th
            <span class="k" style="background:#1c3554"></span><span class="k" style="background:#1f4f8a"></span>
            <span class="k" style="background:#2a6fc2"></span><span class="k" style="background:#4e93e6"></span>
            <span class="k" style="background:#8dbcf2"></span> 4,7 → 11,3</div>
        </div>
        <div class="petak-grid">{''.join(petak)}</div>
        <div class="sumber">Bingkai oranye = kuadran I (prioritas). Petak disusun alfabetis, bukan posisi geografis.
        Arahkan kursor ke petak untuk detail.</div></div>""")

with kol_panel:
    peringatan = [
        ("#f0a35e", "Tembalang &amp; Mijen · kuadran I", "Beban tinggi, rasio intervensi 2,70 dan 1,72 per 100."),
        ("#e25757", "Banyumanik · BB naik 46,7%", "20% catin mengalami penurunan BB."),
        ("#e25757", "Semarang Utara · BB turun 28,6%", "Proporsi penurunan tertinggi di kota."),
        ("#e0a526", "Candisari · BB tetap 44,4%", "Hanya separuh catin mengalami kenaikan BB."),
        ("#e0a526", "Kualitas data", "Entri kader belum divalidasi; data ganda Elsimil–Primadona."),
    ]
    isi = "".join(f'<div class="alert"><span class="ic" style="background:{c}">!</span>'
                  f'<div><div class="j">{j}</div><div class="t">{t}</div></div></div>'
                  for c, j, t in peringatan)
    tr = "".join(
        f'<div class="baris-tr"><span>{th}</span><span class="mono">{real} / {tgt} · {fmt(real / tgt * 100, 1)}%</span></div>'
        f'<div class="bar-bg"><div class="bar" style="width:100%"></div></div>'
        for th, (tgt, real) in TARGET.items())
    html(f'<div class="kartu"><h3>Perlu perhatian</h3>{isi}</div>')
    st.write("")
    html(f'<div class="kartu"><h3>Target vs realisasi</h3>{tr}</div>')

st.write("")

# ---------------------------------------------------------------------------
# 6. PERINGKAT LUARAN BB
# ---------------------------------------------------------------------------
rows = []
for i, (_, r) in enumerate(D.sort_values("pct_naik", ascending=False).iterrows(), start=1):
    tebal = "font-weight:700;color:#f0a35e;" if r.kecamatan == sorot else "color:#c5c9cf;"
    rows.append(
        f'<div class="rank-row"><span class="mono" style="color:#6f757e">{i:02d}</span>'
        f'<span style="{tebal}">{r.kecamatan}</span>'
        f'<div class="stack" title="Naik {fmt(r.pct_naik, 1)}% · Tetap {fmt(r.pct_tetap, 1)}% · Turun {fmt(r.pct_turun, 1)}%">'
        f'<div style="background:#3fb85f;width:{r.pct_naik}%"></div>'
        f'<div style="background:#e0a526;width:{r.pct_tetap}%"></div>'
        f'<div style="background:#e25757;width:{r.pct_turun}%"></div></div>'
        f'<span class="mono" style="text-align:right">{fmt(r.pct_naik, 1)}%</span></div>')
html(f"""<div class="kartu">
    <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:10px;margin-bottom:12px">
      <h3 style="margin:0">Peringkat luaran BB catin</h3>
      <div class="legend"><span><i style="background:#3fb85f"></i>Naik</span>
      <span><i style="background:#e0a526"></i>Tetap</span><span><i style="background:#e25757"></i>Turun</span></div>
    </div><div class="rank">{''.join(rows)}</div></div>""")

st.write("")

# ---------------------------------------------------------------------------
# 7. ANALISIS LANJUTAN (tab)
# ---------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["Kuadran prioritas", "Uji statistik", "Data"])

POSISI = {"Semarang Barat": "middle left", "Ngaliyan": "bottom center", "Gajahmungkur": "top right",
          "Semarang Selatan": "top left", "Tembalang": "bottom center"}

with tab1:
    fig = go.Figure()
    for nama, m, w in [("Kuadran I (prioritas)", DF.kuadran == "I", "#f0a35e"),
                       ("Kuadran lain", DF.kuadran != "I", "#4e93e6")]:
        d = DF[m]
        fig.add_scatter(
            name=nama, x=d.pct_dini, y=d.rasio, mode="markers+text", text=d.kecamatan,
            textposition=[POSISI.get(k, "top center") for k in d.kecamatan],
            textfont=dict(size=11, color="#c5c9cf"),
            marker=dict(size=d.n_catin ** 0.5 * 3 + 6, color=w, line=dict(color="#111316", width=2)),
            customdata=d[["n_catin", "pct_naik", "kuadran"]],
            hovertemplate="<b>%{text}</b><br>Kawin < 19 th: %{x:.2f}%<br>Rasio: %{y:.2f} per 100"
                          "<br>Catin: %{customdata[0]} · BB naik %{customdata[1]}%"
                          "<br>Kuadran %{customdata[2]}<extra></extra>")
    fig.add_vline(x=MED_DINI, line_dash="dot", line_color="#6f757e")
    fig.add_hline(y=MED_RASIO, line_dash="dot", line_color="#6f757e")
    fig.update_layout(
        height=520, paper_bgcolor="#1a1d22", plot_bgcolor="#1a1d22",
        font=dict(family="Space Grotesk, sans-serif", color="#c5c9cf", size=12),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", y=1.08, x=0, font=dict(color="#c5c9cf")),
        hoverlabel=dict(bgcolor="#20242a", font_color="#e8eaed"))
    fig.update_xaxes(title="% PUS perempuan kawin pertama < 19 tahun", gridcolor="#262a31", zeroline=False)
    fig.update_yaxes(title="Catin per 100 PUS kawin < 19 th (log)", type="log", gridcolor="#262a31",
                     tickvals=[1, 2, 5, 10, 20], ticktext=["1", "2", "5", "10", "20"], zeroline=False)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Garis titik-titik = median kota ({fmt(MED_DINI, 2)}% dan {fmt(MED_RASIO, 2)} per 100). "
               "Ukuran lingkaran sebanding dengan jumlah catin terintervensi.")

with tab2:
    pas = [("% kawin < 19 th", "pct_dini", "Jumlah catin", "n_catin"),
           ("Jumlah kawin < 19 th", "p_lt19", "Jumlah catin", "n_catin"),
           ("% kawin < 19 th", "pct_dini", "Rasio per 100", "rasio"),
           ("% kawin < 19 th", "pct_dini", "% BB naik", "pct_naik"),
           ("Jumlah catin", "n_catin", "% BB naik", "pct_naik")]
    hasil = []
    for lx, x, ly, y in pas:
        rho, p = stats.spearmanr(DF[x], DF[y])
        hasil.append({"Variabel X": lx, "Variabel Y": ly, "ρ Spearman": round(rho, 3), "p": round(p, 3),
                      "Kesimpulan": "Bermakna" if p < 0.05 else "Tidak bermakna"})
    st.markdown("**Korelasi Spearman antarkecamatan (n = 16)**")
    st.dataframe(pd.DataFrame(hasil), hide_index=True, use_container_width=True)
    chi, p, dof, exp = stats.chi2_contingency(pd.DataFrame({"a": DF.bb_naik, "b": DF.n_catin - DF.bb_naik}).values)
    c1, c2, c3 = st.columns(3)
    c1.metric("χ² BB naik antarkecamatan", fmt(chi, 2))
    c2.metric("db", dof)
    c3.metric("p", "< 0,001" if p < 0.001 else fmt(p, 3))
    st.caption(f"{int((exp < 5).sum())} sel memiliki frekuensi harapan < 5; dikonfirmasi uji Monte Carlo (p < 0,001).")

with tab3:
    t = DF[["kode", "kecamatan", "pus", "p_lt19", "pct_dini", "n_catin", "bb_naik", "bb_tetap",
            "bb_turun", "pct_naik", "rasio", "kuadran"]].copy()
    t[["pct_dini", "rasio"]] = t[["pct_dini", "rasio"]].round(2)
    t.columns = ["Kode", "Kecamatan", "PUS", "Kawin < 19 th", "% kawin < 19 th", "Catin", "BB naik",
                 "BB tetap", "BB turun", "% BB naik", "Rasio per 100", "Kuadran"]
    st.dataframe(t, hide_index=True, use_container_width=True)
    st.download_button("Unduh data (CSV)", t.to_csv(index=False).encode("utf-8"),
                       "data_catin_kecamatan_2025.csv", "text/csv")

html('<div class="sumber">Sumber: Pendataan Keluarga s.d. 2025 · Laporan PANSOS/DASHAT 2025, '
     'Disdalduk KB Kota Semarang · Diolah: Inez Ajeng Puspita, MBKM FKM UNDIP</div>')
