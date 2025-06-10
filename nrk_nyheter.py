import feedparser
import json
from datetime import datetime

# Lista RSS feedów NRK z kategoriami
RSS_FEEDS = {
    "Toppsaker": "https://www.nrk.no/toppsaker.rss",
    "Nyheter": "https://www.nrk.no/nyheter/siste.rss",
    "Innenriks": "https://www.nrk.no/norge/toppsaker.rss",
    "Urix": "https://www.nrk.no/urix/toppsaker.rss",
    "Sápmi": "https://www.nrk.no/sapmi/oddasat.rss",
    "Sport": "https://www.nrk.no/sport/toppsaker.rss",
    "Kultur": "https://www.nrk.no/kultur/toppsaker.rss",
    "Livsstil": "https://www.nrk.no/livsstil/toppsaker.rss",
    "Viten": "https://www.nrk.no/viten/toppsaker.rss",
    "Dokumentar": "https://www.nrk.no/dokumentar/toppsaker.rss",
    "Ytring": "https://www.nrk.no/ytring/toppsaker.rss",
    "Filmpolitiet": "https://www.nrk.no/filmpolitiet/toppsaker.rss",
    "Musikkanmeldelser": "https://www.nrk.no/kultur/musikkanmeldelser.rss"
}

# Zakres dat: maj 2025
START_YEAR, START_MONTH = 2025, 5
END_YEAR, END_MONTH = 2025, 5

articles_by_category = {}

for category, url in RSS_FEEDS.items():
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries:
        # Próbujemy odczytać pole published
        published = entry.get("published", entry.get("updated", ""))
        if not published:
            continue
        # Parsowanie daty
        try:
            dt = datetime(*entry.published_parsed[:6])
        except Exception:
            continue
        # Filtracja na maj 2025
        if dt.year == START_YEAR and dt.month == START_MONTH:
            articles.append({
                "title": entry.title,
                "link": entry.link,
                "published": dt.isoformat()
            })
    articles_by_category[category] = articles

# Zapis do pliku JSON
output_file = "nrk_may2025_articles.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(articles_by_category, f, ensure_ascii=False, indent=2)

# Podsumowanie wyników
summary = {cat: len(arts) for cat, arts in articles_by_category.items()}
print("Liczba artykułów z maja 2025 wg kategorii:")
for cat, count in summary.items():
    print(f"  {cat}: {count}")
print(f"Zapisano szczegóły w pliku {output_file}")
