import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import numpy as np
import streamlit as st
import os

dir_name = os.path.dirname(__file__)

st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="",
    layout="wide",
)

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.05)
WARNA_UTAMA = "#c0392b"
WARNA_SEKUNDER = "#4c72b0"
WARNA_ABU = "#b0b7c3"



@st.cache_data
def load_q1():
    df = pd.read_csv(
        os.path.join(dir_name, "dataset_q1.csv"),
        parse_dates=["order_purchase_timestamp"],
        usecols=[
            "order_id", "order_item_id", "price", "freight_value",
            "product_category_name_english", "customer_id",
            "order_status", "order_purchase_timestamp",
            "customer_state", "review_score",
        ],
    )
    return df


@st.cache_data
def load_q2():
    df = pd.read_csv(
        os.path.join(dir_name, "dataset_q2.csv"),
        parse_dates=[
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
        usecols=[
            "order_id", "customer_id", "order_status",
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
            "is_delivery_anomaly",
            "selisih_estimasi_vs_aktual",
            "review_score", "customer_state",
        ],
    )
    return df


dataset_q1 = load_q1()
dataset_q2 = load_q2()


st.title("E-Commerce Public Dataset Dashboard")
st.caption("Proyek Analisis Data — Nugroho Nur Cahyo · ds128b6y1401")
st.markdown("---")


def create_top5_table(df, sort_by="nilai_penjualan"):
    """Membuat tabel 5 kategori teratas beserta metrik turunan."""
    total_nilai = df["price"].sum()
    skor_rata2 = df["review_score"].mean()

    tabel = (
        df.groupby("product_category_name_english")
        .agg(
            nilai_penjualan=("price", "sum"),
            barang_terjual=("order_item_id", "size"),
            harga_rata2=("price", "mean"),
            harga_median=("price", "median"),
            skor_rata2=("review_score", "mean"),
            jumlah_review=("review_score", "count"),
        )
        .sort_values(sort_by, ascending=False)
        .reset_index()
    )
    tabel["persen_nilai"] = (tabel["nilai_penjualan"] / total_nilai * 100).round(1)
    tabel["persen_review_ada"] = (
        tabel["jumlah_review"] / tabel["barang_terjual"] * 100
    ).round(1)
    tabel["selisih_skor_vs_state"] = (tabel["skor_rata2"] - skor_rata2).round(2)
    tabel["peringkat"] = tabel.index + 1
    return tabel.head(5), total_nilai, skor_rata2


def prepare_q2_analysis(df):
    """Menyiapkan semua metrik yang dibutuhkan untuk visualisasi Q2."""
    q2 = df.drop_duplicates("order_id").copy()
    q2["is_late"] = q2["selisih_estimasi_vs_aktual"] < 0
    q2["hari_telat"] = -q2["selisih_estimasi_vs_aktual"]

    # Metrik umum
    median_selisih = q2["selisih_estimasi_vs_aktual"].median()
    total_pesanan = len(q2)
    jumlah_telat = q2["is_late"].sum()
    persen_telat = jumlah_telat / total_pesanan * 100

    # Drop NaN review untuk analisis skor
    q2_review = q2.dropna(subset=["review_score"]).copy()
    q2_review["review_score"] = q2_review["review_score"].astype(int)

    # Rata-rata skor per status telat
    rata = q2_review.groupby("is_late")["review_score"].agg(["mean", "count"]).sort_index()
    selisih_skor = rata.loc[False, "mean"] - rata.loc[True, "mean"] if True in rata.index else 0

    # Persentase telat per skor
    telat_df = q2_review[q2_review["is_late"]]
    total_per_skor = q2_review.groupby("review_score").size()
    jumlah_telat_per_skor = telat_df.groupby("review_score").size().reindex(total_per_skor.index, fill_value=0)
    persen_per_skor = jumlah_telat_per_skor / total_per_skor * 100

    # Kelompok keterlambatan
    batas = [0, 2, 4, 7, 14, 30, np.inf]
    label_kel = ["0-2", "2-4", "4-7", "7-14", "14-30", ">30"]
    kel = telat_df.assign(kelompok=pd.cut(telat_df["hari_telat"], bins=batas, labels=label_kel))
    per_kel = kel.groupby("kelompok", observed=True)["review_score"].agg(["mean", "count"])

    return {
        "median_selisih": median_selisih,
        "total_pesanan": total_pesanan,
        "jumlah_telat": jumlah_telat,
        "persen_telat": persen_telat,
        "rata": rata,
        "selisih_skor": selisih_skor,
        "total_per_skor": total_per_skor,
        "jumlah_telat_per_skor": jumlah_telat_per_skor,
        "persen_per_skor": persen_per_skor,
        "per_kel": per_kel,
    }



tab1, tab2 = st.tabs([
    "Pertanyaan 1 — Penjualan & Kepuasan per Kategori",
    "Pertanyaan 2 — Keterlambatan & Review Score",
])


with tab1:
    st.subheader("Top 5 Kategori Produk: Penjualan & Kepuasan Pelanggan")
    st.markdown(
        "Analisis total penjualan produk dan rata-rata tingkat kepuasan pelanggan "
        "untuk 5 kategori produk teratas, berdasarkan tanggal pembelian."
    )

    # ── SIDEBAR FILTERS ──
    with st.container():
        col_f1, col_f2, col_f3 = st.columns([1, 1, 1])

        # Rentang tanggal (dari order_purchase_timestamp)
        min_date_q1 = dataset_q1["order_purchase_timestamp"].min().date()
        max_date_q1 = dataset_q1["order_purchase_timestamp"].max().date()

        with col_f1:
            date_range_q1 = st.date_input(
                "Rentang Tanggal Pembelian",
                value=(pd.Timestamp("2018-06-01").date(), pd.Timestamp("2018-08-31").date()),
                min_value=min_date_q1,
                max_value=max_date_q1,
                key="date_q1",
            )

        # Filter state
        all_states_q1 = sorted(dataset_q1["customer_state"].dropna().unique().tolist())
        with col_f2:
            selected_state_q1 = st.selectbox(
                "State (Wilayah)",
                options=all_states_q1,
                index=all_states_q1.index("SP"),
                key="state_q1",
            )

        # Sort by
        sort_options = {
            "Volume Barang": "barang_terjual",
            "Total Harga": "nilai_penjualan",
            "Rata-rata Skor Review": "skor_rata2",
        }
        with col_f3:
            sort_label = st.selectbox(
                "Urutkan Berdasarkan",
                options=list(sort_options.keys()),
                index=1,
                key="sort_q1",
            )
        sort_col = sort_options[sort_label]

    # ── APPLY FILTERS ──
    if isinstance(date_range_q1, tuple) and len(date_range_q1) == 2:
        start_q1, end_q1 = pd.Timestamp(date_range_q1[0]), pd.Timestamp(date_range_q1[1]) + pd.Timedelta(days=1)
    else:
        start_q1 = pd.Timestamp(date_range_q1)
        end_q1 = pd.Timestamp(date_range_q1) + pd.Timedelta(days=1)

    mask_q1 = (
        (dataset_q1["order_status"] == "delivered")
        & (dataset_q1["customer_state"] == selected_state_q1)
        & (dataset_q1["order_purchase_timestamp"] >= start_q1)
        & (dataset_q1["order_purchase_timestamp"] < end_q1)
    )
    data_q1 = dataset_q1[mask_q1].copy()

    if data_q1.empty:
        st.warning("Tidak ada data untuk filter yang dipilih. Silakan ubah filter.")
    else:
        top5, total_nilai, skor_rata2_state = create_top5_table(data_q1, sort_by=sort_col)

        # ── METRIC CARDS ──
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Nilai Penjualan", f"R$ {total_nilai:,.0f}")
        m2.metric("Total Barang Terjual", f"{len(data_q1):,}")
        m3.metric("Rata-rata Skor Review", f"{skor_rata2_state:.2f}")
        persen_top5 = top5["nilai_penjualan"].sum() / total_nilai * 100 if total_nilai > 0 else 0
        m4.metric("Kontribusi Top 5", f"{persen_top5:.1f}%")

        st.markdown("---")

        # ── VISUALISASI ──
        plot_q1 = top5.iloc[::-1]
        warna_q1 = [WARNA_UTAMA if i == len(plot_q1) - 1 else WARNA_ABU for i in range(len(plot_q1))]

        fig, axes = plt.subplots(1, 2, figsize=(16, 5), sharey=True)

        # Chart A: Nilai penjualan
        axes[0].barh(
            plot_q1["product_category_name_english"],
            plot_q1["nilai_penjualan"],
            color=warna_q1,
        )
        for i, (nilai, barang, harga) in enumerate(
            zip(plot_q1["nilai_penjualan"], plot_q1["barang_terjual"], plot_q1["harga_rata2"])
        ):
            axes[0].text(
                nilai, i,
                f"  {nilai / 1000:,.1f} rb | {barang:,} brg | R$ {harga:,.0f}/brg",
                va="center", fontsize=9,
            )
        axes[0].set_xlim(0, plot_q1["nilai_penjualan"].max() * 1.8)
        axes[0].set_xlabel("Nilai Penjualan (R$)")
        axes[0].set_title("A. Nilai Penjualan, Jumlah Barang & Harga Rata-rata")
        axes[0].xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}k"))

        # Chart B: Skor review
        axes[1].scatter(
            plot_q1["skor_rata2"],
            plot_q1["product_category_name_english"],
            s=120, color=warna_q1, zorder=3, edgecolors="white", linewidth=0.5,
        )
        axes[1].axvline(
            skor_rata2_state, ls="--", color="black", alpha=0.6,
            label=f"Rata-rata {selected_state_q1} ({skor_rata2_state:.2f})",
        )
        for i, skor in enumerate(plot_q1["skor_rata2"]):
            axes[1].text(skor, i + 0.22, f"{skor:.2f}", ha="center", fontsize=9)
        x_min = max(1, plot_q1["skor_rata2"].min() - 0.3)
        x_max = min(5, plot_q1["skor_rata2"].max() + 0.3)
        axes[1].set_xlim(x_min, x_max)
        axes[1].grid(axis="x", alpha=0.3)
        axes[1].set_xlabel("Rata-rata Skor Review (1-5)")
        axes[1].set_title("B. Kepuasan Pelanggan per Kategori")
        axes[1].legend(loc="lower right", fontsize=8)

        fig.suptitle(
            f"5 Kategori dengan {sort_label} Tertinggi di {selected_state_q1}, "
            f"{date_range_q1[0].strftime('%d %b %Y')} — {date_range_q1[1].strftime('%d %b %Y')}",
            fontsize=13, fontweight="bold",
        )
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        # ── TABEL DETAIL ──
        with st.expander("Lihat Tabel Detail Top 5"):
            display_cols = [
                "peringkat", "product_category_name_english",
                "nilai_penjualan", "barang_terjual", "harga_rata2",
                "skor_rata2", "persen_nilai", "selisih_skor_vs_state",
            ]
            st.dataframe(
                top5[display_cols].rename(columns={
                    "peringkat": "#",
                    "product_category_name_english": "Kategori",
                    "nilai_penjualan": "Total Penjualan (R$)",
                    "barang_terjual": "Barang Terjual",
                    "harga_rata2": "Harga Rata² (R$)",
                    "skor_rata2": "Skor Rata²",
                    "persen_nilai": "% Nilai",
                    "selisih_skor_vs_state": f"Δ Skor vs {selected_state_q1}",
                }).style.format({
                    "Total Penjualan (R$)": "{:,.0f}",
                    "Barang Terjual": "{:,}",
                    "Harga Rata² (R$)": "{:,.0f}",
                    "Skor Rata²": "{:.2f}",
                    "% Nilai": "{:.1f}%",
                    f"Δ Skor vs {selected_state_q1}": "{:+.2f}",
                }),
                use_container_width=True,
                hide_index=True,
            )


# ═════════════════════════════════════════════
# TAB 2 — KETERLAMBATAN & REVIEW
# ═════════════════════════════════════════════
with tab2:
    st.subheader("Keterlambatan Pengiriman & Dampaknya terhadap Review Score")
    st.markdown(
        "Analisis median selisih estimasi vs aktual, persentase pesanan terlambat, "
        "dan hubungan keterlambatan dengan rata-rata review score, berdasarkan tanggal pesanan diterima."
    )

    # ── FILTERS ──
    with st.container():
        col_g1, col_g2 = st.columns([1, 1])

        # Rentang tanggal (dari order_delivered_customer_date)
        valid_dates_q2 = dataset_q2["order_delivered_customer_date"].dropna()
        min_date_q2 = valid_dates_q2.min().date()
        max_date_q2 = valid_dates_q2.max().date()

        with col_g1:
            date_range_q2 = st.date_input(
                "Rentang Tanggal Pesanan Diterima",
                value=(pd.Timestamp("2018-01-01").date(), pd.Timestamp("2018-08-31").date()),
                min_value=min_date_q2,
                max_value=max_date_q2,
                key="date_q2",
            )

        all_states_q2 = sorted(dataset_q2["customer_state"].dropna().unique().tolist())
        with col_g2:
            selected_state_q2 = st.selectbox(
                "State (Wilayah)",
                options=all_states_q2,
                index=all_states_q2.index("SP"),
                key="state_q2",
            )

    # ── APPLY FILTERS ──
    if isinstance(date_range_q2, tuple) and len(date_range_q2) == 2:
        start_q2, end_q2 = pd.Timestamp(date_range_q2[0]), pd.Timestamp(date_range_q2[1]) + pd.Timedelta(days=1)
    else:
        start_q2 = pd.Timestamp(date_range_q2)
        end_q2 = pd.Timestamp(date_range_q2) + pd.Timedelta(days=1)

    tanggal_q2 = dataset_q2["order_delivered_customer_date"]
    mask_q2 = (
        (dataset_q2["order_status"] == "delivered")
        & (dataset_q2["customer_state"] == selected_state_q2)
        & (tanggal_q2 >= start_q2)
        & (tanggal_q2 < end_q2)
        & (dataset_q2["is_delivery_anomaly"] == False)
    )
    data_q2 = dataset_q2[mask_q2].copy()

    if data_q2.empty:
        st.warning("Tidak ada data untuk filter yang dipilih. Silakan ubah filter.")
    else:
        metrics = prepare_q2_analysis(data_q2)

        # ── METRIC CARDS ──
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Pesanan (Unik)", f"{metrics['total_pesanan']:,}")
        m2.metric("Median Selisih Estimasi", f"+{metrics['median_selisih']:.1f} hari")
        m3.metric("Pesanan Terlambat", f"{metrics['jumlah_telat']:,} ({metrics['persen_telat']:.1f}%)")
        if True in metrics["rata"].index and False in metrics["rata"].index:
            m4.metric(
                "Δ Skor (Tepat vs Telat)",
                f"{metrics['selisih_skor']:.2f} poin",
            )
        else:
            m4.metric("Δ Skor", "N/A")

        st.markdown("---")

        # ── VISUALISASI ──
        fig2, axes2 = plt.subplots(1, 3, figsize=(19, 5.5))

        # Chart A: Rata-rata skor telat vs tidak
        rata = metrics["rata"]
        if True in rata.index and False in rata.index:
            labels_a = ["Tepat/Lebih Cepat", "Terlambat"]
            values_a = [rata.loc[False, "mean"], rata.loc[True, "mean"]]
            counts_a = [rata.loc[False, "count"], rata.loc[True, "count"]]
            colors_a = [WARNA_SEKUNDER, WARNA_UTAMA]
        elif False in rata.index:
            labels_a = ["Tepat/Lebih Cepat"]
            values_a = [rata.loc[False, "mean"]]
            counts_a = [rata.loc[False, "count"]]
            colors_a = [WARNA_SEKUNDER]
        else:
            labels_a = ["Terlambat"]
            values_a = [rata.loc[True, "mean"]]
            counts_a = [rata.loc[True, "count"]]
            colors_a = [WARNA_UTAMA]

        batang = axes2[0].bar(labels_a, values_a, color=colors_a, width=0.5)
        for b, m_val, n_val in zip(batang, values_a, counts_a):
            axes2[0].text(
                b.get_x() + b.get_width() / 2, m_val,
                f"{m_val:.2f}\n(n={n_val:,})",
                ha="center", va="bottom", fontsize=9,
            )
        axes2[0].set_ylim(1, 5.5)
        axes2[0].set_ylabel("Rata-rata Skor Review")
        axes2[0].set_title(
            f"A. Skor Review: Telat vs Tidak\n(selisih {metrics['selisih_skor']:.2f} poin)"
        )

        # Chart B: Persentase telat per skor
        persen = metrics["persen_per_skor"]
        total_per_skor = metrics["total_per_skor"]
        jumlah_telat_per_skor = metrics["jumlah_telat_per_skor"]

        axes2[1].bar(persen.index.astype(str), persen.values, color=WARNA_UTAMA, width=0.5)
        for skor in persen.index:
            if persen[skor] > 0:
                axes2[1].text(
                    str(skor), persen[skor],
                    f"{persen[skor]:.0f}%\n({jumlah_telat_per_skor[skor]:,}/{total_per_skor[skor]:,})",
                    ha="center", va="bottom", fontsize=8,
                )
        axes2[1].set_ylim(0, max(persen.max() * 1.35, 1))
        axes2[1].set_xlabel("Skor Review")
        axes2[1].set_ylabel("% Pesanan Terlambat")
        axes2[1].set_title("B. % Pesanan Terlambat per Skor Review")

        # Chart C: Skor per kelompok keterlambatan
        per_kel = metrics["per_kel"]
        if not per_kel.empty:
            x_kel = np.array(per_kel.index.astype(str))
            y_kel = per_kel["mean"].values
            kecil = (per_kel["count"] < 100).values

            axes2[2].plot(x_kel, y_kel, "-", color=WARNA_UTAMA, linewidth=1.5)
            axes2[2].scatter(x_kel[~kecil], y_kel[~kecil], color=WARNA_UTAMA, zorder=3, s=60)
            axes2[2].scatter(
                x_kel[kecil], y_kel[kecil],
                facecolors="white", edgecolors=WARNA_UTAMA, zorder=3, s=60,
                label="Sampel < 100",
            )
            for i, (m_val, n_val) in enumerate(zip(y_kel, per_kel["count"])):
                axes2[2].text(i, m_val + 0.15, f"n={n_val:,}", ha="center", fontsize=8)
            if False in rata.index:
                axes2[2].axhline(
                    rata.loc[False, "mean"], ls="--", color=WARNA_SEKUNDER,
                    label="Rata-rata pesanan tidak telat",
                )
            axes2[2].set_ylim(1, 5.2)
            axes2[2].set_xlabel("Hari Terlambat")
            axes2[2].set_ylabel("Rata-rata Skor Review")
            axes2[2].set_title("C. Skor Review per Lama Keterlambatan")
            axes2[2].legend(loc="lower right", fontsize=7)
        else:
            axes2[2].text(0.5, 0.5, "Tidak ada pesanan terlambat", transform=axes2[2].transAxes,
                          ha="center", va="center", fontsize=12, color="gray")
            axes2[2].set_title("C. Skor Review per Lama Keterlambatan")

        fig2.suptitle(
            f"Keterlambatan Pengiriman & Review Score — Pesanan Delivered di {selected_state_q2}, "
            f"{date_range_q2[0].strftime('%d %b %Y')} — {date_range_q2[1].strftime('%d %b %Y')}",
            fontsize=13, fontweight="bold",
        )
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

        # ── INSIGHT RINGKAS ──
        with st.expander("Insight Ringkas"):
            st.markdown(f"""
**Ringkasan untuk {selected_state_q2}:**

- **Median selisih estimasi:** +{metrics['median_selisih']:.1f} hari lebih awal dari estimasi.
- **Pesanan terlambat:** {metrics['jumlah_telat']:,} dari {metrics['total_pesanan']:,} pesanan ({metrics['persen_telat']:.1f}%).
- **Selisih skor:** Pesanan terlambat memiliki skor rata-rata **{metrics['selisih_skor']:.2f} poin lebih rendah** dibanding pesanan tepat waktu.
- Keterlambatan **bukan satu-satunya** penyebab skor rendah — sebagian besar pesanan berskor 1 justru tidak terlambat.
- Semakin lama keterlambatan, skor semakin turun drastis, terutama setelah melewati 4 hari.
            """)

st.markdown("---")
st.caption("© 2026 Nugroho Nur Cahyo — Proyek Akhir Fundamental Analisis Data · Dicoding")
