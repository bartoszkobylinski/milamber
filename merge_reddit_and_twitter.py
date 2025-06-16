import json
from datetime import datetime

def merge_reddit_and_twitter(reddit_file: str, twitter_file: str, output_file: str):
    """
    Łączy posty z Reddita i tweety z Twittera w jeden plik JSON.
    Normalizuje strukturę jako lista obiektów ze wspólnymi polami:
      - id
      - date (ISO 8601)
      - content
      - url
      - source ("reddit" lub "twitter")
    """
    merged = []

    # Wczytaj i przetwórz posty z Reddita
    with open(reddit_file, "r", encoding="utf-8") as f:
        reddit_posts = json.load(f)
    for post in reddit_posts:
        created = post.get("created_utc")
        try:
            date_iso = datetime.utcfromtimestamp(float(created)).isoformat() + "Z"
        except Exception:
            date_iso = None
        content = post.get("title", "")
        selftext = post.get("selftext", "")
        if selftext:
            content = f"{content}\n\n{selftext}"
        merged.append({
            "id": post.get("id"),
            "date": date_iso,
            "content": content,
            "url": post.get("url") or post.get("permalink"),
            "source": "reddit"
        })

    # Wczytaj i przetwórz tweety z Twittera
    with open(twitter_file, "r", encoding="utf-8") as f:
        tweets = json.load(f)
    for tweet in tweets:
        merged.append({
            "id": tweet.get("id"),
            "date": tweet.get("date"),
            "content": tweet.get("content"),
            "url": tweet.get("url"),
            "source": "twitter"
        })

    # Zapisz wynik
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"Zapisano {len(merged)} wpisów w pliku '{output_file}'")

if __name__ == "__main__":
    # Nazwy plików (zmodyfikuj według potrzeb)
    reddit_file = "r_norge_may2025_posts.json"
    twitter_file = "Po_nordycku_tweets_may2025_norway.json"
    output_file = "merged_norway_discussion.json"
    merge_reddit_and_twitter(reddit_file, twitter_file, output_file)
