import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import re

def get_korean_tax_rate():
    url = "https://taxsummaries.pwc.com/republic-of-korea/corporate/other-taxes"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Get plain text
    text = soup.get_text(separator=' ', strip=True)

    # Normalize to lowercase for searching
    lower_text = text.lower()

    # Find the start and end of the search window
    start_idx = lower_text.find("flexible tax rate")
    end_idx = lower_text.find("korea stock exchange", start_idx)

    if start_idx == -1 or end_idx == -1:
        print("Couldn't locate required phrases.")
        return None

    snippet = text[start_idx:end_idx]  # Grab substring from 'flexible tax rate' to first 'korean stock exchange'

    numbers = re.findall(r"\d+\.?\d*\%?", snippet)

    if not numbers:
        print("No numbers found in section.")
        return None


    try:
        if len(numbers) == 1:
            value = float(numbers[0].replace('%', ''))
        else:
            value = float(numbers[1].replace('%', ''))
        return value
    except ValueError:
        print("Failed to parse number.")
        return None

def update_rates():
    rate = get_korean_tax_rate()
    if rate is None:
        print("No rate extracted.")
        return

    current_ym = datetime.now().strftime("%Y-%-m")

    try:
        df = pd.read_csv("krtax.csv")
    except FileNotFoundError:
       return None

    # Add the new column and keep the single row format
    df[current_ym] = [f"{rate}%"] 
    df.to_csv("krtax.csv", index=False)
    print(f" Updated column {current_ym}: {rate}%")

if __name__ == "__main__":
    update_rates()