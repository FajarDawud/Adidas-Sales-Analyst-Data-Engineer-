from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import psycopg2 as db 
import pandas as pd
import datetime as dt
from datetime import timedelta
from elasticsearch import Elasticsearch

'''
=================================================
Adidas Dataset Analyst

Nama  : Fajar Dawud

Program ini dibuat untuk melakukan automatisasi transform dan load data 
dari PostgreSQL ke ElasticSearch. Adapun dataset yang dipakai adalah 
dataset mengenai penjualan di Perusahaan Adidas.
=================================================
'''

def fetch_from_postgresql():
    """
    Mengambil data dari PostgreSQL, mendeteksi header secara dinamis,
    membersihkan data, dan mengembalikannya dalam bentuk DataFrame.

    Return:
        df (DataFrame): Data yang sudah dibersihkan.
    """
    # Koneksi ke PostgreSQL
    conn_string = "dbname='airflow' host='postgres' user='airflow' password='airflow' port='5432'"
    conn = db.connect(conn_string)

    # Mengambil data menggunakan pandas
    df = pd.read_sql('SELECT * FROM public.table_m3', conn)
    df.to_csv('/opt/airflow/dags/P2M3_fajar_dawud_data_raw.csv', index = False)
    print("======Data Saved======")
def clean_data_raw():
    # Deteksi baris header dinamis
    df = pd.read_csv('/opt/airflow/dags/P2M3_fajar_dawud_data_raw.csv')
    header_row_idx = None
    for i in range(min(10, len(df))):
        row = df.iloc[i]
        if row.isnull().sum() < len(row) // 2:
            header_row_idx = i
            break

    if header_row_idx is None:
        raise ValueError("Tidak ditemukan baris yang cocok untuk header.")

    new_header = df.iloc[header_row_idx].fillna("unknown").astype(str)
    df = df.iloc[header_row_idx + 1:].copy()
    df.columns = new_header
    df = df.reset_index(drop=True)

    # Hapus kolom yang tidak bermakna
    df = df.loc[:, ~df.columns.str.lower().str.contains("unknown")]
    df = df.dropna(axis=1, how="all")
    df = df.loc[:, ~(df == 'unknown').all()]

    # Normalisasi nama kolom
    df.columns = (
        df.columns
        .str.lower()
        .str.strip()
        .str.replace(" ", "_")
        .str.replace(r"[^\w\s]", "", regex=True)
    )

    # Hapus duplikat
    df = df.drop_duplicates()

    # Konversi 'invoice_date' ke datetime
    if 'invoice_date' in df.columns:
        df['invoice_date'] = pd.to_datetime(df['invoice_date'], errors='coerce')

    # Konversi kolom numerik & isi missing values
    for col in df.columns:
        if col == 'invoice_date':
            continue
        try:
            col_data = pd.to_numeric(df[col], errors='coerce')
            if col_data.notnull().sum() > 0:
                df[col] = col_data.fillna(col_data.median())
            else:
                df[col] = df[col].fillna("Unknown")
        except Exception as e:
            print(f"Kolom '{col}' error saat dibersihkan: {e}")

    print("Kolom akhir:", df.columns.tolist())
    df.to_csv('/opt/airflow/dags/P2M3_fajar_dawud_data_clean.csv', index = False)

def post_to_elasticsearch():
    """
    Mengirim data clean dari CSV ke Elasticsearch

    """
    es = Elasticsearch("http://elasticsearch:9200")

    # Memeriksa koneksi Elasticsearch
    if not es.ping():
        raise ConnectionError("Gagal terhubung ke Elasticsearch.")
    else:
        print("Berhasil terhubung ke Elasticsearch.")

    df = pd.read_csv('/opt/airflow/dags/P2M3_fajar_dawud_data_clean.csv')
    for i, r in df.iterrows():
        doc = r.to_json()
        res = es.index(index = "fajar_m3", doc_type = 'doc', body = doc)
        print(res)
default_args = {
    'owner': 'fajar',
    'start_date': dt.datetime(2024, 11, 2, 9, 10, 0) - timedelta(hours=7),
    'retries': 1,
    'retry_delay': dt.timedelta(minutes=2),
}

with DAG("M3CleanData",
         default_args = default_args,
         schedule_interval = '10-30/10 9 * * 6',
         catchup = True
         ) as dag:
    FetchfromPostgreSQL = PythonOperator(task_id = 'get', python_callable = fetch_from_postgresql)
    DataCleaning = PythonOperator(task_id = 'clean', python_callable = clean_data_raw)
    PosttoElasticsearch = PythonOperator(task_id = 'insert', python_callable = post_to_elasticsearch)

FetchfromPostgreSQL >> DataCleaning >> PosttoElasticsearch