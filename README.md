**Analisis Penjualan Produk Adidas untuk Optimalisasi Strategi Pemasaran**

## Deskripsi
Proyek ini merupakan Arsitektur sebagai Data Engineer dan sekaligus Analisis nya. Dalam proyek ini, dilakukan proses ETL otomatis menggunakan Apache Airflow, validasi data menggunakan Great Expectations, penyimpanan data dalam PostgreSQL, pemrosesan data untuk dikirim ke Elasticsearch, serta visualisasi eksploratif menggunakan Kibana.

Dataset yang digunakan adalah data penjualan Adidas dari [Kaggle](https://www.kaggle.com/datasets/heemalichaudhari/adidas-sales-dataset). Dataset ini berisi informasi penjualan produk seperti retailer, wilayah penjualan, harga, margin keuntungan, dan unit yang terjual.

---

## Tujuan Proyek
Menganalisis karakteristik penjualan produk Adidas untuk memberikan rekomendasi bisnis kepada tim marketing terkait:
- Wilayah dengan performa penjualan terbaik
- Produk dengan margin keuntungan tinggi
- Distribusi penjualan antar retailer
- Tren harga terhadap jumlah unit terjual

---

## Dataset
- **Sumber**: [Kaggle - Adidas Sales Dataset](https://www.kaggle.com/datasets/heemalichaudhari/adidas-sales-dataset)
- **Nama File Raw**: `Fajar_Dawud_data_raw.csv`
- **Jumlah Kolom**: >10
- **Jenis Kolom**: Campuran kategorikal dan numerikal
- **Format Kolom**: Sesuai ketentuan (huruf kapital dan campuran)

---

## Arsitektur Proyek
Pipeline data dibangun menggunakan Apache Airflow dengan 3 task utama:

1. **Fetch from PostgreSQL**  
   Menarik data mentah dari database lokal PostgreSQL.
2. **Data Cleaning**  
   - Menghapus duplikat  
   - Menormalisasi nama kolom (lowercase & underscore)  
   - Handling missing values
3. **Post to Elasticsearch**  
   Memasukkan data bersih ke Elasticsearch.

Jadwal pipeline:
- Dimulai: 1 November 2024
- Frekuensi: Setiap Sabtu, pukul 09:10–09:30 WIB, tiap 10 menit

---

## Validasi Data - Great Expectations
1. Expect Column Values to Be Unique
Kolom: retailer_invoice_date

Tujuan: Memastikan kombinasi retailer dan tanggal invoice tidak duplikat.

2. Expect Column Values to Be in Set
Kolom: region

Nilai diizinkan: 'Central', 'East', 'West', 'South'

Tujuan: Validasi konsistensi kategori wilayah.

3. Expect Column Values to Be Between
Kolom: price

Rentang: 10 sampai 150

Kolom: units_sold

Rentang: 0 sampai 1000

Tujuan: Memastikan nilai harga dan unit tidak anomali.

4. Expect Column Values to Not Be Null
Kolom: product, retailer, region, invoice_date, units_sold, price, total_sales, operating_margin

Tujuan: Memastikan tidak ada missing value pada kolom penting.

5. Expect Column Values to Match Regex
Kolom: invoice_date

Regex: \d{4}-\d{2}-\d{2} (format tanggal YYYY-MM-DD)

Tujuan: Validasi format tanggal.

6. Expect Column Values to Be of Type
Kolom: price, units_sold, total_sales, operating_margin harus numerik (float atau int)

Kolom: invoice_date harus bertipe tanggal (datetime64)

7. Expect Table Row Count to Be Between
Tujuan: Memastikan ukuran data tidak menyimpang drastis dari jumlah baris yang diharapkan (antara 500 dan 10.000 baris).
Notebook validasi disimpan sebagai:
`Fajar_Dawud_GX.ipynb`

---

## Visualisasi - Kibana
EDA dilakukan melalui Kibana dengan minimum 6 visualisasi berikut:
1. **Pie Chart** - Penjualan berdasarkan wilayah
2. **Horizontal Bar Plot** - Produk dan jumlah unit yang terjual
3. **Heatmap** - Lokasi terjualnya unit
4. **Vertikal Barplot** - Metode penjualan yang paling menguntungkan penjualan
5. **Line Chart** - Profit dari masing-masing unit yang terjual

Markdown tambahan:
- Kesimpulan & rekomendasi bisnis berdasarkan insight dan referensi

---

## File & Struktur Folder
```bash
Adidas-Sales-Analyst-Data-Engineer-/
├── Fajar_Dawud_data_raw.csv
├── Fajar_Dawud_data_clean.csv
├── Fajar_Dawud_DAG.py
├── Fajar_Dawud_DAG_graph.jpg
├── Fajar_Dawud_ddl.txt
├── Fajar_Dawud_GX.ipynb
├── Fajar_Dawud_conceptual.txt
├── images/
│   ├── plot & insight 01.png
│   ├── plot & insight 02.png
│   ├── plot & insight 03.png
│   ├── plot & insight 04.png
│   ├── plot & insight 05.png
│   └── kesimpulan.png
└── README.md