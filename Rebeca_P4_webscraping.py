#Nina Freeman, Lydia McPhee, Rebeca Mousser, Mason Stewart
#P4 General Conference Webscraping

from bs4 import BeautifulSoup
import requests
import pandas as pd
import sqlalchemy
import matplotlib.pyplot as plt


def create_engine():
    """
    Creates and returns a SQLAlchemy engine for the is303 PostgreSQL database.
    Update username/password if your PostgreSQL setup is different.
    """
    username = "postgres"
    password = "18313180"
    host = "localhost"
    port = "5432"
    database = "IS303"

    connection_string = (
        f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
    )

    return sqlalchemy.create_engine(connection_string)

def drop_table(engine):
    """
    Drops the general_conference table if it already exists.
    """
    with engine.connect() as conn:
        conn.execute(sqlalchemy.text("DROP TABLE IF EXISTS general_conference"))
        conn.commit()


def save_talk_to_database(talk_dict, engine):
    """
    Saves one talk dictionary as one row in the general_conference table.
    """
    talk_df = pd.DataFrame([talk_dict])

    talk_df.to_sql(
        "general_conference",
        con=engine,
        if_exists="append",
        index=False
    )

def get_all_talks():
    """
    Loads all rows from the general_conference table in postgres.
    """
    engine = create_engine()
    return pd.read_sql("SELECT * FROM general_conference", engine)

def scrape_data():
    """
    Scrapes the talk data and saves it to postgreSQL
    """
    print("Scraping data...")

    engine = create_engine()
    drop_table(engine)

    talks_data = scrape_basic_info()

    for talk in talks_data:
        save_talk_to_database(talk, engine)

    print("You've saved the scraped data to your postgres database.")


def get_talk_links():
    """
    Gets all individual talk links from October 2025 General Conference.
    Skips session pages.
    """
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


def get_standard_works_dict():
    """
    Returns a blank dictionary with all standard works books initialized to 0.
    """
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



def scrape_basic_info():
    """
    Scrapes speaker, talk title, kicker, and scripture references for each talk.
    """
    talk_links = get_talk_links()
    talks_data = []

    for url in talk_links:
        print(f"Scraping: {url}")

        response = requests.get(url)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.content, "html.parser")

        # ---- TITLE ----
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else ""

        # Skip sustaining talk
        if "sustaining" in title.lower():
            continue

        # ---- SPEAKER ----
        speaker_tag = soup.find(string=lambda text: text and text.strip().startswith("By "))
        speaker = speaker_tag.strip()[3:] if speaker_tag else ""

                # ---- KICKER ----
        kicker_tag = soup.find("p", class_="kicker")
        kicker = kicker_tag.text.strip() if kicker_tag else ""

        # Create a fresh dictionary for this talk
        scripture_dict = get_standard_works_dict()
        scripture_dict["Speaker_Name"] = speaker
        scripture_dict["Talk_Name"] = title
        scripture_dict["Kicker"] = kicker

        # Find footnotes section
        footnotes_section = soup.find("footer")

        # Handle talks with no footnotes
        if footnotes_section is not None:
            text = footnotes_section.get_text(" ", strip=True).lower()

            # Count how many times each book appears
            for key in scripture_dict:
                if key in ["Speaker_Name", "Talk_Name", "Kicker"]:
                    continue
                scripture_dict[key] = text.count(key.lower())

        talks_data.append(scripture_dict)

    return talks_data



def show_all_talks_chart(df):
    """
    Bar chart of total scripture references across all talks.
    Only shows books referenced more than 2 times total.
    """
    scripture_df = df.drop(columns=["Speaker_Name", "Talk_Name", "Kicker"])
    totals = scripture_df.sum().sort_values(ascending=False)
    totals = totals[totals > 2]

    plt.figure(figsize=(14, 6))
    plt.bar(totals.index, totals.values)
    plt.title("Standard Works Referenced in General Conference")
    plt.xlabel("Standard Works Books")
    plt.ylabel("# Times Referenced")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


def show_single_talk_chart(df, talk_name):
    """
    Bar chart of scripture references for one specific talk.
    Only shows books with at least 1 reference.
    """
    talk_row = df[df['Talk_Name'] == talk_name]
    scripture_data = talk_row.drop(columns=['Speaker_Name', 'Talk_Name', 'Kicker']).transpose()
    scripture_data.columns = ['count']
    scripture_data = scripture_data[scripture_data['count'] >= 1]

    plt.figure(figsize=(14, 6))
    plt.bar(scripture_data.index, scripture_data['count'])
    plt.title(f'Standard Works Referenced in: {talk_name}')
    plt.xlabel('Standard Works Books')
    plt.ylabel('# Times Referenced')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


def show_summaries():
    """
    Handles the Part 2 menu: lets user view an all-talks chart
    or pick a specific talk to chart.
    """
    choice = input(
        "You selected to see summaries. \n" \
        "Enter 1 to see a summary of all talks. \n"
        "Enter 2 to select a specific talk.\n"
        "Enter anything else to exit: "
    )

    if choice == '1':
        df = get_all_talks()
        show_all_talks_chart(df)

    elif choice == '2':
        df = get_all_talks()

        print("\nThe following are the names of speakers and their talks:")
        talk_lookup = {}
        for index, row in df.iterrows():
            number = index + 1
            print(f"{number}: {row['Speaker_Name']} - {row['Talk_Name']}")
            talk_lookup[number] = row['Talk_Name']
        raw_choice = input("\nPlease enter the number of the talk you want to see summarized: ").strip()

        if raw_choice.isdigit():
            talk_number = int(raw_choice)
            if talk_number in talk_lookup:
                show_single_talk_chart(df, talk_lookup[talk_number])
            else:
                print("That number doesn't match any talk.")
        else:
            print("Invalid input. Please enter a number.")

    else:
        print("Closing the program.")


def main():
    user_input = input(
        "If you want to scrape data, enter 1. \n"
        "If you want to see summaries of stored data, enter 2. \n"
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