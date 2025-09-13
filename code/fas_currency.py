import requests
from dotenv import load_dotenv
import os
import json
import datetime


def fetch_and_store():
    load_dotenv()
    key = os.getenv("CURRENCY_KEY")

    if not key:
        raise ValueError("CURRENCY_KEY not found in .env file")

    url = f"http://apilayer.net/api/live?access_key={key}&source=USD&format=1"
    response = requests.get(url)
    data = response.json()

    if not data.get("success", False):
        raise Exception(f"API request failed: {data}")

    quotes = data["quotes"]

    now = datetime.datetime.utcnow().isoformat()

    # Prepare cleaned dictionary: {"EUR": 0.94, "GBP": 0.86, ...}
    cleaned = {"last_updated": now, "base": "USD", "rates": {currency[3:]: rate for currency, rate in quotes.items()}}

    with open("./db/currency.db", "w") as f:
        json.dump(cleaned, f, indent=4)

    print("Rates successfully stored in currency.db")


if __name__ == "__main__":
    fetch_and_store()
