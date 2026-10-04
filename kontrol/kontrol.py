#!/usr/bin/env python3
"""Föy 01 — Otomatik Değerlendirici

GitHub Actions içinde çalışır (bkz. .github/workflows/degerlendir.yml).
Öğrencinin sql/ ve sonuc/ klasörlerindeki teslimini, ogrno.txt'deki
numaradan yeniden üretilen KİŞİYE ÖZEL veri setine karşı kontrol eder.

Beklenen değerler veritabanından değil, veri üretecinden (veri/uret.py)
Python ile hesaplanır; bu yüzden bu dosyada hazır SQL cevabı yoktur.
"""
import os
import re
import sys
from collections import Counter
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "veri"))
from uret import uret  # noqa: E402

try:
    import psycopg
except ImportError:
    print("HATA: psycopg kurulu değil (pip install 'psycopg[binary]').")
    sys.exit(2)

# ---------------------------------------------------------------- yardımcılar
SONUCLAR = []  # (görev, puan, tam_puan, mesaj)


def kaydet(gorev, alinan, tam, mesaj):
    SONUCLAR.append((gorev, alinan, tam, mesaj))
    durum = "✓" if alinan == tam else ("~" if alinan > 0 else "✗")
    print(f"[{durum}] {gorev}: {alinan}/{tam} — {mesaj}")


def oku(yol):
    p = KOK / yol
    if not p.exists():
        return None
    ham = p.read_bytes()
    # Windows'ta PowerShell'in ">" yonlendirmesi UTF-16 yazar; Not Defteri de
    # UTF-8'e BOM ekler. Bunlari cozmezsek ogrencinin dogru cikti dosyasi
    # taninmaz ve haksiz puan kaybi olur.
    if ham[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return ham.decode("utf-16", errors="replace")
    return ham.decode("utf-8-sig", errors="replace")

def sql_kodu(metin):
    """SQL metninden yorumlari atar.

    Sablon dosyalarinin KENDI yorumlarinda "CREATE TABLE komutunuzu yazin"
    gibi ifadeler gectigi icin, ham metinde anahtar kelime aramak bos teslimi
    gecerli sayiyordu. Denetimler bu fonksiyonun ciktisi uzerinde yapilir.
    """
    metin = re.sub(r"/\*.*?\*/", " ", metin or "", flags=re.S)
    return re.sub("--.*", " ", metin)


def baglanti():
    return psycopg.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5432"),
        user=os.environ.get("PGUSER", "vtys"),
        password=os.environ.get("PGPASSWORD", "vtys2026"),
        dbname=os.environ.get("PGDATABASE", "vtysdb"),
        autocommit=True,
    )


# ---------------------------------------------------------------- kontroller
def ogrno_al():
    icerik = oku("ogrno.txt")
    if icerik is None:
        return None
    icerik = icerik.strip()
    return icerik if icerik.isdigit() else None


def kontrol_g1():
    icerik = oku("sonuc/g1.txt")
    if not icerik:
        kaydet("Görev 1", 0, 10, "sonuc/g1.txt bulunamadı veya boş.")
        return
    if "PostgreSQL" in icerik and "vtys" in icerik:
        kaydet("Görev 1", 10, 10, "Ortam doğrulama çıktısı geçerli.")
    else:
        kaydet("Görev 1", 5, 10,
               "Dosya var ama beklenen sürüm/bağlantı bilgisi eksik görünüyor.")


def kontrol_g2(con):
    sql = oku("sql/g2_ddl.sql")
    if not sql or "CREATE" not in sql_kodu(sql).upper():
        kaydet("Görev 2", 0, 20, "sql/g2_ddl.sql bulunamadı veya CREATE TABLE içermiyor.")
        return False
    try:
        con.execute("DROP TABLE IF EXISTS kitaplar CASCADE")
        con.execute(sql)
    except Exception as e:
        kaydet("Görev 2", 0, 20, f"DDL çalıştırılamadı: {e}")
        return False

    kolonlar = {r[0]: r[1] for r in con.execute(
        """SELECT column_name, data_type FROM information_schema.columns
           WHERE table_name = 'kitaplar'""").fetchall()}
    gerekli = {"kitap_id", "ad", "yazar", "yayin_yili", "sayfa", "tur"}
    if not kolonlar:
        kaydet("Görev 2", 0, 20, "kitaplar tablosu oluşmadı; dosyada çalışan bir CREATE TABLE yok.")
        return False
    eksik = gerekli - set(kolonlar)
    if eksik:
        kaydet("Görev 2", 8, 20, f"Tablo oluştu ama eksik sütun(lar) var: {', '.join(sorted(eksik))}")
        return False

    pk = con.execute(
        """SELECT a.attname FROM pg_index i
           JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
           WHERE i.indrelid = 'kitaplar'::regclass AND i.indisprimary""").fetchall()
    if [r[0] for r in pk] != ["kitap_id"]:
        kaydet("Görev 2", 15, 20, "Sütunlar tamam; ancak kitap_id PRIMARY KEY değil.")
        return True
    kaydet("Görev 2", 20, 20, "Tablo şeması ve birincil anahtar doğru.")
    return True


def veri_yukle(con, satirlar):
    """Beklenen veriyi tabloya değerlendirici yükler (öğrencinin COPY'si
    yerel Docker ortamına özgü /veri yolunu kullanır)."""
    con.execute("TRUNCATE kitaplar")
    with con.cursor() as cur:
        with cur.copy(
            "COPY kitaplar (kitap_id, ad, yazar, yayin_yili, sayfa, tur) FROM STDIN"
        ) as cp:
            for s in satirlar:
                cp.write_row((s["kitap_id"], s["ad"], s["yazar"],
                              s["yayin_yili"], s["sayfa"], s["tur"]))


def kontrol_g3(satirlar):
    puan = 0
    sql = oku("sql/g3_yukleme.sql")
    if sql and re.search(r"\bCOPY\b", sql, re.IGNORECASE) and "kitaplar" in sql:
        puan += 10
        m1 = "COPY komutu yerinde."
    else:
        m1 = "sql/g3_yukleme.sql içinde kitaplar tablosuna COPY bulunamadı."

    yillar = [s["yayin_yili"] for s in satirlar]
    beklenen = [str(len(satirlar)), str(min(yillar)), str(max(yillar))]
    icerik = oku("sonuc/g3.txt") or ""
    bulunan = [b for b in beklenen if b in icerik]
    if len(bulunan) == 3:
        puan += 15
        m2 = "Doğrulama çıktısı sizin veri setinizle uyumlu."
    elif icerik:
        m2 = ("Çıktı sizin veri setinizle uyuşmuyor. ogrno.txt'deki numara ile "
              "uret.py'a verdiğiniz numaranın aynı olduğundan ve sorguyu kendi "
              "yüklediğiniz tablo üzerinde çalıştırdığınızdan emin olun.")
    else:
        m2 = "sonuc/g3.txt bulunamadı."
    kaydet("Görev 3", puan, 25, f"{m1} {m2}")


def g4_beklenenler(satirlar):
    """Dört sorunun beklenen sonuçları — üreteç verisinden Python ile."""
    b = {}
    b[1] = [(s["ad"], s["yayin_yili"]) for s in satirlar if s["yayin_yili"] >= 2015]
    b[2] = [(s["ad"], s["sayfa"]) for s in satirlar
            if s["tur"] == "Roman" and s["sayfa"] > 400]
    sirali = sorted(satirlar, key=lambda s: -s["sayfa"])
    esik = sirali[4]["sayfa"]
    b[3] = {"esikler": [s["sayfa"] for s in sirali[:5]],
            "adaylar": {(s["ad"], s["yazar"], s["sayfa"])
                        for s in satirlar if s["sayfa"] >= esik}}
    b[4] = Counter(s["tur"] for s in satirlar)
    return b


def kontrol_g4(con, satirlar):
    sql = oku("sql/g4_sorgular.sql")
    if not sql:
        kaydet("Görev 4", 0, 25, "sql/g4_sorgular.sql bulunamadı.")
        return

    parcalar = re.split(r"--\s*Soru\s*4\.(\d)[^\n]*", sql)
    sorgular = {}
    for i in range(1, len(parcalar) - 1, 2):
        sorgular[int(parcalar[i])] = parcalar[i + 1].strip()

    beklenen = g4_beklenenler(satirlar)
    puanlar = {1: 6, 2: 6, 3: 6, 4: 7}
    toplam = 0
    mesajlar = []

    for no in (1, 2, 3, 4):
        q = sorgular.get(no, "").rstrip().rstrip(";")
        if not q:
            mesajlar.append(f"4.{no}: '-- Soru 4.{no}' başlığı altında sorgu yok.")
            continue
        try:
            rows = con.execute(q).fetchall()
        except Exception as e:
            mesajlar.append(f"4.{no}: sorgu hatası ({str(e).splitlines()[0]}).")
            continue

        if no == 1:
            yillar = [r[-1] for r in rows]
            dogru = (Counter((str(r[0]), r[-1]) for r in rows)
                     == Counter((a, y) for a, y in beklenen[1])
                     and yillar == sorted(yillar, reverse=True))
        elif no == 2:
            dogru = (Counter((str(r[0]), r[-1]) for r in rows)
                     == Counter(beklenen[2]))
        elif no == 3:
            dogru = (len(rows) == 5
                     and [r[-1] for r in rows] == beklenen[3]["esikler"]
                     and all((str(r[0]), str(r[1]), r[2]) in beklenen[3]["adaylar"]
                             for r in rows))
        else:
            sayilar = [r[-1] for r in rows]
            dogru = (Counter({str(r[0]): r[-1] for r in rows})
                     == beklenen[4]
                     and sayilar == sorted(sayilar, reverse=True))

        if dogru:
            toplam += puanlar[no]
            mesajlar.append(f"4.{no}: doğru.")
        else:
            mesajlar.append(f"4.{no}: sonuç beklenenden farklı.")

    kaydet("Görev 4", toplam, 25, " ".join(mesajlar))


def ogrenci_metni(markdown):
    """Markdown'dan kod bloklarini atip ogrencinin KENDI yazdigi metni birakir.

    Yapay zekanin urettigi SQL'i yapistirip tek satir elestiri yazmayan
    teslimler yalnizca uzunluga bakildiginda esigi gecip tam puan aliyordu
    (gercek teslimlerde tespit edildi). Puan artik duz metne gore verilir.
    """
    m = markdown or ""
    m = re.sub(r"```.*?```", " ", m, flags=re.S)
    m = re.sub(r"```.*", " ", m, flags=re.S)
    m = re.sub(r"^\s{4,}\S.*$", " ", m, flags=re.M)
    m = re.sub(r"`[^`]*`", " ", m)
    return re.sub(r"\s+", " ", m).strip()


def kontrol_ai():
    icerik = oku("sonuc/ai_elestiri.md")
    if not icerik or len(ogrenci_metni(icerik)) < 300:
        kaydet("AI Köşesi", 0, 10,
               "sonuc/ai_elestiri.md yok ya da eleştiri metniniz 300 karakterden kısa "
               "(yapıştırdığınız kod blokları sayılmaz). Föyde istenen iki "
               "somut eleştiriyi yazdığınızda bu uzunluk zaten aşılır "
               "(içerik ayrıca asistan tarafından okunur).")
    else:
        kaydet("AI Köşesi", 10, 10,
               "Dosya teslim edildi (isabet puanı asistan değerlendirmesiyle kesinleşir).")


# ---------------------------------------------------------------- ana akış
def main():
    print("=" * 64)
    print("Föy 01 — Otomatik Değerlendirme")
    print("=" * 64)

    ogrno = ogrno_al()
    if not ogrno:
        print("HATA: ogrno.txt bulunamadı ya da geçerli bir numara içermiyor.")
        print("Deponun kökündeki ogrno.txt dosyasına yalnızca öğrenci numaranızı yazın.")
        sys.exit(1)
    print(f"Öğrenci no: {ogrno} (veri seti bu numaradan yeniden üretiliyor)\n")

    satirlar = uret(ogrno)

    kontrol_g1()
    with baglanti() as con:
        tablo_var = kontrol_g2(con)
        if tablo_var:
            try:
                veri_yukle(con, satirlar)
            except Exception as e:
                print(f"    (veri yüklenemedi, Görev 3–4 atlanıyor: {e})")
                tablo_var = False
        if tablo_var:
            kontrol_g3(satirlar)
            kontrol_g4(con, satirlar)
        else:
            kaydet("Görev 3", 0, 25, "Tablo hazır olmadığı için kontrol edilemedi.")
            kaydet("Görev 4", 0, 25, "Tablo hazır olmadığı için kontrol edilemedi.")
    kontrol_ai()

    alinan = sum(s[1] for s in SONUCLAR)
    tam = sum(s[2] for s in SONUCLAR)
    print("\n" + "=" * 64)
    print(f"TOPLAM (otomatik kontrol edilen kısım): {alinan}/{tam}")
    print("Ön quiz (5p) ve Görev 5 (15p) bu rapora dahil değildir.")
    print("=" * 64)

    ozet = os.environ.get("GITHUB_STEP_SUMMARY")
    if ozet:
        with open(ozet, "a", encoding="utf-8") as f:
            f.write("## Föy 01 — Otomatik Değerlendirme\n\n")
            f.write("| Bileşen | Puan | Açıklama |\n|---|---|---|\n")
            for gorev, a, t, m in SONUCLAR:
                f.write(f"| {gorev} | {a}/{t} | {m} |\n")
            f.write(f"| **Toplam** | **{alinan}/{tam}** | |\n")

    sys.exit(0 if alinan == tam else 1)


if __name__ == "__main__":
    main()
