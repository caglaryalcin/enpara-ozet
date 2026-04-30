#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enpara Kredi Kartı Ekstresi → Kategori Özeti (.txt)
Kullanım: python finance_parser.py
"""

import re
import sys
import unicodedata
from pathlib import Path

import pdfplumber

KATEGORILER = {
    "Yurtdışı Harcamalar": ["yurt disi", "yurtdisi"],
    "Kahve":              ["aroasting", "sespresso", "soil coffee", "starbucks",
                            "shady coffee", "fam coffee", "null coffee",
                            "kahve dunyasi", "coffeemania", r"\bcoffee\b",
                            r"\bpiano\b",
                            "gloria jean", "caribou", "petra roast",
                            "mandabatmaz", "costa", "caffe nero", "tim horton",
                            r"\bbrew\b", r"\bkahve"],
    "Yemek / Restoran":   ["gunaydin", "oses", "cigkofte", "cig kofte",
                            "konyali", r"\bkosk\b", "bartos", "burger",
                            "prava", r"\bpita\b", "pravaa", "kavurmaci", "steakho",
                            "kasaf", r"\betli\b", r"\bkofte", "doner",
                            "lokanta", "restoran", "pizza", r"\blariba\b",
                            "tacuk", "torunlar", "battal gazi",
                            "mcdonalds", "mcdonald", r"\bkfc\b", "burger king",
                            "pizza hut", "dominos", "little caesar", "subway",
                            "popeyes", "taco bell", "five guys",
                            "yemeksepeti", "trendyol yemek",
                            "fast food",
                            "kebap", "kebab", "mangal", "ocakbasi", "lahmacun",
                            r"\bpide\b", r"\bborek\b", r"\bbalik\b", r"\bfirin\b",
                            "sushi", "iskender", "tantuni",
                            "bigchefs", "carls jr", "arby",
                            "tavuk dunyasi", "muhallebici",
                            "happy moon", "welldone", "ranchero",
                            "eataly", "morini", "ramiz",
                            r"\bdurumle\b", "saray muhallebi",
                            "espressolab", "espresso lab",
                            "faruk gulluoglu"],
    "Market / Gıda":      ["getir", r"param\s*/", "migros", r"\ba101\b", r"\bbim\b",
                            "carrefour", "demir gida", "simit", "pastane",
                            "kuruyemis", "bozacisi", "cikolata", "kasap",
                            "kosk", "konyali", "gida", r"\bet\b", "unlu mamul",
                            r"\bsok\b", "hakmar", "makromarket", "file market",
                            r"\bdia\b", "ekomini", "tarım kredi",
                            r"\bmanav\b", r"\bbakkal\b", "sut market", "fresh market",
                            "kose market",
                            "dora roma", "kizilkayalar"],
    "Sağlık":             ["eczane", "eczanesi", "hastane", "hospital", "klinik",
                            "universitesi tip", "ozel gop", "raim eczane",
                            "foca eczane", "optik",
                            r"\bdis\b", "dental", r"\bdoktor\b", "poliklinik",
                            "medikal", r"\blab\b", "laboratuvar",
                            "saglik merkezi", "rontgen", "ultrason",
                            r"\bhekim\b", "dis klinigi"],
    "Dijital / Abonelik": ["claude", "google", "playstation", r"\bpsn\b", "youtube",
                            "netflix", "spotify", r"\bapple\b", "microsoft", "steam",
                            "twitch", "amazonprime", "amazon prime", "disney", "exxen",
                            "blutv", "supercell", r"\bbein\b", "deezer", "canva",
                            "workspace",
                            "mubi", r"\bgain\b", r"\btod\b", "ssport", "fizy", "muud",
                            "storytel", "audible", "linkedin", r"\bzoom\b", "dropbox",
                            "adobe", "chatgpt", "midjourney", "github", "faceit",
                            "epicgames", "epic games", "roblox", "nintendo",
                            "icloud", "parametrix"],
    "Online Alışveriş":   [r"\bamazon\b", "hepsiburada", "hepsipay", "n11",
                            "trendyol", "aliexpress", "ciceksepeti",
                            "gittigidiyor", "iyzico", "temu", "shein",
                            r"\bebay\b", "reyonplus", "sahibinden",
                            "sanal magaza", r"\.(com|net)(\.tr)?\b"],
    "Fatura / Hizmet":    ["turkcell", "turk telekom", "ttnet", "vodafone",
                            "elektrik", "dogalgaz", "igdas", r"\biski\b", "internet",
                            "fiber", "sigorta", "aidat", "danisim elektrik",
                            "ibb spor", "istanbulkart", "erbay reklam", "paytr",
                            r"\bibb\b", "ck bogaz", "bogazici", "3dteknobiz",
                            "baskentgaz", "enerjisa", "toroslar", "dicle elektrik",
                            r"\bptt\b", "yurtici kargo", "mng kargo", "aras kargo",
                            r"\bups\b", r"\bdhl\b", "fedex", r"\bkargo\b"],
    "Seyahat":            [r"\bthy\b", "turkish airlines", "pegasus", "sunexpress",
                            "anadolujet", "corendon",
                            r"\botel\b", r"\bhotel\b", "hostel", "booking",
                            "airbnb", "trivago", "expedia", "tatilsepeti",
                            r"\btur\b", "turoperator", "otobus",
                            r"\bido\b", "turyol", r"\bvapur\b",
                            "ets tur", "jolly tur"],
    "Oyuncak":            ["oyuncak", "toyz", "lego", "jumbo"],
    "Giyim / Alışveriş": ["lcw", "jack jones", "ikea", "beymen", "decathlon", "koton",
                            r"\bmango\b", r"\bzara\b", "boyner",
                            "defacto", r"\bh&m\b", "h and m", "marks spencer", r"\bmavi\b",
                            "lacoste", r"\bnike\b", "adidas", r"\bpuma\b",
                            "new balance", "skechers", "reserved", "bershka",
                            "pull bear", "stradivarius", "massimo dutti",
                            "sarar", "altinyildiz", r"\bnetwork\b", "lefties",
                            "gratis", "watsons",
                            # Giyim & Ayakkabı
                            "colins", "columbia", "converse", r"\bgap\b", "levis",
                            "hummel", "avva", "ipekyol", "kigili", "jimmy key",
                            r"\bloft\b", "ltb", "armine", "damat", "derimod",
                            "ecrou", "hatemoglu", "hotici", "lufian", "naramaxx",
                            r"\bflo\b", "deichmann", "greyder", "intersport",
                            "fenerium", "gs store",
                            # Elektronik
                            "media markt", "arcelik", "casper", r"\bdyson\b", r"\blg\b",
                            # Ev & Yaşam
                            "bella maison", "english home", "enza home",
                            "karaca", "madame coco", "emsan", "korkmaz",
                            # Kozmetik & Parfüm
                            "flormar", "golden rose", "kiko", "lelas", "cella",
                            "d&p parfum", "flormar",
                            # Bebek
                            "chicco", "ebebe", "mamino"],
    "Ulaşım":             ["akaryakit", "petrol", r"\bshell\b", r"\bbp\b", "opet",
                            r"\btotal\b", "otopark", "otoyol", r"\bhgs\b", r"\bogs\b",
                            r"\byss\b", "kopru gecis",
                            "motorlu tasit", r"\bmtv\b", r"\bmetro\b", "taksi",
                            r"\buber\b", "bitaksi", "marti", "gopark", "filo otomotiv",
                            "uzl filo",
                            "easypark", "parkmatic", "tuvturk",
                            "sabiha gokcen", r"\bsaw\b",
                            r"\botogar\b", "karayollari"],
    "Faiz / Vergi":       ["faiz", "kkdf", "bsmv", "komisyon", r"\bvergi\b", "masraf",
                            "alisveris faizi"],
}

def normalize(text):
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    tr = str.maketrans("şğüöıçşğüöiç", "sguoicsguoic")
    return text.translate(tr)


FOREIGN_CCY_RE = re.compile(
    r"\(\s*[\d.,]+\s+[A-Z]{3}\s*\)|\(\s*[A-Z]{3}\s+[\d.,]+\s*\)"
)


def kategori_bul(aciklama):
    if FOREIGN_CCY_RE.search(aciklama):
        return "Yurtdışı Harcamalar"
    n = normalize(aciklama)
    for kat, kelimeler in KATEGORILER.items():
        for k in kelimeler:
            pat = k if (r"\b" in k or r"\s" in k) else re.escape(k)
            if re.search(pat, n):
                return kat
    return "Diğer"


def parse_tutar(metin):
    if not metin:
        return None
    metin = metin.replace("TL", "").strip()
    negative = metin.startswith("-")
    metin = metin.replace("-", "").strip()
    metin = metin.replace(".", "").replace(",", ".")
    try:
        val = float(metin)
        return -val if negative else val
    except ValueError:
        return None


def format_tl(val):
    return f"{val:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")


AYLAR = {1:"Ocak",2:"Şubat",3:"Mart",4:"Nisan",5:"Mayıs",6:"Haziran",
         7:"Temmuz",8:"Ağustos",9:"Eylül",10:"Ekim",11:"Kasım",12:"Aralık"}

TUTAR_SON = re.compile(r"(?<!\d)([\s\-]*[\d.,]+\s*TL)$")
EKSTRE_BORC = re.compile(r"ekstre borcu\s+([\d.,]+\s*TL)", re.IGNORECASE)
MIN_ODEME   = re.compile(r"minimum \xf6deme tutar\u0131\s+([\d.,]+\s*TL)", re.IGNORECASE)

CID_MAP = {7:"ö", 8:"Ö", 9:"Ş", 10:"ü", 11:"ğ", 12:"ş",
           13:"İ", 14:"Ü", 15:"Ğ", 16:"Ç", 17:"ç"}
CID_RE  = re.compile(r"\(cid:(\d+)\)")

def cid_temizle(text):
    return CID_RE.sub(lambda m: CID_MAP.get(int(m.group(1)), ""), text)


def parse_kart(pdf_path):
    islemler = []
    ekstre_borcu  = None
    min_odeme     = None
    ozet          = None
    ekstre_ay     = None
    ekstre_yil    = None
    with pdfplumber.open(pdf_path) as pdf:
        all_lines = []
        for page in pdf.pages:
            text = cid_temizle(page.extract_text() or "")
            all_lines.extend(text.split("\n"))

    # DEBUG: tüm parse edilen işlemler — sorun çözülünce kaldır

    # Taksitli işlemlerde tutar bazen bir sonraki satırda gelir.
    # Tarihle başlayıp TL içermeyen satırları devam satırıyla birleştir.
    merged = []
    i = 0
    while i < len(all_lines):
        line = all_lines[i]
        if (re.match(r"^\s*\d{2}/\d{2}/\d{4}", line)
                and not TUTAR_SON.search(line)
                and i + 1 < len(all_lines)):
            nxt = all_lines[i + 1].strip()
            if TUTAR_SON.search(nxt) and not re.match(r"^\d{2}/\d{2}/\d{4}", nxt):
                merged.append(line.strip() + " " + nxt)
                i += 2
                continue
        merged.append(line)
        i += 1
    all_lines = merged

    for line in all_lines:
        if ekstre_ay is None:
            m = re.search(r"[Ee]kstre tarihi\s+\d{2}/(\d{2})/(\d{4})", line)
            if m:
                ekstre_ay  = AYLAR.get(int(m.group(1)))
                ekstre_yil = m.group(2)
        if ekstre_borcu is None:
            m = re.search(r"[Ee]kstre borcu\s+([\d.,]+\s*TL)", line)
            if m:
                ekstre_borcu = parse_tutar(m.group(1))
        if min_odeme is None:
            m = re.search(r"[Mm]inimum\s+\S+\s+tutar\S*\s+([\d.,]+\s*TL)", line)
            if m:
                min_odeme = parse_tutar(m.group(1))
        if ozet is None:
            vals = re.findall(r"[\d.,]+ TL", line)
            if len(vals) == 6:
                parsed = [parse_tutar(v) for v in vals]
                if all(v is not None for v in parsed):
                    ozet = {
                        "onceki":    parsed[0],
                        "odeme":     parsed[1],
                        "harcama":   parsed[2],
                        "nakit":     parsed[3],
                        "faiz":      parsed[4],
                        "ekstre":    parsed[5],
                    }
        line = line.strip()
        if not re.match(r"^\d{2}/\d{2}/\d{4}", line):
            continue
        m = TUTAR_SON.search(line)
        if not m:
            continue
        tutar = parse_tutar(m.group(1))
        if tutar is None:
            continue

        rest     = line[11:].strip()
        aciklama = rest[:rest.rfind(m.group(1))].strip()

        taksit_m = re.search(r"\([^)]*\d[\d.,]* TL\)\s*(\d+/\d+)", aciklama)
        taksit   = taksit_m.group(1) if taksit_m else None

        aciklama = re.sub(r"\([^)]*\d[\d.,]* TL\)\s*\d+/\d+", "", aciklama).strip()
        aciklama = re.sub(r"\s+ISTANBUL\s+TR\b", "", aciklama).strip()

        islemler.append({
            "aciklama": aciklama,
            "tutar":    tutar,
            "taksit":   taksit,
            "kategori": kategori_bul(aciklama),
        })

    return islemler, ekstre_borcu, min_odeme, ozet, ekstre_ay, ekstre_yil


def yaz_rapor(f, islemler, ekstre_borcu=None, min_odeme=None, ozet=None, ekstre_ay=None):
    harcamalar  = [i for i in islemler if i["tutar"] > 0]
    odeme_tutari = sum(abs(i["tutar"]) for i in islemler if i["tutar"] < 0)

    grp: dict[str, list] = {}
    for i in harcamalar:
        grp.setdefault(i["kategori"], []).append(i)

    KATEGORI_SIRASI = [
        "Dijital / Abonelik", "Online Alışveriş", "Fatura / Hizmet",
        "Giyim / Alışveriş", "Sağlık", "Market / Gıda", "Yemek / Restoran",
        "Kahve", "Seyahat", "Ulaşım", "Oyuncak", "Yurtdışı Harcamalar",
    ]
    sirali = [(k, grp[k]) for k in KATEGORI_SIRASI if k in grp]
    for k, v in grp.items():
        if k not in KATEGORI_SIRASI and k not in ("Diğer", "Faiz / Vergi"):
            sirali.append((k, v))
    if "Diğer" in grp:
        sirali.append(("Diğer", grp["Diğer"]))
    if "Faiz / Vergi" in grp:
        sirali.append(("Faiz / Vergi", grp["Faiz / Vergi"]))

    genel_toplam = sum(i["tutar"] for i in harcamalar)

    SEP = "─" * 42

    for idx, (kat, islem_listesi) in enumerate(sirali):
        kat_toplam = sum(i["tutar"] for i in islem_listesi)
        oran       = kat_toplam / genel_toplam * 100 if genel_toplam else 0

        f.write(f"{SEP}\n")
        f.write(f"{kat.upper()}  {format_tl(kat_toplam)}  %{oran:.0f}\n")
        f.write(f"{SEP}\n")

        satirlar: list[dict] = []
        tekil: dict[str, dict] = {}
        for i in islem_listesi:
            if i.get("taksit"):
                satirlar.append({"aciklama": i["aciklama"], "tutar": i["tutar"], "taksit": i["taksit"]})
            else:
                if i["aciklama"] not in tekil:
                    tekil[i["aciklama"]] = {"tutar": 0, "taksit": None}
                tekil[i["aciklama"]]["tutar"] += i["tutar"]
        for aciklama, info in tekil.items():
            satirlar.append({"aciklama": aciklama, **info})

        for satir in sorted(satirlar, key=lambda x: x["tutar"], reverse=True):
            taksit_str = f" ({satir['taksit']} Taksit)" if satir.get("taksit") else ""
            f.write(f"{satir['aciklama']}  {format_tl(satir['tutar'])}{taksit_str}\n")

    odeme_etiket = f"{ekstre_ay} ödemesi" if ekstre_ay else "Ödeme"

    f.write(f"\nÖZET\n")
    f.write(f"{SEP}\n")
    if ozet:
        f.write(f"Önceki ekstre borcu                    {format_tl(ozet['onceki'])}\n")
        f.write(f"{odeme_etiket:<38}-{format_tl(ozet['odeme'])}\n")
        f.write(f"Harcamalar ve geçmiş aydan taksitler   {format_tl(ozet['harcama'])}\n")
        if ozet['nakit']:
            f.write(f"Nakit avans                            {format_tl(ozet['nakit'])}\n")
        f.write(f"Faiz, vergiler ve diğer                {format_tl(ozet['faiz'])}\n")
        f.write(f"{SEP}\n")
        f.write(f"Ekstre borcu                           {format_tl(ozet['ekstre'])}\n")
    else:
        f.write(f"Toplam harcama                         {format_tl(genel_toplam)}\n")
        if ekstre_borcu is not None:
            f.write(f"Ekstre borcu                           {format_tl(ekstre_borcu)}\n")
        f.write(f"{SEP}\n")
    if min_odeme is not None:
        f.write(f"Minimum ödeme                          {format_tl(min_odeme)}\n")


def main():
    folder = Path(__file__).parent

    kart_pdfler = [
        pdf for pdf in sorted(folder.glob("*.pdf"))
        if "kredi" in normalize(pdf.name) or "ekstr" in normalize(pdf.name)
    ]

    if not kart_pdfler:
        print("Kredi kartı ekstresi PDF bulunamadı.")
        return

    for kart_pdf in kart_pdfler:
        print(f"Okunuyor: {kart_pdf.name}")
        islemler, ekstre_borcu, min_odeme, ozet, ekstre_ay, ekstre_yil = parse_kart(kart_pdf)
        print(f"{len([i for i in islemler if i['tutar'] > 0])} harcama işlemi bulundu.")

        donem = f"{ekstre_ay}_{ekstre_yil}" if (ekstre_ay and ekstre_yil) else kart_pdf.stem
        out_path = folder / f"Enpara_Rapor_{donem}.txt"
        with open(out_path, "w", encoding="utf-8") as f:
            yaz_rapor(f, islemler, ekstre_borcu, min_odeme, ozet, ekstre_ay)

        print(f"Rapor: {out_path.name}\n")


if __name__ == "__main__":
    main()