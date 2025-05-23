# Sales Prediction API

## Proje Açıklaması

Bu proje, Turkcell Geleceği Yazan Kadınlar eğitimi kapsamında geliştirilmiş bir satış tahmin API'sidir. Geçmiş satış verileri kullanarak belirli ürünlerin gelecekteki satışlarını tahmin etmektedir. API, FastAPI framework'ü ile geliştirilmiş olup, Python ve XGBoost modelini kullanarak tahminler yapmaktadır. Veritabanı olarak PostgreSQL kullanılmakta ve SQLAlchemy ile bağlantı sağlanmaktadır.

### Kullanılacak Teknolojiler:

- **FastAPI**: API'yi geliştirmek için kullanılan framework.
- **SQLAlchemy**: Veritabanı bağlantıları ve sorguları için kullanılan ORM.
- **XGBoost**: Satış tahminlerini yapmak için kullanılan makine öğrenmesi modeli.
- **PostgreSQL**: Veritabanı yönetim sistemi.
- **Joblib**: Modeli kaydetmek ve yüklemek için kullanılır.

## API Uç Noktaları

### 1. `/products` - Ürün Listesini Al

**GET** isteği ile tüm ürünlerin listesine erişebilirsiniz.

**Örnek İstek:**

```http
GET /products
```

**YANIT:**

```json
[
  {
    "product_id": 1,
    "product_name": "Product A"
  },
  {
    "product_id": 2,
    "product_name": "Product B"
  }
]
```

### 2. `/predict` - Satış Tahmini Yap

**POST** isteği ile bir ürün için satış tahmini yapılabilir. Kullanıcıdan `product_id`, `year`, `month`, `quantity`, `week` ve `customer_id` gibi veriler alınır.

**Örnek İstek:**

```http
POST /predict
```

**Request Body->Raw:**

```json
{
  "product_id": 1,
  "year": 2025,
  "month": 4,
  "quantity": 100,
  "week": 2,
  "customer_id": 12345
}
```

**YANIT:**

```json
{
  "product_id": 1,
  "year": 2025,
  "month": 4,
  "predicted_sales": 250.45
}
```

### 3. `/retrain` - Modeli Yeniden Eğit

**POST** isteği ile mevcut model yeniden eğitilebilir. Bu uç nokta veritabanından alınan yeni verilerle modelin güncellenmesini sağlar.

**Örnek İstek:**

```http
POST /retrain
```

**YANIT**

```json
{
  "message": "Model başarıyla yeniden eğitildi ve kaydedildi."
}
```

## Projeyi Çalıştırma

### Gereksinimler

Projenin çalışabilmesi için aşağıdaki Python kütüphanelerinin yüklü olması gerekmektedir:

```bash
pip install -r requirements.txt
```

### Çalıştırma

FastAPI Uygulamasını Başlatmak: API'yi çalıştırmak için aşağıdaki komutu kullanabilirsiniz:

```bash
uvicorn api:app --reload
```

Burada, `api` uygulamanın ana dosyasının adı, `app` ise FastAPI uygulama nesnesidir.

**Veritabanı Bağlantısı:** PostgreSQL veritabanınızın doğru şekilde yapılandırıldığından emin olun. `DATABASE_URL` içinde belirtilen bilgileri (kullanıcı adı, şifre, veritabanı adı vb.) güncelleyin.

**Model Yükleme:** Model dosyasının (`optimized_xgb.pkl`) doğru yerde olduğundan ve API'nin yüklenmesi sırasında hatasız olarak okunabildiğinden emin olun.

## Swagger ve Postman

Projeyi çalıştırdığınızda, Swagger ile API dokümantasyonuna şu adresten erişebilirsiniz:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Swagger üzerinden API'yi test edebilir, uç noktaları ve parametreleri keşfedebilirsiniz.

**Postman ile test etmek için:** Sales Prediction API koleksiyonunu indirip kullanabilirsiniz. Postman koleksiyonunu Postman uygulamasında import ederek, tüm uç noktaları test edebilirsiniz.

## Modelin Eğitilmesi

Eğer modelin eğitilmesi gerekiyorsa, `/retrain` uç noktasını kullanarak veritabanından yeni verilerle modelinizi yeniden eğitebilirsiniz.

## Hata Yönetimi

Herhangi bir hata durumunda API, kullanıcıya uygun HTTP hata kodu ve mesajı döndürecektir. Örneğin:

- **404**: Ürün bulunamadığında
- **500**: Sunucu tarafında bir hata oluştuğunda

# Swagger ve Postman Dokümantasyonu

**Swagger UI:** FastAPI'nin otomatik olarak sunduğu Swagger UI üzerinden API'yi test edebilirsiniz.

**Postman:** Aşağıdaki adımları izleyerek Postman ile API'yi test edebilirsiniz:

- **Koleksiyonu İndirin:** Postman Koleksiyonu İndir
- **API Uç Noktalarını Test Edin:** Postman üzerinden her bir uç noktayı test edin.

## Sonraki Adımlar

- **Model İyileştirmeleri:** Modelin doğruluğunu artırmak için verileri ve parametreleri inceleyin.
- **API Performans Testleri:** Yük testi yaparak API'nin performansını analiz edin.

##Proje Sahibi İletişim
Proje Sahibi : Meryemnur Pala
Mail:meryemnur6969@gmail.com
