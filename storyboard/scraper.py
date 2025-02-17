
import requests
from bs4 import BeautifulSoup
import sqlite3
import time

# Create or connect to a database
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create table for storing Airbnb listings
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Appartments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        price TEXT,
        link TEXT
    )
""")
conn.commit()

# Function to scrape Airbnb data
def scrape_airbnb(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch data: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Airbnb listings container (modify this if structure changes)
    listings = soup.find_all("div", class_="some-listing-class")

    for listing in listings:
        title = listing.find("h2").text.strip() if listing.find("h2") else "No Title"
        price = listing.find("span", class_="price").text.strip() if listing.find("span", class_="price") else "No Price"
        link = "https://www.airbnb.com" + listing.find("a")["href"] if listing.find("a") else "No Link"

        print(f"Inserting: {title} | {price} | {link}")

        # Insert into database
        cursor.execute("INSERT INTO listings (title, price, link) VALUES (?, ?, ?)", (title, price, link))
        conn.commit()

        time.sleep(2)  # Avoid getting blocked

# Example: Modify the URL to match your search query
airbnb_url = "https://www.airbnb.com/s/Paris--France/homes"
scrape_airbnb(airbnb_url)

# Close the database connection
conn.close()
