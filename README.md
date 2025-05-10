# Uçak Üretim Sistemi - Django REST API

Bu proje, takımlara göre parça üretimi, montaj, geri dönüşüm ve stok kontrolü gibi işlemleri yürüten JWT tabanlı bir Django REST API uygulamasıdır.

## Proje Kapsamı

* JWT ile kimlik doğrulama sistemi
* Takımlara özgü parça yetkilendirme mekanizması
* Parça stok takibi ve geri dönüşüm süreci
* Uçak montaj işlemleri ve parça takibi
* Swagger ile API dokümantasyonu

---

## Kurulum Rehberi (Geliştirici)

### 1. Depoyu Klonlayın

```bash
git clone https://github.com/edibesad/baykar-backend-case.git
cd backend
```

### 2. Ortam Değişkenlerini Tanımlayın

```bash
cp .env.example .env
```

### 3. Docker Servislerini Başlatın

```bash
docker-compose build
docker-compose up
```

> Bu adım PostgreSQL ve Django servislerini başlatır.

### 4. Gerekli Migration Dosyalarını Oluşturun

```bash
docker-compose exec web python manage.py makemigrations
# Yalnızca "core" uygulaması için:
# docker-compose exec web python manage.py makemigrations core
```

### 5. Veritabanı Tablolarını Oluşturun

```bash
docker-compose exec web python manage.py migrate
```

### 6. Varsayılan Veri Setini Ekleyin (Uçak Modeli, Takım, Parça Tipi)

```bash
docker-compose exec web python manage.py seed
```

### 7. Yönetici Kullanıcı Oluşturun

```bash
docker-compose exec web python manage.py createsuperuser
```

> Bu adım **zorunludur**. Sisteme giriş yapabilecek bir kullanıcı olmadan JWT token alınamaz. Admin panelinden bu kullanıcıya ilişkili bir `Personnel` kaydı oluşturmanız gerekir.

### 8. Yönetim Paneline Erişim

```
http://localhost:8000/admin
```

Bu panel aracılığıyla yeni kullanıcılar ve `Personnel` verileri ekleyebilirsiniz.

---

## API Erişimi

### Swagger Dokümentasyonu:

```
http://localhost:8000/docs/
```

### Kimlik Doğrulama

#### 1. JWT Token Alma

```
POST /api/v1/auth/
{
  "username": "admin",
  "password": "123456"
}
```

#### 2. Access Token Yenileme

```
POST /api/v1/auth/refresh/
{
  "refresh": "<refresh_token>"
}
```

#### 3. Giriş Yapmış Kullanıcı Bilgilerini Getirme

```
GET /api/v1/me/
Authorization: Bearer <access_token>
```

---
