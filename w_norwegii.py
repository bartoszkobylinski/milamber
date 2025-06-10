import praw
import json

# 1) Uwierzytelnienie PRAW (na sztywno wpisane wartości)
reddit = praw.Reddit(
    client_id="fGqvN8yBxbGgOKFyhZaO-Q",
    client_secret="ci3ZV2HjZaJxidSK4FW-Wt-sPDiJwA",
    user_agent="Milamber_skrypt_v1.0"
)

# Weryfikacja, czy połączenie się powiodło:
print("Read-only:", reddit.read_only)  # powinno wypisać True

subreddit = reddit.subreddit("norge")

# 2) Zakres czasowy (Unix timestampy UTC dla maja 2025)
#     1 maja 2025 00:00:00 UTC  → 1746057600
#    31 maja 2025 23:59:59 UTC  → 1748735999
TS_START = 1746057600  # 2025-05-01 00:00:00 UTC
TS_END   = 1748735999  # 2025-05-31 23:59:59 UTC

# 3) Pobieranie postów z r/norge za maj 2025, z dodatkowymi polami 'flair' i 'post_hint'
filtered_posts = []
for submission in subreddit.new(limit=None):
    created = submission.created_utc
    if created < TS_START:
        # Gdy natrafimy na post sprzed 1 maja 2025 → dalsze też będą starsze, więc przerywamy
        break

    if TS_START <= created <= TS_END:
        # Wyciągamy flaire (może być None, jeśli post nie ma flaira)
        flair = submission.link_flair_text

        # Wyciągamy post_hint (może być "image", "link", "self", "video" itp., albo None)
        post_hint = getattr(submission, "post_hint", None)

        # Dodatkowo: zaznaczmy, czy to na pewno obrazek, bazując na post_hint lub rozszerzeniu URL
        is_image = False
        if post_hint == "image":
            is_image = True
        else:
            url = submission.url.lower() if submission.url else ""
            if url.endswith((".jpg", ".jpeg", ".png", ".gif")):
                is_image = True

        # Analogicznie możemy w razie potrzeby oznaczyć video
        is_video = (post_hint == "hosted:video" or post_hint == "rich:video")

        filtered_posts.append({
            "id": submission.id,
            "title": submission.title,
            "selftext": submission.selftext,
            "author": str(submission.author),
            "created_utc": submission.created_utc,
            "score": submission.score,
            "num_comments": submission.num_comments,
            "permalink": submission.permalink,
            "url": submission.url,
            "flair": flair,
            "post_hint": post_hint,
            "is_image": is_image,
            "is_video": is_video
        })

# 4) Zapisanie postów do pliku JSON
with open("r_norge_may2025_posts.json", "w", encoding="utf-8") as f:
    json.dump(filtered_posts, f, ensure_ascii=False, indent=2)

print(f"Pobrano {len(filtered_posts)} postów z r/norge w maju 2025.")

# 5) Pobieranie komentarzy z r/norge za maj 2025 (bez zmian – flair nie dotyczy komentarzy)
filtered_comments = []
for comment in subreddit.comments(limit=None):
    created = comment.created_utc
    if created < TS_START:
        # Gdy komentarz jest starszy niż 1 maja 2025 → przerywamy
        break
    if TS_START <= created <= TS_END:
        filtered_comments.append({
            "id": comment.id,
            "body": comment.body,
            "author": str(comment.author),
            "created_utc": comment.created_utc,
            "score": comment.score,
            "parent_id": comment.parent_id,
            "link_id": comment.link_id,
            "permalink": comment.permalink
        })

# 6) Zapisanie komentarzy do pliku JSON
with open("r_norge_may2025_comments.json", "w", encoding="utf-8") as f:
    json.dump(filtered_comments, f, ensure_ascii=False, indent=2)

print(f"Pobrano {len(filtered_comments)} komentarzy z r/norge w maju 2025.")
