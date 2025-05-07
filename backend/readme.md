# Uçak Üretim Sistemi - Django API

Bu proje, takımlara göre parça üretimi, montaj, geri dönüşüm ve stok kontrolü gibi işlemleri içeren JWT tabanlı bir Django REST API uygulamasıdır.

## İçerik

* JWT ile kimlik doğrulama
* Takıma bağlı parça yetkileri
* Parça stoğu, geri dönüşüm işlemleri
* Uçak montajı ve parça takibi
* Swagger dokümantasyonu

---

## İlk Kurulum (Geliştirici Rehberi)

### 1. Reposu klonla

```bash
git clone <repo-url>
cd backend
```

### 2. Ortam dosyası oluştur

```
cp .env.example .env
```

### 3. Docker ile ayağa kaldır

```bash
docker-compose build
docker-compose up -d
```

> Bu işlem PostgreSQL ve Django servisini başlatır.

### 4. Migration dosyalarını oluştur

```bash
docker-compose exec web python manage.py makemigrations
# veya sadece core app için
# docker-compose exec web python manage.py makemigrations core
```

### 5. Veritabanı tablolarını oluştur

```bash
docker-compose exec web python manage.py migrate
```

### 6. İlk verileri ekle (uçak modeli, takım, parça tipi)

```bash
docker-compose exec web python manage.py seed
```

### 7. Admin kullanıcısı oluştur

```bash
docker-compose exec web python manage.py createsuperuser
```

> Bu adım **zorunludur** çünkü sisteme giriş yapılacak kullanıcı yoksa `/auth/` endpoint'inden token alamazsın. Bu kullanıcıya admin panelden `Personnel` ilişkisi kurmalısın.

### 8. Admin paneli (tarayıcıdan)

```
http://localhost:8000/admin
```

Buradan yeni kullanıcı ve Personnel ekleyebilirsin.

---

## API Erişimi

### Swagger Dokümanı:

```
http://localhost:8000/docs/
```

### Kimlik Doğrulama:

#### 1. Giriş (JWT token al):

```
POST /api/v1/auth/
{
  "username": "admin",
  "password": "123456"
}
```

#### 2. Access token yenile:

```
POST /api/v1/auth/refresh/
{
  "refresh": "<refresh_token>"
}
```

#### 3. Kullanıcı bilgisi:

```
GET /api/v1/me/
Authorization: Bearer <access_token>
```

---

## Dizin Yapısı (kısaca)

```
backend/
├── core/
│   ├── models/
│   ├── views/
│   ├── serializers/
│   ├── urls/v1.py
│   └── admin.py
├── config/ (settings, urls)
├── docker-compose.yml
└── manage.py
```

