import json
import argparse
from collections import defaultdict
from pprint import pprint

# Ustal zestaw docelowych flairów (w lower-case do porównań)
TARGET_FLAIRS = {"artikkel", "nyheter", "politikk"}

def load_posts(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def filter_and_group(posts):
    """
    Filtruje listę postów, zostawiając tylko te z flairami Artikkel, Nyheter, Politikk,
    a następnie grupuje je według flairu (lower-case).
    """
    groups = defaultdict(list)
    for p in posts:
        flair = p.get("flair")
        if flair and flair.lower() in TARGET_FLAIRS:
            groups[flair.lower()].append(p)
    return groups

def sort_groups(groups, metric):
    """
    Dla każdej grupy (flair) sortuje listę postów malejąco wg zadanego metricu.
    """
    for flair, items in groups.items():
        groups[flair] = sorted(items, key=lambda x: x.get(metric, 0), reverse=True)
    return groups

def summarize(groups, metric, top_n=None):
    """
    Tworzy podsumowanie dla każdej grupy:
      - count: liczba postów
      - total_<metric>: suma wartości metricu
      - avg_<metric>: średnia wartość metricu
      - top_posts: lista top_n postów wg metricu
    """
    summary = {}
    for flair, items in groups.items():
        count = len(items)
        total = sum(item.get(metric, 0) for item in items)
        avg = total / count if count else 0
        summary[flair] = {
            "count": count,
            f"total_{metric}": total,
            f"avg_{metric}": round(avg, 2),
            "top_posts": items[:top_n] if top_n else items
        }
    return summary

def main():
    parser = argparse.ArgumentParser(
        description="Grupuje i sortuje posty z r/norge wg trzech flairów i metryki aktywności."
    )
    parser.add_argument(
        "json_file",
        help="ścieżka do pliku z postami (JSON)"
    )
    parser.add_argument(
        "--metric",
        choices=["score", "num_comments"],
        default="num_comments",
        help="metryka zaangażowania do sortowania (domyślnie num_comments)"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="ile najlepszych postów z każdego flairu wypisać"
    )
    parser.add_argument(
        "--output",
        help="ścieżka do pliku JSON, w którym zapisać wynik; jeśli brak, wypisze na konsolę"
    )
    args = parser.parse_args()

    posts = load_posts(args.json_file)
    groups = filter_and_group(posts)
    groups = sort_groups(groups, args.metric)
    summary = summarize(groups, args.metric, top_n=args.top)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"Wynik zapisano do {args.output}")
    else:
        print("### Podsumowanie flairów i aktywności ###")
        pprint(summary)

if __name__ == "__main__":
    main()
