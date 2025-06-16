import os
import json
from openai import OpenAI

# ——————————————————————————————————————————————
# 1) Konfiguracja
OPENAI_API_KEY = os.getenv("OPENAI_APIKEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Ścieżki do plików
MERGED_FILE    = "merged_norway_discussion.json"
PAST_TOPICS    = "previous_podcast_topics.txt"   # plik z 1 tematem na wiersz
OUTPUT_CANDIDATES = "candidate_topics.json"
OUTPUT_TOP10      = "top10_catchy_topics.txt"
# ——————————————————————————————————————————————

def load_previous_topics(path: str) -> list[str]:
    """Wczytuje Twoje 20 poprzednich tematów, jeden wiersz = jeden temat."""
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def generate_candidate_topics(merged_json: str, n_candidates: int = 40) -> list[str]:
    """
    Pierwszy etap: LLM generuje listę kandydatów ze złączonych postów/tweetów.
    """
    with open(merged_json, encoding="utf-8") as f:
        data = json.load(f)
    contents = "\n\n---\n\n".join(entry["content"] for entry in data)

    system = (
        "Jesteś asystentem badającym treści społecznościowe. "
        "Na podstawie poniższego zbioru wpisów wygeneruj listę "
        f"{n_candidates} propozycji tematów podcastu: krótkich, chwytliwych tytułów."
    )
    user = f"Treść zbioru:\n{contents[:3000]}…"  # obetnij, by nie przekroczyć limitu promptu

    resp = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role":"system","content":system},
            {"role":"user","content":user}
        ],
        max_tokens=1024,
        temperature=0.8
    )
    # oczekujemy odpowiedzi jako lista linii
    lines = resp.choices[0].message.content.splitlines()
    candidates = [l.strip("0123456789. )") for l in lines if l.strip()]
    # jeśli jest więcej niż n_candidates, tniemy
    return candidates[:n_candidates]

def rank_by_catchiness(candidates: list[str], past_topics: list[str], top_n: int = 10) -> list[str]:
    """
    Drugi etap: few-shot ranking. Podajemy 20 starych tematów jako wzorzec, 
    model wybiera top_n najbardziej chwytliwych.
    """
    # przygotuj przykład few-shot
    few_shot = "\n".join(f"{i+1}. {t}" for i, t in enumerate(past_topics))
    cand_list = "\n".join(f"{i+1}. {t}" for i, t in enumerate(candidates))

    system = (
        "Jesteś ekspertem od chwytliwych tytułów podcastów. "
        "Poniżej masz przykłady 20 tematów, które używaliśmy w poprzednich odcinkach:\n"
        f"{few_shot}\n\n"
        "Teraz, spośród poniższych propozycji, "
        f"wybierz {top_n} NAJCHWYTLIWSZYCH tytułów (podawaj je w formie listy, "
        "każdy w osobnej linii, w kolejności od najbardziej do najmniej chwytliwego):\n"
        f"{cand_list}"
    )

    resp = client.chat.completions.create(
        model="o3",
        messages=[{"role":"system","content":system}],
        temperature=1
    )
    lines = resp.choices[0].message.content.splitlines()
    # usuń numerowanie
    return [l.strip("0123456789. )") for l in lines if l.strip()]

if __name__ == "__main__":
    # 1) Wczytaj Twoje poprzednie 20 tematów
    previous = load_previous_topics(PAST_TOPICS)

    # 2) Wygeneruj kandydatów
    candidates = generate_candidate_topics(MERGED_FILE, n_candidates=40)
    with open(OUTPUT_CANDIDATES, "w", encoding="utf-8") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)
    print(f"Pobrano {len(candidates)} kandydatów → zapisano w {OUTPUT_CANDIDATES}")

    # 3) Użyj few-shot ranking, by wybrać 10 NAJCHWYTLIWSZYCH
    top10 = rank_by_catchiness(candidates, previous, top_n=10)
    with open(OUTPUT_TOP10, "w", encoding="utf-8") as f:
        f.write("\n".join(f"{i+1}. {t}" for i,t in enumerate(top10)))
    print("Top 10 chwytliwych tematów:")
    for i, t in enumerate(top10,1):
        print(f" {i}. {t}")
