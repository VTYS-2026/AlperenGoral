#!/usr/bin/env python3
"""Kişiye özel veri üreteci — Föy 01 (kitaplar.csv)

Kullanım:
    python3 veri/uret.py <ogrenci_no>

Aynı öğrenci numarası her çalıştırmada AYNI veri setini üretir
(üreteç, numaranızı rastgelelik tohumu olarak kullanır). Bu sayede
sorgular herkes için ortak, sonuçlar kişiye özeldir.
"""
import csv
import random
import sys
from pathlib import Path

TURLER = ["Roman", "Bilim", "Tarih", "Şiir", "Deneme",
          "Polisiye", "Fantastik", "Biyografi"]

ADLAR = ["Ahmet", "Ayşe", "Mehmet", "Elif", "Mustafa", "Zeynep", "Ali",
         "Fatma", "Hasan", "Emine", "Murat", "Hülya", "Kemal", "Nazlı",
         "Selim", "Leyla", "Orhan", "Sevgi", "Yakup", "Melek"]

SOYADLAR = ["Yılmaz", "Kaya", "Demir", "Çelik", "Şahin", "Yıldız", "Aydın",
            "Arslan", "Doğan", "Kılıç", "Aslan", "Çetin", "Koç", "Kurt",
            "Özdemir", "Erdoğan", "Polat", "Güneş", "Taş", "Bulut"]

KELIME1 = ["Kayıp", "Sessiz", "Uzak", "Mavi", "Son", "Gizli", "Kırık",
           "Beyaz", "Derin", "Yalnız", "Eski", "Unutulmuş", "Karanlık",
           "Sonsuz", "Küçük"]

KELIME2 = ["Şehir", "Nehir", "Rüzgar", "Yolculuk", "Bahçe", "Gölge",
           "Ada", "Mektup", "Gece", "Deniz", "Dağ", "Hikâye", "Zaman",
           "Kapı", "Harita"]

EKLER = ["ve Sonrası", "Efsanesi", "Günlükleri", "Sırrı", "Masalı"]


def uret(ogrno: str):
    """Öğrenci numarasından deterministik kitap listesi üretir.

    Satır sayısı ve yıl aralığı da numaradan türetilir; böylece Görev 3'ün
    doğrulama değerleri (COUNT, MIN, MAX) bile kişiye özeldir.
    """
    tohum = int(ogrno)
    rnd = random.Random(tohum)
    satir_sayisi = 460 + tohum % 81          # 460–540 arası, kişiye özel
    alt_yil = 1950 + rnd.randint(0, 10)      # en eski yıl, kişiye özel
    kullanilan_adlar = set()
    satirlar = []
    for kitap_id in range(1, satir_sayisi + 1):
        while True:
            ad = f"{rnd.choice(KELIME1)} {rnd.choice(KELIME2)}"
            if rnd.random() < 0.35:
                ad += f" {rnd.choice(EKLER)}"
            if ad not in kullanilan_adlar:
                kullanilan_adlar.add(ad)
                break
        satirlar.append({
            "kitap_id": kitap_id,
            "ad": ad,
            "yazar": f"{rnd.choice(ADLAR)} {rnd.choice(SOYADLAR)}",
            "yayin_yili": rnd.randint(alt_yil, 2025),
            "sayfa": rnd.randint(60, 900),
            "tur": rnd.choice(TURLER),
        })
    return satirlar


def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print("Kullanım: python3 veri/uret.py <ogrenci_no>")
        print("Örnek   : python3 veri/uret.py 230541001")
        sys.exit(1)

    ogrno = sys.argv[1]
    hedef = Path(__file__).resolve().parent / "kitaplar.csv"
    satirlar = uret(ogrno)

    with open(hedef, "w", newline="", encoding="utf-8") as f:
        yazici = csv.DictWriter(
            f, fieldnames=["kitap_id", "ad", "yazar", "yayin_yili", "sayfa", "tur"])
        yazici.writeheader()
        yazici.writerows(satirlar)

    yillar = [s["yayin_yili"] for s in satirlar]
    print(f"Üretildi: {hedef}")
    print(f"  Satır sayısı : {len(satirlar)}")
    print(f"  Yıl aralığı  : {min(yillar)} – {max(yillar)}")
    print("Bu dosya size özeldir; sorgu sonuçlarınız sınıftaki herkesten farklıdır.")


if __name__ == "__main__":
    main()
