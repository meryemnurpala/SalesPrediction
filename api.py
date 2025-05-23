from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sklearn.model_selection import train_test_split  
from sklearn.ensemble import RandomForestRegressor 
import pandas as pd

# FastAPI uygulamasını başlat
app = FastAPI()

# Model dosyasının var olup olmadığını kontrol et
model_path = "optimized_xgb.pkl"
if not os.path.exists(model_path):
    raise RuntimeError(f"❌ Model dosyası bulunamadı: {model_path}")

try:
    model = joblib.load(model_path)
except Exception as e:
    raise RuntimeError(f"❌ Model yüklenirken hata oluştu: {e}")

# PostgreSQL bağlantı bilgileri
DB_USERNAME = "postgres"  # Kullanıcı adını yaz
DB_PASSWORD = "123456"  # PostgreSQL şifreni yaz
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "northwind"

# SQLAlchemy bağlantı dizesi
DATABASE_URL = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# Veritabanına bağlanmak için yardımcı fonksiyon
def get_product_details(db: Session, product_id: int):
    result = db.execute(
        text("SELECT product_name, unit_price, category_id FROM products WHERE product_id = :product_id"),
        {"product_id": product_id},
    ).fetchone()
    
    if result:
        return result  # (product_name, unit_price, category_id)
    return None

# Giriş verisi için Pydantic modeli
class PredictionInput(BaseModel):
    product_id: int
    year: int
    month: int
    quantity: int
    week: int
    customer_id: int  # Yeni eklenen müşteri bilgisi

@app.get("/products")
def get_products():
    try:
        with Session(engine) as session:
            # 'text' fonksiyonu ile sorguyu metin olarak belirtelim
            result = session.execute(
                text("SELECT product_id, product_name FROM products")
            ).fetchall()
            
            return [{"product_id": r[0], "product_name": r[1]} for r in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hata oluştu: {e}")
    
# /predict uç noktası: Tahmin yapılmasını sağlar
@app.post("/predict")
def predict_sales(data: PredictionInput):
    try:
        # Veritabanı bağlantısı
        with Session(engine) as session:
            # Ürün bilgilerini al
            product_details = get_product_details(session, data.product_id)

            if not product_details:
                raise HTTPException(status_code=404, detail="Product not found in the database.")
            
            product_name, unit_price, category_id = product_details

            # Modelin beklediği veri formatına uygun hale getirme
            is_weekend = 1 if data.month in [6, 7] else 0  # Hafta sonu kontrolü
            prev_month_diff = 5  # Örnek bir değer
            rolling_avg_3months = 48.7  # Örnek bir değer

            input_data = np.array([[  
                data.year,
                data.month,
                data.week,
                data.product_id,
                unit_price,
                category_id,
                is_weekend,
                prev_month_diff,
                rolling_avg_3months
            ]], dtype=np.float32)

            # Tahmini satış miktarını modelden al
            prediction = model.predict(input_data)

            return {
                "product_id": data.product_id,
                "year": data.year,
                "month": data.month,
                "predicted_sales": round(float(prediction[0]), 2)
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hata oluştu: {e}")

# /retrain uç noktası: Modeli yeniden eğitir (opsiyonel)
@app.post("/retrain")
def retrain_model():
    try:
        # Veritabanından yeni veriyi alalım
        engine = create_engine(DATABASE_URL)
        with Session(engine) as session:
            # Burada, modelin eğitilmesi için gerekli verileri alıyoruz
            query = text("""
                SELECT 
                    od.product_id, 
                    p.product_name, 
                    p.unit_price, 
                    od.quantity, 
                    o.order_date
                FROM order_details od
                JOIN orders o ON od.order_id = o.order_id
                JOIN products p ON od.product_id = p.product_id
            """)
            data = pd.read_sql(query, session.bind)
        
        # Veriyi işleyelim (Örneğin: Yıl ve Ay bilgilerini eklemek)
        data["order_date"] = pd.to_datetime(data["order_date"])
        data["year"] = data["order_date"].dt.year
        data["month"] = data["order_date"].dt.month
        data.drop(columns=["order_date"], inplace=True)

        # Özellik ve hedef değişkenleri ayıralım
        X = data[["year", "month", "product_id", "unit_price"]]  # Özellikler
        y = data["quantity"]  # Hedef değişken (satış miktarı)

        # Veriyi eğitim ve test setlerine ayıralım
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Modeli eğitelim (RandomForest örneği)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Modeli kaydedelim
        joblib.dump(model, "optimized_model.pkl")

        return {"message": "Model başarıyla yeniden eğitildi ve kaydedildi."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hata oluştu: {e}")

@app.get("/")
def home():
    return {"message": "Sales Prediction API is running!"}
