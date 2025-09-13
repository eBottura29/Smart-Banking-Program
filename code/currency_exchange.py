import json


class CurrencyConverter:
    def __init__(self, db_path="./db/currency.db"):
        with open(db_path, "r") as f:
            data = json.load(f)
        self.base = data["base"]
        self.rates = data["rates"]

    def get_rate(self, currency):
        if currency == self.base:
            return 1.0
        if currency in self.rates:
            return self.rates[currency]
        raise ValueError(f"Currency {currency} not found in database")

    def convert(self, amount, from_currency, to_currency):
        from_rate = self.get_rate(from_currency)
        to_rate = self.get_rate(to_currency)

        # Convert from source → USD → target
        usd_amount = amount / from_rate
        return usd_amount * to_rate


if __name__ == "__main__":
    converter = CurrencyConverter()

    # Example usage
    print(converter.convert(100, "EUR", "GBP"))  # Convert 100 EUR → GBP
    print(converter.convert(50, "USD", "JPY"))  # Convert 50 USD → JPY
