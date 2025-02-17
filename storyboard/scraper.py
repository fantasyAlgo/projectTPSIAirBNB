
import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import random

# Create or connect to a database
conn = sqlite3.connect("database2.db")
cursor = conn.cursor()

# Create table for storing Airbnb listings
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Appartments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        price TEXT,
        link_img TEXT,
        description TEXT
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
    listings = soup.find_all("div", class_="c82435a4b8 a178069f51 a6ae3c2b40 a18aeea94d d794b7a0f7 f53e278e95 c6710787a4")

    for listing in listings:
        title = listing.find("div", class_="f6431b446c a15b38c233").text.strip()
        descriptions = listing.find_all("div", class_="abf093bdfe")
        final_description = ""
        for description in descriptions:
            if len(description.text.strip().split(" ")) > 7:
                final_description = description.text.strip()
                break

        price = random.random()*10
        link = listing.find('img', {'data-testid' : 'image'})['src']

        print(f"Inserting: {title} | {price} | {link} | {final_description[:10]}")

        # Insert into database
        cursor.execute("INSERT INTO Appartments (title, price, link_img, description) VALUES (?, ?, ?, ?)", (title, price, link, final_description))
        conn.commit()

        time.sleep(2)  # Avoid getting blocked

# Example: Modify the URL to match your search query
#airbnb_url = "https://www.booking.com/searchresults.html?aid=2425901&label=bra115jc-1DCAEoggI46AdIM1gDaHGIAQGYATG4ARnIAQ_YAQPoAQH4AQKIAgGoAgO4AuO5zb0GwAIB0gIkNzBlMWE3NGUtYTY0Ny00ZWZmLWE0ZjktNmU1NzQ3NWNlNTAz2AIE4AIB&dest_id=-130386&dest_type=city&group_adults=2&req_adults=2&no_rooms=1&group_children=null&req_children=null"
airbnb_url = "https://www.booking.com/searchresults.html?label=bra115jc-1DCAEoggI46AdIM1gDaHGIAQGYATG4ARnIAQ_YAQPoAQH4AQKIAgGoAgO4AuO5zb0GwAIB0gIkNzBlMWE3NGUtYTY0Ny00ZWZmLWE0ZjktNmU1NzQ3NWNlNTAz2AIE4AIB&sid=3f57d673ed03132fda8b83070eb7d920&aid=2425901&checkin=2025-02-22&checkout=2025-02-23&dest_id=-132007&dest_type=city&group_adults=null&req_adults=null&no_rooms=null&group_children=null&req_children=null"

scrape_airbnb(airbnb_url)

# Close the database connection
conn.close()
