import requests
import praw
import csv
import time
import os
from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyAkcvWCRdVrsgUqkBM1Qp9e2XWVOhZTTzg")

API_URL = "https://api.coingecko.com/api/v3/coins/markets"
PARAMS = {
    "vs_currency": "usd",
    "category": "meme-token",
    "order": "market_cap_desc",
    "per_page": 2,
    "page": 1,
    "sparkline": False
}

reddit = praw.Reddit(
    client_id="KILOuaF_m4rc7Gh4uGfh7w",
    client_secret="K8P8mynn-wiUxwMjXp7CGsZrLRVkJg",
    user_agent="tw by Economy-Froyo-5438 (twapp)",
    username="Economy-Froyo-5438",
)

def fetch_meme_coin_data():
    response = requests.get(API_URL, params=PARAMS)
    if response.status_code == 200:
        return response.json()  
    else:
        print("Error fetching meme coins:", response.status_code)
        return []

def get_reddit_data(coin_name, limit=20):
    posts = reddit.subreddit("all").search(coin_name, limit=limit)

    total_upvotes = 0
    total_comments = 0
    total_awards = 0
    num_posts = 0
    post_titles = []

    for post in posts:
        try:
            total_upvotes += post.score
            total_comments += post.num_comments
            total_awards += post.total_awards_received
            num_posts += 1
            post_titles.append(post.title) 
        except Exception as e:
            print(f"Error analyzing post for {coin_name}: {e}")

    if num_posts == 0:
        return None
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(system_instruction="there 20 post title given to you, you need to tell me how many are postive, negative and neutral. nothing else than that should be printed and"),
            contents=["\n".join(post_titles)]
        )
        overall_sentiment = response.text
        response2 = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(system_instruction="there are some given info of Coin, Market Cap, Current Price, 24h Volume, and some reddit info about coin Total Upvotes, Total Comments and Overall Sentiment so give a single verdict on it for like 15 words"),
            contents=[f"Coin: {coin_name}\nMarket Cap: {total_upvotes}\nCurrent Price: {total_comments}\n24h Volume: {total_awards}\nTotal Upvotes: {total_upvotes}\nTotal Comments: {total_comments}\nOverall Sentiment: {overall_sentiment}\nPosts: {', '.join(post_titles)}"]
        )
        verdict = response2.text
    except Exception as e:
        print(f"Error analyzing posts with Gemini for {coin_name}: {e}")
        overall_sentiment = "Error"
        verdict = "Error"


    return {
        "Total Upvotes": total_upvotes,
        "Total Comments": total_comments,
        #"Total Awards": total_awards,
        "Avg. Posts Analyzed": num_posts,
        #"Post Titles": "; ".join(post_titles),  
        "Overall Sentiment": overall_sentiment, 
        #"Engagement score":round(total_upvotes / (num_posts * total_comments) * 100),
        #"Average Upvotes Per Post": round(total_upvotes / num_posts, 2) if num_posts > 0 else 0,
        "Average Comments Per Post": round(total_comments / num_posts, 2) if num_posts > 0 else 0,
        "verdict": verdict,

    }

def save_to_csv(data, filename="meme_coin_reddit_data.csv"):
    fieldnames = ["Rank", "Coin", "Symbol", "Market Cap", "Current Price", "24h Volume","Total Upvotes", "Total Comments", "Average Comments Per Post", "Avg. Posts Analyzed","Overall Sentiment", "verdict"]

    filename = filename

    try:
        print(f"Saving {len(data)} records to {filename}...")
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)

        print(f"✅ Data saved successfully to: {filename}")
    except Exception as e:
        print(f"❌ Error writing to CSV: {e}")

def main():
    meme_coins = fetch_meme_coin_data()
    if not meme_coins:
        print("❌ Failed to fetch meme coins!")
        return

    combined_data = []

    for i, coin in enumerate(meme_coins[:10], start=1):
        coin_name = coin["name"]
        coin_symbol = coin["symbol"].upper()
        market_cap = coin["market_cap"]
        current_price = coin["current_price"]
        volume_24h = coin["total_volume"]

        print(f"🔍 Fetching Reddit data for {coin_name}...")
        reddit_data = get_reddit_data(coin_name)

        data = {
            "Rank": i,
            "Coin": coin_name,
            "Symbol": coin_symbol,
            "Market Cap": market_cap,
            "Current Price": current_price,
            "24h Volume": volume_24h
        }

        if reddit_data:
            data.update(reddit_data)
        else:
            print(f"⚠️ No Reddit data found for {coin_name}")
            data.update({
                "Total Upvotes": 0,
                "Total Comments": 0,
                "Total Awards": 0,
                "Average Upvotes Per Post": 0,
                "Average Comments Per Post": 0,
                "Number of Posts Analyzed": 0,
                "Post Titles": "",
                "Overall Sentiment": ""
            })

        combined_data.append(data)
        time.sleep(2)

    save_to_csv(combined_data)
    print("✅ Meme coin Reddit data collection completed!")

if __name__ == "__main__":
    main()
