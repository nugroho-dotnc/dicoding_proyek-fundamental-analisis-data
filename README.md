# Proyek Analisis Data: E-Commerce Public Dataset

**Nama:** Nugroho Nur Cahyo  
**Email:** nugroho.nur.cahyo.career@gmail.com  
**ID Dicoding:** nugroho-dotnc

## Deskripsi Proyek

Proyek ini menganalisis dataset publik e-commerce Brasil untuk menjawab dua pertanyaan bisnis:

1. **Pertanyaan 1:** Berapa total penjualan produk dan rata-rata tingkat kepuasan pelanggan untuk 5 kategori produk teratas di suatu wilayah pada rentang waktu tertentu?
2. **Pertanyaan 2:** Berapa median selisih antara tanggal estimasi dan tanggal sampai sebenarnya, berapa persen pesanan yang terlambat, dan apakah keterlambatan menurunkan rata-rata review score?

Hasil analisis divisualisasikan dalam dashboard interaktif menggunakan **Streamlit**.

## Struktur Proyek

```
├── dashboard/
│   ├── dashboard.py          # Aplikasi Streamlit dashboard
│   ├── dataset_q1.csv        # Dataset hasil olahan untuk Pertanyaan 1
│   └── dataset_q2.csv        # Dataset hasil olahan untuk Pertanyaan 2
├── datasets/                  # Dataset mentah (raw)
│   ├── customers_dataset.csv
│   ├── orders_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── products_dataset.csv
│   ├── product_category_name_translation.csv
│   ├── sellers_dataset.csv
│   └── geolocation_dataset.csv
├── proyek_analisis_data_final.ipynb   # Notebook analisis data
├── requirements.txt                    # Daftar library Python
└── README.md                           # Dokumentasi proyek (file ini)
```

## Setup Environment

### Prasyarat

- **Python** 3.9 atau lebih baru
- **pip** (Python package manager)

### 1. Clone / Download Proyek

Pastikan seluruh file proyek sudah tersedia di komputer lokal.

### 2. Buat Virtual Environment (opsional, direkomendasikan)

```bash
# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Library yang digunakan:

| Library      | Keterangan                        |
|-------------|-----------------------------------|
| `streamlit`  | Framework dashboard interaktif    |
| `pandas`     | Manipulasi dan analisis data      |
| `matplotlib` | Visualisasi data (backend chart)  |
| `seaborn`    | Visualisasi statistik             |
| `numpy`      | Operasi numerik                   |

## Menjalankan Dashboard Streamlit

### 1. Pindah ke Direktori Dashboard

```bash
cd dashboard
```

### 2. Jalankan Streamlit

```bash
streamlit run dashboard.py
```

### 3. Buka di Browser

Setelah perintah dijalankan, terminal akan menampilkan URL seperti:

```
Local URL: http://localhost:8501
```

Buka URL tersebut di browser untuk melihat dashboard.

## Fitur Dashboard

### Tab 1 — Penjualan & Kepuasan per Kategori

| Filter                 | Keterangan                                              |
|-----------------------|--------------------------------------------------------|
| Rentang Tanggal       | Berdasarkan tanggal pembelian (`order_purchase_timestamp`) |
| State                 | Wilayah pelanggan (contoh: SP, RJ, MG, dll.)           |
| Urutkan Berdasarkan   | Volume Barang, Total Harga, atau Rata-rata Skor Review  |

**Visualisasi:**
- Horizontal bar chart — nilai penjualan + jumlah barang + harga rata-rata
- Scatter plot — rata-rata skor review per kategori vs rata-rata state

### Tab 2 — Keterlambatan & Review Score

| Filter            | Keterangan                                                    |
|-------------------|---------------------------------------------------------------|
| Rentang Tanggal   | Berdasarkan tanggal pesanan diterima (`order_delivered_customer_date`) |
| State             | Wilayah pelanggan                                              |

**Visualisasi:**
- Bar chart — rata-rata skor review (telat vs tidak telat)
- Bar chart — persentase pesanan terlambat per skor review
- Line chart — rata-rata skor review per kelompok lama keterlambatan
