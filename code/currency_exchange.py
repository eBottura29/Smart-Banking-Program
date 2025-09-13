import json
from pathlib import Path


class CurrencyConverter:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).resolve().parent.parent / "db" / "currency.db"
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Currency DB not found: {self.db_path}")
        with open(self.db_path, "r") as f:
            data = json.load(f)
        self.base = data.get("base", "USD")
        self.rates = data.get("rates", {})

    def get_rate(self, currency):
        currency = currency.upper()
        if currency == self.base:
            return 1.0
        if currency in self.rates:
            return float(self.rates[currency])
        raise ValueError(f"Currency {currency} not found in database")

    def convert(self, amount, from_currency, to_currency):
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        from_rate = self.get_rate(from_currency)
        to_rate = self.get_rate(to_currency)
        # Convert from source → USD → target
        usd_amount = amount / from_rate
        return usd_amount * to_rate
