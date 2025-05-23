import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import xgboost as xgb
import numpy as np
import joblib

# PostgreSQL bağlantısı
DB_USERNAME = "kullanıcı adınız"
DB_PASSWORD = "sifreniz"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "database adınız"

DATABASE_URL = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# 📌 **Veriyi çekme**
query = """
SELECT 
    EXTRACT(YEAR FROM o.order_date) AS year,
    EXTRACT(MONTH FROM o.order_date) AS month,
    EXTRACT(WEEK FROM o.order_date) AS week,
    EXTRACT(DOW FROM o.order_date) AS weekday,
    od.product_id,
    p.product_name,
    p.unit_price,
    c.category_id,
    SUM(od.quantity) AS quantity
FROM order_details od
JOIN orders o ON od.order_id = o.order_id
JOIN products p ON od.product_id = p.product_id
JOIN categories c ON p.category_id = c.category_id
GROUP BY year, month, week, weekday, od.product_id, p.product_name, p.unit_price, c.category_id
ORDER BY year, month, week
"""

df = pd.read_sql(query, engine)

# 📌 **1. Aykırı Değerleri Temizleme**
Q1 = df["quantity"].quantile(0.05)
Q3 = df["quantity"].quantile(0.95)
IQR = Q3 - Q1
df = df[(df["quantity"] >= Q1 - 1.5 * IQR) & (df["quantity"] <= Q3 + 1.5 * IQR)]

# 📌 **2. Yeni Özellikler Ekleyelim**
df["is_weekend"] = df["weekday"].apply(lambda x: 1 if x in [0, 6] else 0)  # Cumartesi ve Pazar = 1

# 📌 **3. Zaman Serisi Özellikleri**
df["prev_month_diff"] = df.groupby("product_id")["quantity"].diff().fillna(0)

df["rolling_avg_3months"] = df.groupby("product_id")["quantity"].rolling(window=3, min_periods=1).mean().reset_index(0, drop=True)

# 📌 **4. Feature Scaling**
scaler = StandardScaler()
df[["unit_price", "category_id"]] = scaler.fit_transform(df[["unit_price", "category_id"]])

# 📌 **5. Model İçin Veri Setini Hazırlama**
X = df[["year", "month", "week", "product_id", "unit_price", "category_id", "is_weekend", "prev_month_diff", "rolling_avg_3months"]]
y = df["quantity"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 📌 **6. Gelişmiş Hiperparametre Tuning**
xgb_model = xgb.XGBRegressor(objective="reg:squarederror")

param_grid = {
    "n_estimators": [300, 500, 700],
    "max_depth": [6, 8, 10],
    "learning_rate": [0.01, 0.05, 0.1],
    "subsample": [0.8, 0.9, 1.0],
    "colsample_bytree": [0.8, 0.9, 1.0],
    "gamma": [0, 0.1, 0.3]  # Overfitting önleme için
}

grid_search = GridSearchCV(xgb_model, param_grid, cv=3, scoring="neg_mean_absolute_error", verbose=1, n_jobs=-1)
grid_search.fit(X_train, y_train)

best_model = grid_search.best_estimator_

# 📌 **7. Test Sonuçları**
y_pred = best_model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)

print(f"🔥 **Optimized XGBoost MAE:** {mae:.2f}")
print(f"🔥 **Optimized XGBoost MSE:** {mse:.2f}")

joblib.dump(best_model, "optimized_xgb.pkl")
print("✅ Model başarıyla kaydedildi: optimized_xgb.pkl")
