import json
import features


def user_menu():
    print("\n1. View Balance\n2. Deposit Money\n3. Withdraw Money\n4. Change Currency\n5. Card Settings\n6. Log Out\n0. Exit\n")
    ipt = input("> ")
    try:
        ipt = int(ipt)
    except ValueError:
        print("Please enter a valid number.")
        return 0
    return ipt


def logged_out_menu():
    print("\n1. Log In\n2. Create Account\n0. Exit\n")
    ipt = input("> ")
    try:
        ipt = int(ipt)
    except ValueError:
        print("Please enter a valid number.")
        return user_menu()
    return ipt


def main():
    running = True
    while running:
        print("#########################\n" + "# SMART BANKING PROGRAM #" + "\n#########################")

        with open("./db/user.db", "r") as user_db:
            data = json.load(user_db)
            logged_in = data["logged in"]
            account = data["account"]

        if logged_in:
            choice = user_menu()

            match choice:
                case 1:
                    features.view_balance(account)
        else:
            choice = logged_out_menu()


if __name__ == "__main__":
    main()
