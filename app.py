"""
SIAP NIKAH SEMARANG - Dashboard Skrining Calon Pengantin & Intervensi DASHAT
Laporan MBKM - Inez Ajeng Puspita (25000123120031), FKM Universitas Diponegoro

Menjalankan:
    pip install -r requirements.txt
    streamlit run app.py
"""

from datetime import date, datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Siap Nikah Semarang · Skrining Catin", page_icon="💐", layout="wide")

FILE_DATA = Path(__file__).parent / "data_catin.csv"
KOLOM = ["waktu_input", "kode", "kecamatan", "usia", "tinggi_cm", "berat_kg", "imt", "lila_cm", "hb",
         "rokok", "rencana_nikah", "st_usia", "st_tb", "st_imt", "st_lila", "st_hb", "st_rokok",
         "jumlah_risiko", "kategori"]
KECAMATAN = ["Banyumanik", "Candisari", "Gajahmungkur", "Gayamsari", "Genuk", "Gunungpati", "Mijen",
             "Ngaliyan", "Pedurungan", "Semarang Barat", "Semarang Selatan", "Semarang Tengah",
             "Semarang Timur", "Semarang Utara", "Tembalang", "Tugu"]

# Warna tema "ceria dan charming"
ROSE, CORAL, LAV, MINT, SUN, INK, SOFT = "#d63a6a", "#f28c6b", "#8a74c9", "#2e9e86", "#e9a91c", "#3b2a35", "#7a6470"
STATUS = {  # warna + ikon + label - status tidak pernah hanya warna
    "Aman": ("#2e9e86", "✓"),
    "Waspada": ("#d98a00", "!"),
    "Berisiko": ("#d63a6a", "✕"),
}

# ---------------------------------------------------------------------------
# GAYA
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Nunito:wght@400;600;700;800&display=swap');
html, body, .stApp, .stApp p, .stApp label, .stApp input, .stApp button, .stApp li { font-family: 'Nunito', system-ui, sans-serif; }
.stApp { background: radial-gradient(circle at 0% 0%, #ffe8ef 0, transparent 38%),
                     radial-gradient(circle at 100% 0%, #efe9ff 0, transparent 34%),
                     radial-gradient(circle at 100% 100%, #e3f7f1 0, transparent 36%), #fffafb; color: #3b2a35; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.4rem; max-width: 1280px; }
h1, h2, h3, .disp { font-family: 'Fraunces', Georgia, serif !important; color: #3b2a35; }
.hero { background: linear-gradient(120deg, #ffd6e2 0%, #ffe6d6 45%, #e9e2ff 100%); border-radius: 28px;
        padding: 28px 32px; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 18px;
        border: 1px solid #ffffff; box-shadow: 0 10px 30px rgba(214,58,106,.10); }
.hero .t { font-family: 'Fraunces', serif; font-size: 34px; font-weight: 700; line-height: 1.1; color: #3b2a35; }
.hero .s { font-size: 15px; color: #5e4653; margin-top: 6px; max-width: 620px; }
.chip { display: inline-block; background: #ffffffcc; border-radius: 999px; padding: 6px 14px; font-size: 12px;
        font-weight: 700; color: #b02a57; letter-spacing: .04em; }
.kpi { background: #ffffff; border-radius: 22px; padding: 18px 20px; border: 1px solid #f6dfe6;
       box-shadow: 0 6px 18px rgba(59,42,53,.05); height: 100%; }
.kpi .l { font-size: 13px; color: #7a6470; font-weight: 700; }
.kpi .v { font-family: 'Fraunces', serif; font-size: 34px; font-weight: 700; line-height: 1.15; }
.kpi .d { font-size: 12px; color: #7a6470; }
.card { background: #ffffff; border-radius: 22px; padding: 20px 22px; border: 1px solid #f6dfe6;
        box-shadow: 0 6px 18px rgba(59,42,53,.05); }
.ind { display: flex; gap: 12px; align-items: center; padding: 11px 14px; border-radius: 16px; background: #fff7f9; margin-bottom: 8px; }
.ind .ic { flex: none; width: 30px; height: 30px; border-radius: 50%; color: #fff; font-weight: 800; display: flex;
           align-items: center; justify-content: center; font-size: 15px; }
.ind .n { font-weight: 800; font-size: 14px; color: #3b2a35; }
.ind .k { font-size: 12.5px; color: #6b5562; }
.ind .tag { margin-left: auto; font-size: 12px; font-weight: 800; padding: 4px 10px; border-radius: 999px; white-space: nowrap; }
.hasil { border-radius: 24px; padding: 22px 24px; color: #fff; }
.hasil .t { font-family: 'Fraunces', serif; font-size: 28px; font-weight: 700; }
.petak-grid { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 10px; }
@media (max-width: 760px) { .petak-grid { grid-template-columns: repeat(2, minmax(0,1fr)); } .hero .t { font-size: 26px; } }
.petak { border-radius: 18px; padding: 12px 14px; min-height: 92px; display: flex; flex-direction: column; justify-content: space-between; }
.petak .nm { font-size: 13px; font-weight: 800; }
.petak .v { font-family: 'Fraunces', serif; font-size: 22px; font-weight: 700; }
.petak .s { font-size: 11.5px; }
.note { font-size: 12px; color: #7a6470; }
div[data-testid="stTabs"] button p { font-size: 15px; font-weight: 700; }
div[data-testid="stForm"] { background: #ffffff; border-radius: 24px; border: 1px solid #f6dfe6; padding: 8px 10px; }
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button { border-radius: 999px !important; font-weight: 800 !important; }
</style>
""", unsafe_allow_html=True)


def html(s):
    st.markdown(" ".join(x.strip() for x in s.splitlines()), unsafe_allow_html=True)


def fmt(x, d=0):
    s = f"{x:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


# ---------------------------------------------------------------------------
# PENYIMPANAN DATA INPUT
# ---------------------------------------------------------------------------
def baca_data():
    if FILE_DATA.exists():
        return pd.read_csv(FILE_DATA, dtype={"kode": str})
    return pd.DataFrame(columns=KOLOM)


def simpan_data(df):
    df.to_csv(FILE_DATA, index=False)


# ---------------------------------------------------------------------------
# ATURAN SKRINING CATIN PEREMPUAN
#   Ambang batas mengacu pada indikator skrining catin (Elsimil/BKKBN) dan
#   UU No. 16/2019. Sesuaikan dengan pedoman terbaru dari Disdalduk bila berbeda.
# ---------------------------------------------------------------------------
def skrining(usia, tb, bb, lila, hb, rokok):
    imt = bb / (tb / 100) ** 2
    hasil = {}
    if usia < 19:
        hasil["usia"] = ("Berisiko", "Di bawah batas usia minimal menikah (19 tahun, UU 16/2019)")
    elif usia < 20 or usia > 35:
        hasil["usia"] = ("Berisiko", "Usia < 20 atau > 35 tahun: kehamilan berisiko")
    else:
        hasil["usia"] = ("Aman", "Usia 20–35 tahun, usia reproduksi sehat")
    hasil["tb"] = (("Berisiko", "Tinggi badan < 145 cm") if tb < 145 else ("Aman", "Tinggi badan ≥ 145 cm"))
    if imt < 18.5:
        hasil["imt"] = ("Berisiko", f"IMT {fmt(imt, 1)}: kurus (< 18,5)")
    elif imt >= 25:
        hasil["imt"] = ("Waspada", f"IMT {fmt(imt, 1)}: berat badan lebih (≥ 25)")
    else:
        hasil["imt"] = ("Aman", f"IMT {fmt(imt, 1)}: normal")
    hasil["lila"] = (("Berisiko", "LiLA < 23,5 cm: risiko kurang energi kronis (KEK)") if lila < 23.5
                     else ("Aman", "LiLA ≥ 23,5 cm"))
    hasil["hb"] = (("Berisiko", "Hb < 12 g/dL: anemia") if hb < 12 else ("Aman", "Hb ≥ 12 g/dL"))
    hasil["rokok"] = (("Waspada", "Merokok atau terpapar asap rokok") if rokok != "Tidak"
                      else ("Aman", "Tidak terpapar asap rokok"))
    n_risk = sum(v[0] == "Berisiko" for v in hasil.values())
    n_was = sum(v[0] == "Waspada" for v in hasil.values())
    kategori = "Berisiko" if n_risk else ("Waspada" if n_was else "Siap")
    return imt, hasil, n_risk, kategori


NAMA_IND = {"usia": "Usia", "tb": "Tinggi badan", "imt": "Indeks massa tubuh", "lila": "Lingkar lengan atas",
            "hb": "Hemoglobin", "rokok": "Paparan rokok"}
SARAN = {
    "usia": "Konseling pendewasaan usia perkawinan dan perencanaan kehamilan.",
    "tb": "Pemantauan kehamilan lebih ketat; rujuk ke bidan/puskesmas.",
    "imt": "Konsultasi gizi untuk mencapai berat badan ideal sebelum hamil.",
    "lila": "Prioritas bantuan pangan bergizi DASHAT dan pendampingan gizi.",
    "hb": "Konsumsi tablet tambah darah dan makanan kaya zat besi; cek ulang Hb.",
    "rokok": "Berhenti merokok dan hindari asap rokok di rumah.",
}

# ---------------------------------------------------------------------------
# HERO
# ---------------------------------------------------------------------------
data = baca_data()
n_data = len(data)
if "toast" in st.session_state:
    st.toast(st.session_state.pop("toast"))
html(f"""<div class="hero"><div>
<span class="chip">DISDALDUK KB KOTA SEMARANG · DASHAT</span>
<div class="t" style="margin-top:10px">Siap Nikah, Siap Sehat 💐</div>
<div class="s">Skrining kesehatan calon pengantin perempuan dan pemantauan intervensi Dapur Sehat Atasi Stunting
untuk mencegah stunting sejak sebelum hamil.</div></div>
<div style="text-align:right"><div class="note">Catin tercatat di aplikasi ini</div>
<div class="disp" style="font-size:44px;font-weight:700;color:{ROSE}">{n_data}</div></div></div>""")
st.write("")

tab_input, tab_rekap, tab_kota = st.tabs(["✍️  Input & cek catin", "🌷  Rekap catin terdata", "🗺️  Gambaran Kota Semarang"])

# ---------------------------------------------------------------------------
# TAB 1 - INPUT
# ---------------------------------------------------------------------------
with tab_input:
    kiri, kanan = st.columns([1.05, 1], gap="large")
    with kiri:
        st.markdown("### Data calon pengantin perempuan")
        st.caption("Gunakan kode atau inisial, jangan nama lengkap atau NIK, untuk menjaga kerahasiaan data pribadi.")
        with st.form("form_catin", clear_on_submit=False):
            c1, c2 = st.columns(2)
            kode = c1.text_input("Kode / inisial catin", placeholder="mis. CTN-001 atau A.R.", max_chars=20)
            kec = c2.selectbox("Kecamatan", KECAMATAN, index=None, placeholder="Pilih kecamatan")
            c1, c2 = st.columns(2)
            usia = c1.number_input("Usia (tahun)", 14, 60, 22)
            nikah = c2.date_input("Rencana tanggal menikah", value=date.today(), format="DD/MM/YYYY")
            c1, c2, c3 = st.columns(3)
            tb = c1.number_input("Tinggi badan (cm)", 120.0, 200.0, 155.0, 0.1)
            bb = c2.number_input("Berat badan (kg)", 30.0, 150.0, 50.0, 0.1)
            lila = c3.number_input("LiLA (cm)", 15.0, 45.0, 25.0, 0.1)
            c1, c2 = st.columns(2)
            hb = c1.number_input("Hemoglobin / Hb (g/dL)", 5.0, 20.0, 12.5, 0.1)
            rokok = c2.selectbox("Merokok / terpapar asap rokok?", ["Tidak", "Terpapar asap rokok", "Merokok"])
            simpan = st.form_submit_button("💗  Cek & simpan data", type="primary", use_container_width=True)

        if simpan:
            if not kode.strip() or kec is None:
                st.error("Kode/inisial dan kecamatan wajib diisi.")
            else:
                imt, hasil, n_risk, kategori = skrining(usia, tb, bb, lila, hb, rokok)
                baris = {"waktu_input": datetime.now().strftime("%Y-%m-%d %H:%M"), "kode": kode.strip(),
                         "kecamatan": kec, "usia": usia, "tinggi_cm": tb, "berat_kg": bb, "imt": round(imt, 1),
                         "lila_cm": lila, "hb": hb, "rokok": rokok, "rencana_nikah": nikah.isoformat(),
                         **{f"st_{k}": v[0] for k, v in hasil.items()},
                         "jumlah_risiko": n_risk, "kategori": kategori}
                data = pd.concat([data, pd.DataFrame([baris])], ignore_index=True)
                simpan_data(data)
                st.session_state["terakhir"] = (kode.strip(), imt, hasil, n_risk, kategori)
                st.session_state["toast"] = f"Data {kode.strip()} tersimpan 💐"
                st.rerun()

    with kanan:
        st.markdown("### Hasil skrining")
        if "terakhir" not in st.session_state:
            html(f"""<div class="card" style="text-align:center;padding:40px 24px">
            <div style="font-size:44px">🌸</div>
            <div class="disp" style="font-size:22px;font-weight:700;margin-top:6px">Belum ada hasil</div>
            <div class="note" style="margin-top:6px">Isi formulir di samping lalu tekan <b>Cek &amp; simpan data</b>.
            Hasil kategori dan saran akan tampil di sini.</div></div>""")
        else:
            kode_t, imt, hasil, n_risk, kategori = st.session_state["terakhir"]
            warna = {"Siap": ("linear-gradient(120deg,#2e9e86,#5cc3a6)", "Siap menuju kehamilan sehat 🌿"),
                     "Waspada": ("linear-gradient(120deg,#d98a00,#f2b544)", "Perlu perhatian ringan 🌼"),
                     "Berisiko": ("linear-gradient(120deg,#d63a6a,#f28c6b)", "Catin berisiko, perlu pendampingan 💗")}[kategori]
            html(f"""<div class="hasil" style="background:{warna[0]}">
            <div style="font-size:13px;font-weight:800;opacity:.9">Catin {kode_t}</div>
            <div class="t">{kategori.upper()}</div>
            <div style="font-size:14px;font-weight:600">{warna[1]} · {n_risk} indikator berisiko</div></div>""")
            st.write("")
            baris = []
            for k, (stt, ket) in hasil.items():
                w, ic = STATUS[stt]
                baris.append(f'<div class="ind"><span class="ic" style="background:{w}">{ic}</span>'
                             f'<div><div class="n">{NAMA_IND[k]}</div><div class="k">{ket}</div></div>'
                             f'<span class="tag" style="background:{w}1f;color:{w}">{stt}</span></div>')
            html("".join(baris))
            saran = [SARAN[k] for k, (s, _) in hasil.items() if s != "Aman"]
            if saran:
                html('<div class="card" style="margin-top:6px"><div class="disp" style="font-size:18px;font-weight:700;'
                     'margin-bottom:6px">Saran tindak lanjut</div>'
                     + "".join(f'<div style="font-size:14px;margin:4px 0">🌷 {s}</div>' for s in saran) + "</div>")

    with st.expander("Kriteria skrining yang dipakai"):
        st.table(pd.DataFrame([
            ("Usia", "< 19 th (di bawah batas UU 16/2019), < 20 th atau > 35 th", "Berisiko"),
            ("Tinggi badan", "< 145 cm", "Berisiko"),
            ("IMT", "< 18,5 (kurus) → berisiko; ≥ 25 (berat lebih) → waspada", "Berisiko / Waspada"),
            ("LiLA", "< 23,5 cm (risiko KEK)", "Berisiko"),
            ("Hemoglobin", "< 12 g/dL (anemia)", "Berisiko"),
            ("Paparan rokok", "Merokok atau terpapar asap rokok", "Waspada"),
        ], columns=["Indikator", "Batas", "Status"]))
        st.caption("Kategori akhir: Berisiko jika ≥ 1 indikator berisiko; Waspada jika hanya ada indikator waspada; "
                   "selain itu Siap. Sesuaikan batas dengan pedoman terbaru dari Disdalduk KB bila berbeda.")

# ---------------------------------------------------------------------------
# TAB 2 - REKAP DATA INPUT
# ---------------------------------------------------------------------------
with tab_rekap:
    if data.empty:
        html('<div class="card" style="text-align:center;padding:40px"><div style="font-size:40px">🌷</div>'
             '<div class="disp" style="font-size:22px;font-weight:700">Belum ada data catin</div>'
             '<div class="note">Mulai dari tab <b>Input &amp; cek catin</b>, atau pulihkan data dari file CSV di bawah.</div></div>')
    else:
        n = len(data)
        n_r = (data.kategori == "Berisiko").sum()
        n_w = (data.kategori == "Waspada").sum()
        n_s = (data.kategori == "Siap").sum()
        kpi = [("Total catin", str(n), "terdata di aplikasi", ROSE),
               ("Berisiko", f"{n_r}", f"{fmt(n_r / n * 100, 1)}% dari catin", "#d63a6a"),
               ("Waspada", f"{n_w}", f"{fmt(n_w / n * 100, 1)}% dari catin", "#b87400"),
               ("Siap", f"{n_s}", f"{fmt(n_s / n * 100, 1)}% dari catin", MINT)]
        for col, (l, v, d, w) in zip(st.columns(4), kpi):
            with col:
                html(f'<div class="kpi"><div class="l">{l}</div><div class="v" style="color:{w}">{v}</div>'
                     f'<div class="d">{d}</div></div>')
        st.write("")

        g1, g2 = st.columns(2, gap="large")
        with g1:
            st.markdown("#### Indikator berisiko yang paling banyak")
            hit = pd.DataFrame({
                "Indikator": [NAMA_IND[k] for k in NAMA_IND],
                "Berisiko": [(data[f"st_{k}"] == "Berisiko").sum() for k in NAMA_IND],
                "Waspada": [(data[f"st_{k}"] == "Waspada").sum() for k in NAMA_IND]})
            hit = hit.sort_values("Berisiko")
            fig = go.Figure()
            fig.add_bar(y=hit.Indikator, x=hit.Berisiko, name="Berisiko", orientation="h", marker_color="#d63a6a",
                        text=[v if v else "" for v in hit.Berisiko], textposition="outside", marker_line=dict(color="#ffffff", width=2))
            fig.add_bar(y=hit.Indikator, x=hit.Waspada, name="Waspada", orientation="h", marker_color="#e9a91c",
                        text=[v if v else "" for v in hit.Waspada], textposition="outside", marker_line=dict(color="#ffffff", width=2))
            fig.update_layout(barmode="group", height=360, margin=dict(l=10, r=30, t=10, b=10),
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font=dict(family="Nunito", color=INK, size=13),
                              legend=dict(orientation="h", y=1.08, x=0))
            fig.update_xaxes(showgrid=True, gridcolor="#f3e1e7", title="Jumlah catin")
            st.plotly_chart(fig, use_container_width=True)
        with g2:
            st.markdown("#### Kategori per kecamatan")
            per = data.groupby(["kecamatan", "kategori"]).size().unstack(fill_value=0)
            for k in ["Siap", "Waspada", "Berisiko"]:
                if k not in per:
                    per[k] = 0
            per = per.loc[per.sum(axis=1).sort_values().index]
            fig = go.Figure()
            for k, w in [("Siap", MINT), ("Waspada", "#e9a91c"), ("Berisiko", "#d63a6a")]:
                fig.add_bar(y=per.index, x=per[k], name=k, orientation="h", marker_color=w,
                            marker_line=dict(color="#ffffff", width=2))
            fig.update_layout(barmode="stack", bargap=0.45, height=360, margin=dict(l=10, r=10, t=10, b=10),
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font=dict(family="Nunito", color=INK, size=13),
                              legend=dict(orientation="h", y=1.08, x=0, traceorder="normal"))
            fig.update_xaxes(showgrid=True, gridcolor="#f3e1e7", title="Jumlah catin", dtick=1)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Daftar catin")
        pilih = st.multiselect("Tampilkan kategori", ["Berisiko", "Waspada", "Siap"],
                               default=["Berisiko", "Waspada", "Siap"])
        tampil = data[data.kategori.isin(pilih)][
            ["waktu_input", "kode", "kecamatan", "usia", "tinggi_cm", "berat_kg", "imt", "lila_cm", "hb",
             "rokok", "jumlah_risiko", "kategori"]].rename(columns={
                "waktu_input": "Waktu input", "kode": "Kode", "kecamatan": "Kecamatan", "usia": "Usia",
                "tinggi_cm": "TB (cm)", "berat_kg": "BB (kg)", "imt": "IMT", "lila_cm": "LiLA (cm)", "hb": "Hb",
                "rokok": "Rokok", "jumlah_risiko": "Jml risiko", "kategori": "Kategori"})
        st.dataframe(tampil, hide_index=True, use_container_width=True)

    st.markdown("#### Simpan & pulihkan data")
    st.caption("Di Streamlit Cloud, data yang diinput bisa hilang saat aplikasi dimulai ulang. "
               "Unduh CSV secara berkala sebagai cadangan, lalu unggah kembali bila perlu.")
    a, b, c = st.columns(3)
    a.download_button("⬇️  Unduh data (CSV)", data.to_csv(index=False).encode("utf-8"),
                      "data_skrining_catin.csv", "text/csv", use_container_width=True, disabled=data.empty)
    up = b.file_uploader("Unggah CSV cadangan", type="csv", label_visibility="collapsed")
    if up is not None and b.button("⬆️  Pulihkan dari CSV", use_container_width=True):
        baru = pd.read_csv(up, dtype={"kode": str})
        if set(KOLOM) <= set(baru.columns):
            simpan_data(baru[KOLOM])
            st.success(f"{len(baru)} data dipulihkan.")
            st.rerun()
        else:
            st.error("Format CSV tidak sesuai. Gunakan file hasil unduhan dari aplikasi ini.")
    if c.button("🗑️  Hapus data terakhir", use_container_width=True, disabled=data.empty):
        simpan_data(data.iloc[:-1])
        st.session_state.pop("terakhir", None)
        st.rerun()

# ---------------------------------------------------------------------------
# TAB 3 - GAMBARAN KOTA (data Disdalduk)
# ---------------------------------------------------------------------------
with tab_kota:
    kota = pd.DataFrame([
        ("Banyumanik", 16136, 766, 15, 46.7), ("Candisari", 8648, 564, 36, 50.0), ("Gajahmungkur", 6301, 403, 17, 94.1),
        ("Gayamsari", 7687, 802, 35, 94.3), ("Genuk", 19962, 1715, 84, 66.7), ("Gunungpati", 14077, 1592, 71, 81.7),
        ("Mijen", 11722, 1219, 21, 85.7), ("Ngaliyan", 19680, 1241, 48, 93.8), ("Pedurungan", 23631, 1479, 17, 76.5),
        ("Semarang Barat", 16735, 952, 38, 81.6), ("Semarang Selatan", 5926, 353, 17, 82.4),
        ("Semarang Tengah", 4143, 327, 73, 83.6), ("Semarang Timur", 5864, 595, 73, 78.1),
        ("Semarang Utara", 14036, 751, 21, 71.4), ("Tembalang", 28054, 1923, 52, 88.5), ("Tugu", 4314, 395, 26, 88.5),
    ], columns=["kecamatan", "pus", "p_lt19", "n_catin", "pct_naik"])
    kota["pct_dini"] = kota.p_lt19 / kota.pus * 100
    prioritas = {"Tembalang", "Mijen"}

    kpi = [("PUS", "206.916", "16 kecamatan", INK), ("Kawin pertama < 19 th", "7,29%", "15.077 PUS", ROSE),
           ("Catin terintervensi DASHAT", "644", "105,6% dari target 610", LAV),
           ("BB catin naik", "79,4%", "511 catin", MINT)]
    for col, (l, v, d, w) in zip(st.columns(4), kpi):
        with col:
            html(f'<div class="kpi"><div class="l">{l}</div><div class="v" style="color:{w}">{v}</div>'
                 f'<div class="d">{d}</div></div>')
    st.write("")

    def warna(v):  # ramp merah muda: makin gelap = makin tinggi % kawin < 19 th
        for batas, bg, fg in [(6, "#ffe3ec", INK), (7, "#ffc2d4", INK), (8.5, "#f78fae", INK),
                              (10, "#e05a85", "#ffffff"), (99, "#b02a57", "#ffffff")]:
            if v < batas:
                return bg, fg

    petak = []
    for _, r in kota.iterrows():
        bg, fg = warna(r.pct_dini)
        ring = "box-shadow:0 0 0 3px #8a74c9 inset;" if r.kecamatan in prioritas else ""
        label = " · prioritas" if r.kecamatan in prioritas else ""
        petak.append(f'<div class="petak" style="background:{bg};color:{fg};{ring}" '
                     f'title="{r.kecamatan}: {fmt(r.p_lt19)} dari {fmt(r.pus)} PUS">'
                     f'<div class="nm">{r.kecamatan}{label}</div><div class="v">{fmt(r.pct_dini, 2)}%</div>'
                     f'<div class="s">BB naik {fmt(r.pct_naik, 1)}% · {r.n_catin} catin</div></div>')
    html(f"""<div class="card"><div style="display:flex;flex-wrap:wrap;justify-content:space-between;gap:10px;align-items:center;margin-bottom:12px">
    <div class="disp" style="font-size:20px;font-weight:700">Perempuan kawin pertama &lt; 19 tahun per kecamatan</div>
    <div class="note">muda → tua = rendah → tinggi (4,75% – 11,31%) · bingkai ungu = kecamatan prioritas</div></div>
    <div class="petak-grid">{''.join(petak)}</div></div>""")
    st.write("")

    st.markdown("#### Luaran DASHAT: persentase catin dengan BB naik")
    d = kota.sort_values("pct_naik")
    fig = go.Figure(go.Bar(
        x=d.pct_naik, y=d.kecamatan, orientation="h", text=[fmt(v, 1) + "%" for v in d.pct_naik],
        textposition="outside", marker_color=[ROSE if v < 70 else (CORAL if v < 85 else MINT) for v in d.pct_naik],
        hovertemplate="<b>%{y}</b><br>BB naik %{x:.1f}%<extra></extra>"))
    fig.update_layout(height=520, margin=dict(l=10, r=40, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Nunito", color=INK, size=13))
    fig.update_xaxes(range=[0, 105], showgrid=True, gridcolor="#f3e1e7", title="% catin terintervensi")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Merah muda < 70% (perlu evaluasi) · oranye 70–84,9% (cukup) · hijau ≥ 85% (baik).")

html('<div class="note" style="margin-top:18px;text-align:center">Sumber gambaran kota: Pendataan Keluarga s.d. 2025 '
     'dan Laporan Intervensi DASHAT 2025, Disdalduk KB Kota Semarang · Dikembangkan oleh Inez Ajeng Puspita, '
     'MBKM FKM UNDIP 💐</div>')
