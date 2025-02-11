import requests
import re
import syllables

def count_syllables(text):
    """
    Count syllables using the 'syllables' package.
    """
    return syllables.estimate(text)

def get_headlines(api_key):
    """
    Fetches headlines from NewsAPI and cleans them by removing trailing source info.
    """
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "us",
        "apiKey": api_key,
        "pageSize": 20
    }
    response = requests.get(url, params=params)
    headlines = []
    if response.status_code == 200:
        data = response.json()
        for article in data.get("articles", []):
            title = article.get("title")
            if title:
                
                clean_title = title.split(" - ")[0]
                headlines.append(clean_title)
    else:
        print("Error fetching headlines:", response.status_code, response.text)
    return headlines

def best_split(headline):
    """
    Attempts to split a headline into three parts (lines) to match a 5-7-5 haiku.
    Tries every possible split and calculates the total error relative to (5, 7, 5).
    Returns a tuple (best_split, best_error) where best_split is a tuple of three strings.
    """
    words = headline.split()
    n = len(words)
    if n < 3:
        return None, None

    
    syl_counts = [count_syllables(word) for word in words]
    best, best_err = None, float('inf')

    
    for i in range(1, n - 1):
        for j in range(i + 1, n):
            syl1 = sum(syl_counts[:i])
            syl2 = sum(syl_counts[i:j])
            syl3 = sum(syl_counts[j:])
            error = abs(syl1 - 5) + abs(syl2 - 7) + abs(syl3 - 5)
            if error < best_err:
                best_err = error
                best = (" ".join(words[:i]), " ".join(words[i:j]), " ".join(words[j:]))
                if best_err == 0:
                    
                    return best, 0
    return best, best_err

def generate_haiku(api_key):
    """
    Iterates over the fetched headlines and uses best_split() on each.
    Returns the haiku split with the smallest error.
    """
    headlines = get_headlines(api_key)
    best_overall, best_headline, best_err = None, None, float('inf')
    for h in headlines:
        split_val, err = best_split(h)
        if split_val and err < best_err:
            best_overall, best_headline, best_err = split_val, h, err
    return best_overall, best_headline, best_err

if __name__ == "__main__":
    API_KEY = "079b795fbf844ab3876b199b0b236b37" 
    haiku, headline, error = generate_haiku(API_KEY)
    if haiku:
        print(f"Best headline: '{headline}' with error: {error}\n")
        print("\n".join(haiku))
    else:
        print("Could not generate a haiku.")
