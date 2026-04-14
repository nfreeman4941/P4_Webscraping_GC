#Nina Freeman, Lydia McPhee, Rebeca Mousser, Mason Stewart
#P4 General Conference Webscraping

from bs4 import BeautifulSoup
import requests
import pandas as pd
import sqlalchemy
import matplotlib.pyplot as plt

#feel free to change this however you see fit, but I think this'll be 
#the best/easiest way for the program to flow using custom functions
def scrape_data():
    print("Scraping data...")

    engine = sqlalchemy.create_engine("postgresql://postgres:your_password@localhost:5432/is303")

    engine.execute("DROP TABLE IF EXISTS general_conference;")

    data = scrape_basic_info()

    df = pd.DataFrame(data)
    df.to_sql("general_conference", engine, if_exists="append", index=False)

    print("You've saved the scraped data to your postgres database.")

def show_summaries():
    print("Showing summaries...")
    # last person who is handling the flow/menu will code this and incorporate everyone else's 

def get_talk_links():
    base_url = "https://www.churchofjesuschrist.org"
    url = base_url + "/study/general-conference/2025/10?lang=eng"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    links = []

    for a_tag in soup.select("a[href]"):
        href = a_tag["href"]

        # Must be a conference talk link
        if "/study/general-conference/2025/10/" not in href:
            continue

        # Skip session pages
        if "session" in href.lower():
            continue

        full_url = href if href.startswith("http") else base_url + href

        if full_url not in links:
            links.append(full_url)

    return links


def scrape_basic_info():
    talk_links = get_talk_links()

    talks_data = []

    for url in talk_links:
        print(f"Scraping: {url}")

        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # ---- TITLE ----
        title_tag = soup.find("p", class_="title")
        title = title_tag.text.strip() if title_tag else ""

        # Skip sustaining talk
        if "sustaining" in title.lower():
            continue

        # ---- SPEAKER ----
        speaker_tag = soup.find(string=lambda text: text and text.strip().startswith("By "))
        speaker = speaker_tag.strip()[3:] if speaker_tag else ""

        # ---- KICKER ----
        kicker_tag = soup.find("p", class_="kicker")
        kicker = kicker_tag.text.strip() if kicker_tag else ""

        # ---- SCRIPTURE DICTIONARY (ADDED FEATURE) ----
        scripture_dict = get_standard_works_dict()

        scripture_dict["Speaker_Name"] = speaker
        scripture_dict["Talk_Name"] = title
        scripture_dict["Kicker"] = kicker

        # find footnotes section
        footnotes_section = soup.find("footer", class_="notes")

        # handle talks with no footnotes
        if footnotes_section is not None:
            text = footnotes_section.text

            # count how many times each book appears
            for key in scripture_dict:
                if key in ["Speaker_Name", "Talk_Name", "Kicker"]:
                    continue
                scripture_dict[key] = text.count(key)

        # return completed dictionary per talk
        talks_data.append(scripture_dict)

    return talks_data

#Here are the standard works to count when scraping.
def get_standard_works_dict():
    return {
        'Speaker_Name': '',
        'Talk_Name': '',
        'Kicker': '',
        'Matthew': 0, 'Mark': 0, 'Luke': 0, 'John': 0, 'Acts': 0, 'Romans': 0,
        '1 Corinthians': 0, '2 Corinthians': 0, 'Galatians': 0, 'Ephesians': 0,
        'Philippians': 0, 'Colossians': 0, '1 Thessalonians': 0, '2 Thessalonians': 0,
        '1 Timothy': 0, '2 Timothy': 0, 'Titus': 0, 'Philemon': 0, 'Hebrews': 0,
        'James': 0, '1 Peter': 0, '2 Peter': 0, '1 John': 0, '2 John': 0,
        '3 John': 0, 'Jude': 0, 'Revelation': 0,

        'Genesis': 0, 'Exodus': 0, 'Leviticus': 0, 'Numbers': 0, 'Deuteronomy': 0,
        'Joshua': 0, 'Judges': 0, 'Ruth': 0, '1 Samuel': 0, '2 Samuel': 0,
        '1 Kings': 0, '2 Kings': 0, '1 Chronicles': 0, '2 Chronicles': 0,
        'Ezra': 0, 'Nehemiah': 0, 'Esther': 0, 'Job': 0, 'Psalm': 0,
        'Proverbs': 0, 'Ecclesiastes': 0, 'Song of Solomon': 0,

        'Isaiah': 0, 'Jeremiah': 0, 'Lamentations': 0, 'Ezekiel': 0, 'Daniel': 0,
        'Hosea': 0, 'Joel': 0, 'Amos': 0, 'Obadiah': 0, 'Jonah': 0,
        'Micah': 0, 'Nahum': 0, 'Habakkuk': 0, 'Zephaniah': 0, 'Haggai': 0,
        'Zechariah': 0, 'Malachi': 0,

        '1 Nephi': 0, '2 Nephi': 0, 'Jacob': 0, 'Enos': 0, 'Jarom': 0, 'Omni': 0,
        'Words of Mormon': 0, 'Mosiah': 0, 'Alma': 0, 'Helaman': 0,
        '3 Nephi': 0, '4 Nephi': 0, 'Mormon': 0, 'Ether': 0, 'Moroni': 0,

        'Doctrine and Covenants': 0,
        'Moses': 0, 'Abraham': 0,
        'Joseph Smith—Matthew': 0,
        'Joseph Smith—History': 0,
        'Articles of Faith': 0
    }

def main():
    user_input = input(
        "If you want to scrape data, enter 1. "
        "If you want to see summaries of stored data, enter 2. "
        "Enter any other value to exit the program: "
    )

    if user_input == "1":
        scrape_data()
    elif user_input == "2":
        show_summaries()
    else:
        print("Closing the program.")


if __name__ == "__main__":
    main()
    