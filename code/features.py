from pathlib import Path
import json
from currency_exchange import CurrencyConverter
import os


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


class Features:
    def __init__(self, db_dir: Path = None):
        self.BASE_DIR = Path(__file__).resolve().parent
        if db_dir is None:
            db_dir = self.BASE_DIR.parent / "db"
        self.db_dir = Path(db_dir)
        self.user_db = self.db_dir / "user.db"
        self.database_db = self.db_dir / "database.db"
        self.currency_db = self.db_dir / "currency.db"
        self.conv = CurrencyConverter(db_path=str(self.currency_db))

    # --- helpers ---
    def _write_user_db(self, data):
        with open(self.user_db, "w") as f:
            json.dump(data, f, indent=4)

    def _read_user_db(self):
        with open(self.user_db, "r") as f:
            return json.load(f)

    def _read_database(self):
        with open(self.database_db, "r") as f:
            return json.load(f)

    def _write_database(self, data):
        with open(self.database_db, "w") as f:
            json.dump(data, f, indent=4)

    # --- authentication ---
    def login(self, username, password):
        db = self._read_database()
        key = username.upper()
        if key in db and db[key]["password"] == password:
            # Allow login even if admin, and check if activated for regular users
            if db[key].get("activated", True) or db[key].get("is_admin", False):
                self._write_user_db({"logged in": True, "account": key})
                return True
        return False

    def logout(self):
        self._write_user_db({"logged in": False, "account": ""})
        print("Logged out.")

    # --- balance & currency ---
    def view_balance(self, account):
        db = self._read_database()
        acct = db.get(account)
        if not acct:
            print("Account not found.")
            input("Press Enter to continue...")
            return
        print(f"\nBalance: {acct.get('balance', 0)} {acct.get('currency', 'USD')}")
        input("Press Enter to continue...")

    def deposit(self, account):
        try:
            amount = float(input("Amount to deposit: "))
        except ValueError:
            print("Invalid amount")
            return
        if amount <= 0:
            print("Amount must be positive")
            return
        db = self._read_database()
        db[account]["balance"] = db[account].get("balance", 0) + amount
        self._write_database(db)
        print(f"Deposit successful. New balance: {db[account]['balance']} {db[account]['currency']}")

    def withdraw(self, account):
        try:
            amount = float(input("Amount to withdraw: "))
        except ValueError:
            print("Invalid amount")
            return
        if amount <= 0:
            print("Amount must be positive")
            return
        db = self._read_database()
        bal = db[account].get("balance", 0)
        if amount > bal:
            print("Insufficient funds")
            return
        db[account]["balance"] = bal - amount
        self._write_database(db)
        print(f"Withdrawal successful. New balance: {db[account]['balance']} {db[account]['currency']}")

    def change_currency(self, account):
        new_cur = input("New currency (3-letter code): ").strip().upper()
        db = self._read_database()
        acct = db.get(account)
        if not acct:
            print("Account not found.")
            return
        old_cur = acct.get("currency", "USD")
        if new_cur == old_cur:
            print("Already using that currency")
            return
        try:
            amount = acct.get("balance", 0)
            converted = self.conv.convert(amount, old_cur, new_cur)
        except Exception as e:
            print(f"Currency conversion failed: {e}")
            return
        acct["balance"] = round(converted, 2)
        acct["currency"] = new_cur
        db[account] = acct
        self._write_database(db)
        print(f"Currency changed from {old_cur} to {new_cur}. New balance: {acct['balance']} {new_cur}")

    # --- card management ---
    def card_settings(self, account):
        db = self._read_database()
        acct = db.get(account)
        if not acct:
            print("Account not found.")
            input("Press Enter to continue...")
            return
        while True:
            print("\n1. Register Card\n2. Unregister Card\n3. View Card\n0. Back\n")
            try:
                c = int(input("> "))
            except ValueError:
                print("Enter a number")
                continue
            if c == 1:
                self.register_card(account)
            elif c == 2:
                self.unregister_card(account)
            elif c == 3:
                card = acct.get("card")
                if card:
                    print("\nCard Details:")
                    print(f"  Brand: {card.get('card', 'N/A')}")
                    print(f"  Type: {card.get('type', 'N/A')}")
                    print(f"  Number: {card.get('number', 'N/A')}")
                    print(f"  Expiration: {card.get('expiration', 'N/A')}")
                    print(f"  CVC: {card.get('CVC', 'N/A')}")
                else:
                    print("No card registered")
                input("Press Enter to continue...")
                clear_terminal()
            elif c == 0:
                break
            else:
                print("Unknown option")

    def register_card(self, account):
        db = self._read_database()
        acct = db.get(account)
        if acct.get("card"):
            print("A card is already registered. Unregister first.")
            input("Press Enter to continue...")
            return
        try:
            number = int(input("Card number (digits only): "))
            expiration = input("Expiration (MM/YY): ").strip()
            card_type = input("Card brand (VISA/MC/...): ").strip().upper() or "VISA"
            kind = input("Type (CREDIT/DEBIT): ").strip().upper() or "CREDIT"
            cvc = int(input("CVC: "))
        except ValueError:
            print("Invalid input for card fields")
            input("Press Enter to continue...")
            return
        acct["card"] = {
            "number": number,
            "expiration": expiration,
            "card": card_type,
            "type": kind,
            "CVC": cvc,
        }
        db[account] = acct
        self._write_database(db)
        print("Card registered")

    def unregister_card(self, account):
        db = self._read_database()
        acct = db.get(account)
        if not acct.get("card"):
            print("No card to unregister")
            input("Press Enter to continue...")
            return
        acct.pop("card", None)
        db[account] = acct
        self._write_database(db)
        print("Card unregistered")
