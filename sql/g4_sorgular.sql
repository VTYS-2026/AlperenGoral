-- =====================================================
-- Föy 01 / Görev 4 — İlk sorgularınız
-- Her sorguyu ilgili "-- Soru 4.x" başlığının ALTINA yazın.
-- Başlık satırlarını silmeyin ve değiştirmeyin; otomatik
-- değerlendirici sorguları bu başlıklardan ayırt eder.
-- Çıktıları sırasıyla sonuc/g4.txt dosyasına kaydedin.
-- =====================================================

-- Soru 4.1
-- (2015 ve sonrası kitapların adı ve yılı — yıla göre yeniden eskiye)
SELECT ad, yayin_yili
FROM kitaplar
WHERE yayin_yili >= 2015
ORDER BY yayin_yili DESC;

-- Soru 4.2
-- (Sayfa sayısı 400'den fazla olan roman türündeki kitapların adı ve sayfa sayısı)
SELECT ad, sayfa
FROM kitaplar
WHERE tur = 'Roman' AND sayfa > 400;

-- Soru 4.3
-- (En kalın 5 kitabın adı, yazarı ve sayfa sayısı)
SELECT ad, yazar, sayfa
FROM kitaplar
ORDER BY sayfa DESC
LIMIT 5;

-- Soru 4.4
-- (Her türdeki kitap sayısı — kalabalıktan aza)
SELECT tur, COUNT(*) AS adet
FROM kitaplar
GROUP BY tur
ORDER BY adet DESC;
