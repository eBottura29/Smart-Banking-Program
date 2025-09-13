from pathlib import Path
import json
import os
from features import Features

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR.parent / "db"
USER_DB = DB_DIR / "user.db"
DATABASE_DB = DB_DIR / "database.db"


def ensure_user_db():
    if not USER_DB.exists():
        USER_DB.parent.mkdir(parents=True, exist_ok=True)
        USER_DB.write_text(json.dumps({"logged in": False, "account": ""}, indent=4))


def ensure_database():
    if not DATABASE_DB.exists():
        DATABASE_DB.parent.mkdir(parents=True, exist_ok=True)
        default = {"ADMIN": {"password": "admin000", "currency": "USD", "balance": 0, "activated": True, "card": None, "is_admin": True}}
        DATABASE_DB.write_text(json.dumps(default, indent=4))


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def logged_out_menu():
    print("\n1. Log In\n2. Create Account\n0. Exit\n")
    ipt = input("> ")
    try:
        return int(ipt)
    except ValueError:
        print("Please enter a valid number.")
        return 0


def user_menu(is_admin=False):
    print("\n1. View Balance\n2. Deposit Money\n3. Withdraw Money\n4. Change Currency" "\n5. Card Settings\n6. Log Out")
    if is_admin:
        print("7. Admin Control Panel")
    print("0. Exit\n")
    try:
        return int(input("> "))
    except ValueError:
        print("Please enter a valid number.")
        return -1


class Admin:
    """Admin functionality integrated into main.py"""

    def __init__(self, db_dir: Path):
        self.db_dir = db_dir
        self.database_db = db_dir / "database.db"

    def _read_database(self):
        with open(self.database_db, "r") as f:
            return json.load(f)

    def _write_database(self, data):
        with open(self.database_db, "w") as f:
            json.dump(data, f, indent=4)

    # --- Admin actions ---
    def create_account(self, username, password, currency="USD", is_admin=False):
        key = username.upper()
        db = self._read_database()
        if key in db:
            return False, "Account already exists"
        db[key] = {"password": password, "currency": currency.upper(), "balance": 0, "activated": True, "card": None, "is_admin": is_admin}
        self._write_database(db)
        return True, f"Account {key} created"

    def delete_account(self, username):
        key = username.upper()
        db = self._read_database()
        if key not in db:
            return False, "Account not found"
        db.pop(key)
        self._write_database(db)
        return True, f"Account {key} deleted"

    def activate_account(self, username):
        key = username.upper()
        db = self._read_database()
        if key not in db:
            return False, "Account not found"
        db[key]["activated"] = True
        self._write_database(db)
        return True, f"Account {key} activated"

    def deactivate_account(self, username):
        key = username.upper()
        db = self._read_database()
        if key not in db:
            return False, "Account not found"
        db[key]["activated"] = False
        self._write_database(db)
        return True, f"Account {key} deactivated"

    def change_details(self, username, **kwargs):
        key = username.upper()
        db = self._read_database()
        if key not in db:
            return False, "Account not found"
        for k, v in kwargs.items():
            if k in db[key]:
                db[key][k] = v
        self._write_database(db)
        return True, f"Account {key} updated"

    # Admin GUI
    def admin_gui(self):
        running = True
        while running:
            clear_terminal()
            print("#######################\n# ADMIN CONTROL PANEL #\n#######################")
            print("\n1. Create Account\n2. Delete Account\n3. Activate Account\n4. Deactivate Account" "\n5. Change Account Details\n0. Back\n")
            try:
                choice = int(input("> "))
            except ValueError:
                print("Enter a number")
                input("Press Enter to continue...")
                continue

            if choice == 1:
                username = input("Username: ").strip()
                password = input("Password: ")
                currency = input("Default currency (3-letter code, e.g. USD): ").strip().upper() or "USD"
                is_admin = input("Grant admin permissions? (y/n): ").strip().lower() == "y"
                success, msg = self.create_account(username, password, currency, is_admin)
                print(msg)
                input("Press Enter to continue...")

            elif choice == 2:
                username = input("Username to delete: ").strip()
                success, msg = self.delete_account(username)
                print(msg)
                input("Press Enter to continue...")

            elif choice == 3:
                username = input("Username to activate: ").strip()
                success, msg = self.activate_account(username)
                print(msg)
                input("Press Enter to continue...")

            elif choice == 4:
                username = input("Username to deactivate: ").strip()
                success, msg = self.deactivate_account(username)
                print(msg)
                input("Press Enter to continue...")

            elif choice == 5:
                username = input("Username to change: ").strip()
                field = input("Field to change (password, currency, balance, is_admin): ").strip()
                value = input("New value: ").strip()
                if field == "balance":
                    try:
                        value = float(value)
                    except ValueError:
                        print("Invalid balance")
                        input("Press Enter to continue...")
                        continue
                elif field == "is_admin":
                    value = value.lower() in ["true", "yes", "1", "y"]
                success, msg = self.change_details(username, **{field: value})
                print(msg)
                input("Press Enter to continue...")

            elif choice == 0:
                running = False

            else:
                print("Unknown option")
                input("Press Enter to continue...")


def main():
    ensure_user_db()
    ensure_database()
    features = Features(db_dir=DB_DIR)
    admin = Admin(DB_DIR)

    running = True
    while running:
        clear_terminal()
        print("#########################\n# SMART BANKING PROGRAM #\n#########################")

        with open(USER_DB, "r") as user_db:
            data = json.load(user_db)
            logged_in = data.get("logged in", False)
            account = data.get("account", "")

        if logged_in and account:
            db_data = json.load(open(DATABASE_DB))
            is_admin = db_data.get(account, {}).get("is_admin", False)

            choice = user_menu(is_admin)
            if choice == 1:
                features.view_balance(account)
            elif choice == 2:
                features.deposit(account)
            elif choice == 3:
                features.withdraw(account)
            elif choice == 4:
                features.change_currency(account)
            elif choice == 5:
                features.card_settings(account)
            elif choice == 6:
                features.logout()
            elif choice == 7 and is_admin:
                admin.admin_gui()
            elif choice == 0:
                print("Goodbye!")
                running = False
            else:
                print("Unknown option.")
                input("Press Enter to continue...")

        else:
            choice = logged_out_menu()
            if choice == 1:
                username = input("Username: ").strip()
                password = input("Password: ")
                if features.login(username, password):
                    print(f"Logged in as {username}")
                    input("Press Enter to continue...")
                else:
                    print("Login failed.")
                    input("Press Enter to continue...")

            elif choice == 2:
                username = input("Choose username: ").strip()
                password = input("Choose password: ")
                currency = input("Default currency (3-letter code, e.g. USD): ").strip().upper() or "USD"
                success, msg = admin.create_account(username, password, currency, is_admin=False)
                print(msg)
                input("Press Enter to continue...")

            elif choice == 0:
                print("Exiting...")
                running = False

            else:
                print("Unknown option.")
                input("Press Enter to continue...")


if __name__ == "__main__":
    main()
