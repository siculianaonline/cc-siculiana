import json
import urllib.request
from datetime import datetime
from email.utils import format_datetime
from xml.sax.saxutils import escape

URL_JSON = "https://siculiana.civicam.it/ajax.php?azione=mediaElementsData&p=1&orderBy=0&idLiveEscluso=0"
BASE_SITE = "https://siculiana.civicam.it"
OUTPUT_FILE = "feed.xml"

MESI_IT = {
    "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4,
    "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8,
    "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12
}

def parse_data_italiana(testo):
    giorno, mese_nome, anno = testo.strip().split(" ")
    mese = MESI_IT[mese_nome.lower()]
    return datetime(int(anno), mese, int(giorno))

def genera_feed():
    req = urllib.request.Request(URL_JSON, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as risposta:
        dati = json.loads(risposta.read().decode("utf-8"))

    items_xml = []
    for elemento in dati.get("aLives", []):
        titolo_originale = elemento.get("titolo", "").strip()
        data_testo = elemento.get("inizio", "").strip()
        link = BASE_SITE + elemento.get("uri", "")
        data_pub = parse_data_italiana(data_testo)
        pub_date_rfc822 = format_datetime(data_pub)
        durata = elemento.get("durata", "")
        categoria = escape(elemento.get("catLabel", ""))
        guid = elemento.get("id", link)

        titolo_nuovo = escape(f"VIDEO - CONSIGLIO COMUNALE DEL {data_testo.upper()}")

        poster_path = elemento.get("validPoster", "")
        poster_url = BASE_SITE + "/" + poster_path.lstrip("/") if poster_path else ""

        img_html = f'<img src="{poster_url}" alt="{escape(titolo_originale)}" /><br/>' if poster_url else ""
        descrizione_testo = f"{titolo_originale} - Durata: {durata}"
        descrizione_html = f"{img_html}{escape(descrizione_testo)}"

        img_tags = ""
        if poster_url:
            img_tags = f"""
      <enclosure url="{escape(poster_url)}" type="image/jpeg" length="0" />
      <media:thumbnail url="{escape(poster_url)}" />"""

        item = f"""    <item>
      <title>{titolo_nuovo}</title>
      <link>{escape(link)}</link>
      <guid isPermaLink="false">{guid}</guid>
      <pubDate>{pub_date_rfc822}</pubDate>
      <description>{escape(descrizione_testo)}</description>
      <content:encoded><![CDATA[{descrizione_html}]]></content:encoded>{img_tags}
    </item>"""
        items_xml.append(item)

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>Consiglio Comunale Siculiana - CiviCam</title>
    <link>{BASE_SITE}</link>
    <description>Feed generato automaticamente dai contenuti CiviCam di Siculiana</description>
    <language>it-it</language>
{chr(10).join(items_xml)}
  </channel>
</rss>"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(rss)

    print(f"Feed generato con {len(dati.get('aLives', []))} elementi.")

if __name__ == "__main__":
    genera_feed()
