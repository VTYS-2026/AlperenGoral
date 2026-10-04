-- =====================================================
-- Föy 01 / Görev 2 — kitaplar tablosu (DDL)
-- CREATE TABLE komutunuzu bu dosyaya yazın.
-- Beklenen sütunlar için föydeki tabloya bakın.
-- =====================================================

CREATE TABLE kitaplar (
    kitap_id INTEGER PRIMARY KEY,
    ad VARCHAR(200) NOT NULL,
    yazar VARCHAR(100) NOT NULL,
    yayin_yili SMALLINT,
    sayfa SMALLINT,
    tur VARCHAR(50)
);
