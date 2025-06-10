import json
import os
from openai import OpenAI

# Ustaw swój klucz API OpenAI jako zmienną środowiskową OPENAI_API_KEY
client = OpenAI(api_key=os.getenv("OPENAI_APIKEY"))

def classify_tweet_about_norway(content: str) -> bool:
    """
    Pyta model OpenAI, czy dany tweet dotyczy Norwegii.
    Zwraca True, jeśli model odpowie "yes", w przeciwnym razie False.
    """
    prompt = (
        "You are a classifier. Answer exactly 'yes' if the following tweet is about Norway "
        "(mentions Norway, its institutions, events in the country, politics, etc.), otherwise answer exactly 'no'.\n\n"
        f"Tweet: \"{content}\"\n\n"
        "Answer:"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    answer = response.choices[0].message.content.strip().lower()
    return answer == "yes"

def filter_tweets(input_json: str, output_json: str):
    """
    Wczytuje tweety z pliku JSON, filtruje te dotyczące Norwegii
    i zapisuje je do nowego pliku JSON.
    """
    with open(input_json, "r", encoding="utf-8") as f:
        tweets = json.load(f)

    norway_tweets = []
    for tweet in tweets:
        content = tweet.get("content", "")
        if classify_tweet_about_norway(content):
            norway_tweets.append(tweet)

    # Zapisz tylko te tweety dotyczące Norwegii
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(norway_tweets, f, ensure_ascii=False, indent=2)

    print(f"Zapisano {len(norway_tweets)} tweetów dotyczących Norwegii w pliku '{output_json}'.")

if __name__ == "__main__":
    INPUT_FILE = "Po_nordycku_tweets_may2025_selenium_visible.json"
    OUTPUT_FILE = "Po_nordycku_tweets_may2025_norway.json"
    filter_tweets(INPUT_FILE, OUTPUT_FILE)
