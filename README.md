# Föy 01 — Ortam Kurulumu ve İlk Veritabanı

Modern Veritabanı Yönetim Sistemleri — Laboratuvar teslim deposu.
Görevlerin tam açıklaması **Föy 01 PDF**'indedir; bu dosya yalnızca kısa bir hatırlatmadır.

## Hızlı başlangıç

```bash
# 1) Öğrenci numaranızı yazın
echo "230541001" > ogrno.txt        # kendi numaranız

# 2) Ortamı başlatın
docker compose up -d

# 3) Kişiye özel verinizi üretin
python3 veri/uret.py 230541001      # kendi numaranız

# 4) Veritabanına bağlanın
docker exec -it vtys-postgres psql -U vtys -d vtysdb
```

## Depo yapısı

| Yol | Ne |
|---|---|
| `ogrno.txt` | Öğrenci numaranız (otomatik değerlendirici bunu kullanır — ilk iş doldurun) |
| `docker-compose.yml` | PostgreSQL 16 + pgAdmin ortamı |
| `veri/uret.py` | Kişiye özel `kitaplar.csv` üreteci |
| `sql/` | Yazacağınız SQL dosyaları (görev başına bir dosya) |
| `sonuc/` | Sorgu çıktılarınız ve AI köşesi teslimi |

## Teslim

```bash
git add ogrno.txt sql/ sonuc/
git commit -m "Foy 01 teslimi"
git push
```

Push sonrası **Actions** sekmesinden otomatik değerlendirme sonucunu görün.
Son teslim saatine kadar deneme sayısı sınırsızdır — kırmızı görürseniz
günlükteki açıklamayı okuyun, düzeltin, yeniden push edin.

> **Not:** Veri setiniz öğrenci numaranızdan üretilir; başkasının çıktısını
> teslim etmek otomatik olarak tespit edilir. Yapay zekâdan yardım alabilirsiniz,
> ancak teslim ettiğiniz her satırı sözlü savunmada açıklayabilmelisiniz.
