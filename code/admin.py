from pathlib import Path
import json
import os

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR.parent / "db"
DATABASE_DB = DB_DIR / "database.db"


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


class Admin:
    def __init__(self, db_dir: Path = None):
        self.BASE_DIR = Path(__file__).resolve().parent
        if db_dir is None:
            db_dir = self.BASE_DIR.parent / "db"
        self.db_dir = Path(db_dir)
        self.database_db = self.db_dir / "database.db"
        self.database_db.parent.mkdir(parents=True, exist_ok=True)
        if not self.database_db.exists():
            # default admin account
            default = {
                "ADMIN": {
                    "password": "admin000",
                    "currency": "USD",
                    "balance": 0,
                    "activated": True,
                    "is_admin": True,
                    "card": None,
                }
            }
            self._write_database(default)

    # --- Database helpers ---
    def _read_database(self):
        with open(self.database_db, "r") as f:
            return json.load(f)

    def _write_database(self, data):
        with open(self.database_db, "w") as f:
            json.dump(data, f, indent=4)

    # --- Admin actions ---
    def create_account(self, username, password, currency="USD"):
        key = username.upper()
        db = self._read_database()
        if key in db:
            return False, "Account already exists"
        db[key] = {
            "password": password,
            "currency": currency.upper(),
            "balance": 0,
            "activated": True,
            "card": None,
        }
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

    # --- Admin authentication ---
    def login_admin(self):
        db = self._read_database()
        print("=== ADMIN LOGIN ===")
        username = input("Admin username: ").strip().upper()
        password = input("Password: ").strip()
        if username in db and db[username]["password"] == password:
            print(f"Welcome, {username}!")
            input("Press Enter to continue...")
            return True
        print("Invalid username or password")
        input("Press Enter to exit...")
        return False


# --- GUI for Admin (only runs if this file is executed) ---
def admin_gui():
    admin = Admin(db_dir=DB_DIR)
    if not admin.login_admin():
        return  # exit if login fails

    running = True
    while running:
        clear_terminal()
        print("#######################\n# ADMIN CONTROL PANEL #\n#######################")
        print("\n1. Create Account\n2. Delete Account\n3. Activate Account\n4. Deactivate Account" "\n5. Change Account Details\n0. Exit\n")
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
            success, msg = admin.create_account(username, password, currency)
            print(msg)
            input("Press Enter to continue...")

        elif choice == 2:
            username = input("Username to delete: ").strip()
            success, msg = admin.delete_account(username)
            print(msg)
            input("Press Enter to continue...")

        elif choice == 3:
            username = input("Username to activate: ").strip()
            success, msg = admin.activate_account(username)
            print(msg)
            input("Press Enter to continue...")

        elif choice == 4:
            username = input("Username to deactivate: ").strip()
            success, msg = admin.deactivate_account(username)
            print(msg)
            input("Press Enter to continue...")

        elif choice == 5:
            username = input("Username to change: ").strip()
            field = input("Field to change (password, currency, balance): ").strip()
            value = input("New value: ").strip()
            if field == "balance":
                try:
                    value = float(value)
                except ValueError:
                    print("Invalid balance")
                    input("Press Enter to continue...")
                    continue
            success, msg = admin.change_details(username, **{field: value})
            print(msg)
            input("Press Enter to continue...")

        elif choice == 0:
            print("Exiting Admin Panel...")
            running = False

        else:
            print("Unknown option")
            input("Press Enter to continue...")


if __name__ == "__main__":
    admin_gui()
