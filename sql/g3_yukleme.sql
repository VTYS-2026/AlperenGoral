-- =====================================================
-- Föy 01 / Görev 3 — CSV'den veri yükleme
-- COPY komutunuzu ve doğrulama sorgusunu bu dosyaya yazın.
-- Doğrulama sorgusunun çıktısını sonuc/g3.txt dosyasına kaydedin.
-- =====================================================

COPY kitaplar FROM '/veri/kitaplar.csv'
WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

SELECT COUNT(*) AS satir_sayisi,
       MIN(yayin_yili) AS en_eski,
       MAX(yayin_yili) AS en_yeni
FROM kitaplar;
