#command to run before using code:
#pip install playwright
#playwright install

#selenium - Not working
"""
from selenium import webdriver
from selenium.webdriver.common.by import By

# Initialize WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# Open tweet URL
tweet_url = "https://x.com/elonmusk/status/1887174880527106540"
driver.get(tweet_url)

# Wait for tweet content
import time
time.sleep(5)  # Wait for content to load

# Extract tweet text
tweet_text = driver.find_element(By.CSS_SELECTOR, "article div[lang]").text

# Print tweet text
print("Tweet:", tweet_text)

# Close WebDriver
driver.quit()
"""
#saves your credentials, run it for first time
"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    page.goto("https://x.com/login")
    page.wait_for_selector("input[name='text']", timeout=60000)
    input("Press ENTER after logging in manually...")
    context.storage_state(path="twitter_login.json")
    print("✅ Session saved!")
    browser.close()

"""
# scrape tweets but only 1
"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Keep browser visible
    context = browser.new_context(storage_state="twitter_login.json")  # Load saved session
    page = context.new_page()

    # Open the search page directly (without logging in again)
    page.goto("https://x.com/search?q=dogecoin&src=typeahead_click&f=top")

    # Wait for tweets to load
    page.wait_for_selector("div[data-testid='tweetText']", timeout=10000)

    # Extract tweets
    tweets = page.locator("div[data-testid='tweetText']").all_text_contents()

    # Print tweets
    print("Top Tweets for Dogecoin:")
    for i, tweet in enumerate(tweets[:10]):  # Limit to first 10 tweets
        print(f"{i+1}. {tweet}")

    browser.close()
"""
# scrape 7-8 tweets per call
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False) 
    context = browser.new_context(storage_state="twitter_login.json")  
    page = context.new_page()

    page.goto("https://x.com/search?q=dogecoin&src=typeahead_click&f=top")


    page.wait_for_selector("div[data-testid='tweetText']", timeout=10000)


    for _ in range(10):  
        page.mouse.wheel(0, 1000)  
        time.sleep(2)  

   
    tweets = page.locator("div[data-testid='tweetText']").all_text_contents()

    
    print("\nTop Tweets for Dogecoin:")
    for i, tweet in enumerate(tweets[:20]):  
        print(f"{i+1}. {tweet.strip()}")

    browser.close()


