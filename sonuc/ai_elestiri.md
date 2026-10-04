# Yapay Zekâ Köşesi — Üret, Sorgula, Düzelt

## 1. Kullanılan Araç ve İstem Bilgisi
* **Kullanılan Yapay Zekâ Aracı:** ChatGPT (GPT-4o) / Gemini 1.5 Pro
* **Verilen İstem (Prompt):** "PostgreSQL’de bir kütüphanenin kitaplarını tutacak tabloyu oluştur."

---

## 2. Yapay Zekânın Ürettiği CREATE TABLE Komutu

```sql
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    published_year INT,
    pages INT,
    genre VARCHAR(50),
    available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. Görev 2 ile Karşılaştırma ve Tasarım Eleştirileri

Görev 2 kapsamında hazırladığımız `kitaplar` tablosu ile yapay zekanın ürettiği `books` tablosu karşılaştırıldığında hem veri tipi seçimi hem de iş kuralları/kısıtlar (constraints) açısından önemli tasarım farkları ve eksiklikler görülmektedir.

### Eleştiri 1: Veri Tipi Seçimi ve Bellek/Depolama Optimizasyonu
Yapay zeka `published_year` ve `pages` alanları için varsayılan olarak 4 baytlık `INT` (INTEGER) veri tipini tercih etmiştir. Ancak kitapların sayfa sayısı pratikte birkaç bini geçmez ve yayın yılı da 4 basamaklı bir sayıdır. Kütüphane gibi yüz binlerce satır barındırabilecek veritabanlarında `SMALLINT` (2 bayt) kullanılması disk ve bellek tasarrufu sağlar. Görev 2'deki şemamızda her iki alan için de `SMALLINT` seçilmiştir.

* **Düzeltilmiş Satırlar:**
```sql
published_year SMALLINT,
pages SMALLINT,
```

### Eleştiri 2: Alan Bütünlüğü ve Eksik CHECK Kısıtları (Constraints)
Yapay zekanın ürettiği şemada hiçbir `CHECK` kısıtı yer almamaktadır. Bu durum, veri bütünlüğü açısından büyük bir zafiyettir. Örneğin veritabanına sayfa sayısı negatif bir değer (-50) veya mantıksız bir yayın yılı (örneğin -3000 veya 9999) girilmesini engelleyen hiçbir kural bulunmamaktadır. Sayfa sayısının kesinlikle 0'dan büyük olması ve yayın yılının mantıklı bir aralıkta (örneğin 1000 ile 2100 arasında) olması kısıtlarla garanti altına alınmalıdır.

* **Düzeltilmiş Satırlar:**
```sql
published_year SMALLINT CHECK (published_year BETWEEN 1000 AND 2100),
pages SMALLINT CHECK (pages > 0),
```

### Eleştiri 3: Dil ve Adlandırma Standartları (İsimlendirme Tutarlılığı)
Yapay zeka tablo ve sütun adlarını İngilizce (`books`, `title`, `author`, `pages`) olarak üretmiştir. Projede kullanılan etki alanı (domain) dili Türkçe ise tüm tablolarda tek bir isimlendirme kuralına sadık kalınmalıdır. Ayrıca `id` gibi genel bir isim yerine hangi tablonun birincil anahtarı olduğunu açıkça belirten `kitap_id` isimlendirmesi ilişkisel modellerde (JOIN işlemlerinde) okunabilirliği artırır.

* **Düzeltilmiş Satırlar:**
```sql
CREATE TABLE kitaplar (
    kitap_id INTEGER PRIMARY KEY,
    ad VARCHAR(200) NOT NULL,
    yazar VARCHAR(100) NOT NULL,
```

### Eleştiri 4: ISBN Alanı Tanımı ve Format Kısıtı
Yapay zeka ISBN alanını `VARCHAR(20)` olarak belirlemiştir. Modern ISBN standartları kesin olarak ISBN-10 veya ISBN-13 formatındadır (10 veya 13 hane). Tireler temizlenmiş biçimde tutulduğunda `CHAR(13)` veri tipi kullanılması ve uzunluk/format kontrolünün `CHECK (length(isbn) IN (10, 13))` kısıtıyla yapılması veri kalitesini güvenceye alır.

* **Düzeltilmiş Satır:**
```sql
isbn CHAR(13) UNIQUE CHECK (length(isbn) = 13),
```

---

## 4. Sonuç ve Düzeltilmiş Bütünleşik Şema

Yapay zekanın ürettiği temel taslağı, yukarıdaki eleştiriler ve PostgreSQL iyi uygulama standartları doğrultusunda revize ettiğimizde elde edilen en uygun şema şöyledir:

```sql
CREATE TABLE kitaplar (
    kitap_id INTEGER PRIMARY KEY,
    ad VARCHAR(200) NOT NULL,
    yazar VARCHAR(100) NOT NULL,
    isbn CHAR(13) UNIQUE,
    yayin_yili SMALLINT CHECK (yayin_yili BETWEEN 1000 AND 2100),
    sayfa SMALLINT CHECK (sayfa > 0),
    tur VARCHAR(50),
    oduncte_mi BOOLEAN DEFAULT FALSE,
    olusturulma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
