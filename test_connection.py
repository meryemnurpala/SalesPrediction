import pandas as pd
from sqlalchemy import create_engine

# PostgreSQL bağlantı bilgileri
DB_USERNAME = "kullanıcı adınız"  # Kullanıcı adını yaz
DB_PASSWORD = "sifreniz"  # PostgreSQL şifreni yaz
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "northwind"

# SQLAlchemy bağlantı dizesi
DATABASE_URL = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# Sipariş ve sipariş detayları tablolarını birleştirelim
query = """
SELECT 
    od.product_id,
    p.product_name,
    p.unit_price,
    od.quantity,
    o.order_date
FROM order_details od
JOIN orders o ON od.order_id = o.order_id
JOIN products p ON od.product_id = p.product_id
"""

df = pd.read_sql(query, engine)

# Tarih sütununu datetime formatına çevir
df["order_date"] = pd.to_datetime(df["order_date"])

# Yıl ve Ay bilgilerini ekleyelim
df["year"] = df["order_date"].dt.year
df["month"] = df["order_date"].dt.month

# Gereksiz sütunu (tarih) kaldıralım
df.drop(columns=["order_date"], inplace=True)

# Eksik değerleri kontrol edelim
#print(df.isnull().sum())

# Temizlenmiş veriyi gösterelim
#print(df.head())

# Aylık ürün satışlarını hesapla
monthly_sales = df.groupby(["year", "month", "product_id", "product_name"])["quantity"].sum().reset_index()

# Veriyi görelim
print(monthly_sales.head())

