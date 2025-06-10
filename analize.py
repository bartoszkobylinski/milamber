import json
import tiktoken
from collections import Counter

def get_unique_flairs(posts):
    """
    posts: lista słowników z kluczami takimi jak "flair"
    Zwraca set unikalnych wartości pola "flair" (pomijając None).
    """
    return {p["flair"] for p in posts if p.get("flair") is not None}

def count_flairs(file_path):
    """
    Wczytuje listę postów z pliku JSON i zwraca liczbę postów
    z flairami 'Artikkel', 'Nyheter' i 'Politikk' (case-insensitive).
    """
    with open(file_path, encoding="utf-8") as f:
        posts = json.load(f)

    flair_counter = Counter()
    for post in posts:
        flair = post.get("flair")
        if flair:
            flair_counter[flair.lower()] += 1

    return {
        "Artikkel": flair_counter.get("artikkel", 0),
        "Nyheter":  flair_counter.get("nyheter",  0),
        "Politikk": flair_counter.get("politikk", 0)
    }

def count_tokens(text: str, encoding_name: str = "gpt-3.5-turbo"):
    """
    Zwraca liczbę tokenów w danym tekście, używając biblioteki tiktoken.
    """
    tokenizer = tiktoken.encoding_for_model(encoding_name)
    tokens = tokenizer.encode(text)
    return len(tokens)

def estimate_cost_for_posts(json_path: str, price_per_1k_tokens: float, encoding_name: str = "gpt-3.5-turbo"):
    """
    Wczytuje listę postów z pliku JSON i szacuje:
    - Całkowitą liczbę tokenów (tytuł + selftext).
    - Przybliżony koszt opracowania tych tokenów w modelu.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        posts = json.load(f)

    total_tokens = 0
    for post in posts:
        title = post.get("title", "")
        selftext = post.get("selftext", "")
        full_text = title + "\n\n" + selftext
        total_tokens += count_tokens(full_text, encoding_name)

    cost = (total_tokens / 1000) * price_per_1k_tokens
    return total_tokens, cost


if __name__ == "__main__":
    # Przykład wczytania JSON-a z pliku i wywołania funkcji:
    with open("r_norge_may2025_posts.json", encoding="utf-8") as f:
        posts = json.load(f)

    unique_flairs = get_unique_flairs(posts)
    print("Unikalne flairy w maju 2025:", unique_flairs)
    counts = count_flairs("r_norge_may2025_posts.json")
    print("Liczba postów wg flairów:", counts)

    json_file = "r_norge_may2025_posts.json"

    try:
        price_input = input("Podaj cenę za 1000 tokenów w USD (np. 0.0015): ").strip()
        price_per_1k_tokens = float(price_input)
    except ValueError:
        print("Niepoprawna wartość ceny. Upewnij się, że to liczba (np. 0.0015).")
        exit(1)
    
    try:
        tokens, estimated_cost = estimate_cost_for_posts(json_file, price_per_1k_tokens)
        print(f"\nŁączna liczba tokenów: {tokens}")
        print(f"Szacowany koszt przy {price_per_1k_tokens} USD za 1000 tokenów: ${estimated_cost:.4f} USD")
    except FileNotFoundError:
        print(f"Plik '{json_file}' nie został odnaleziony.")
    except Exception as e:
        print("Wystąpił błąd podczas obliczeń:", str(e))