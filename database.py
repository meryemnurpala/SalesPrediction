from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# PostgreSQL bağlantı bilgileri
DB_USERNAME = "postgres"  # Kullanıcı adını yaz
DB_PASSWORD = "123456"  # PostgreSQL şifreni yaz
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "northwind"

# SQLAlchemy bağlantı dizesi
DATABASE_URL = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# Oturum yönetimi için SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Veritabanı bağlantısını sağlayacak fonksiyon
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
