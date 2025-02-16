import requests
import syllables

# --- Syllable Counting ---
def count_syllables(text):
    """Count syllables using the 'syllables' package."""
    return syllables.estimate(text)

# --- Fetching Headlines ---
def get_headlines(api_key):
    """
    Fetch headlines from NewsAPI and remove trailing source info.
    """
    url = "https://newsapi.org/v2/top-headlines"
    params = {"country": "us", "apiKey": api_key, "pageSize": 20}
    response = requests.get(url, params=params)
    headlines = []
    if response.status_code == 200:
        data = response.json()
        for article in data.get("articles", []):
            title = article.get("title")
            if title:
                # Remove trailing source info (assumes " - " separates title and source)
                clean_title = title.split(" - ")[0]
                headlines.append(clean_title)
    else:
        print("Error fetching headlines:", response.status_code, response.text)
    return headlines

# --- Best Haiku Split Algorithm ---
def best_split(headline):
    """
    Attempts to split a headline into three parts to approximate a 5-7-5 haiku.
    Returns a tuple (best_split, best_error) where best_split is (line1, line2, line3).
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
    Iterates over headlines to choose the one with the best haiku split.
    Returns (haiku_split, headline, error).
    """
    headlines = get_headlines(api_key)
    best_overall, best_headline, best_err = None, None, float('inf')
    for h in headlines:
        split_val, err = best_split(h)
        if split_val and err < best_err:
            best_overall, best_headline, best_err = split_val, h, err
    return best_overall, best_headline, best_err

# --- Posting to Discord ---
def post_to_discord(webhook_url, message):
    """
    Posts a message to Discord via the provided webhook URL.
    """
    data = {"content": message}
    requests.post(webhook_url, json=data)

# --- Main Execution ---
def main():
    # Replace these with your actual keys/URLs
    API_KEY = "079b795fbf844ab3876b199b0b236b37"
    DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1339685758273061016/COYZDNyTFckb1PX2PDalu-LUnaea-BEIeQsG9c4ca1my9x2dZTmITiFinjRkjN0Dhini"
    
    haiku, headline, error = generate_haiku(API_KEY)
    if haiku:
        # Append the signature "~Group-14" at the end
        message = (f"Best headline: '{headline}' (error: {error})\n\n" +
                   "\n".join(haiku) +
                   "\n\n~Group-14")
        print("Generated Haiku:\n")
        print(message)
        # Post to Discord if a valid webhook URL is provided.
        if DISCORD_WEBHOOK_URL and DISCORD_WEBHOOK_URL != "https://discord.com/api/webhooks/1339685758273061016/COYZDNyTFckb1PX2PDalu-LUnaea-BEIeQsG9c4ca1my9x2dZTmITiFinjRkjN0Dhini":
            post_to_discord(DISCORD_WEBHOOK_URL, message)
    else:
        print("Could not generate a haiku.")

if __name__ == "__main__":
    main()
