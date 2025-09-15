import mysql.connector
from datetime import datetime

#  Database Connection 
def get_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="your password",
            database="database name",
            port='3308'
        )
    except mysql.connector.Error as e:
        print("Database connection failed:", e)
        return None

# Credit/Debit Functionality 
class CreditDebit:
    def __init__(self, amount, acc_no):
        self.amount = amount
        self.acc_no = acc_no

    def credit(self):
        conn = get_connection()
        if not conn:
            return "Database error!"
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET balance = balance + %s WHERE account_no = %s",
                (self.amount, self.acc_no)
            )
            conn.commit()

            cursor.execute("SELECT balance FROM users WHERE account_no = %s", (self.acc_no,))
            bal = cursor.fetchone()

            cursor.execute(
                "INSERT INTO transactions(account_no, action, amount, closing_balance) "
                "VALUES(%s, %s, %s, %s)",
                (self.acc_no, 'credit', self.amount, bal[0])
            )
            conn.commit()
            return "Amount added successfully :)"
        except Exception as e:
            return f"Error: {e}"
        finally:
            cursor.close()
            conn.close()

    def debit(self):
        conn = get_connection()
        if not conn:
            return "Database error!"
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM users WHERE account_no = %s", (self.acc_no,))
            balance = cursor.fetchone()

            if self.amount <= balance[0]:
                cursor.execute(
                    "UPDATE users SET balance = balance - %s WHERE account_no = %s",
                    (self.amount, self.acc_no)
                )
                conn.commit()

                cursor.execute("SELECT balance FROM users WHERE account_no = %s", (self.acc_no,))
                bal = cursor.fetchone()

                cursor.execute(
                    "INSERT INTO transactions(account_no, action, amount, closing_balance) "
                    "VALUES(%s, %s, %s, %s)",
                    (self.acc_no, 'debit', self.amount, bal[0])
                )
                conn.commit()
                return "Amount withdrawn successfully :)"
            else:
                return "Insufficient balance! Try again."
        except Exception as e:
            return f"Error: {e}"
        finally:
            cursor.close()
            conn.close()

#  Main Menu 
def main_menu():
    while True:
        print("-" * 105)
        print("1. User login")
        print("2. Admin login")
        choice = input("Enter option: ")

        if choice == '1':
            user_login_signup()
        elif choice == '2':
            admin_menu()
        else:
            print("Invalid option! Try again.")

#  User Menu 
def user_menu(acc_no):
    while True:
        print("-" * 105)
        print("1. View account details")
        print("2. Debit amount")
        print("3. Credit amount")
        print("4. Pin change")
        print("5. Statement")
        print("6. Logout")
        choice = input("Enter option: ")

        conn = get_connection()
        if not conn:
            print("Database error!")
            return
        cursor = conn.cursor()

        if choice == '1':
            cursor.execute("SELECT * FROM users WHERE account_no = %s", (acc_no,))
            account_details = cursor.fetchone()
            fields = ['Account number:', 'Full name:', 'Account type:', 'PIN:', 'Bank balance:']
            print("-" * 105)
            for i, field in enumerate(fields):
                print(field, account_details[i])

        elif choice == '2':
            amt = int(input("Enter amount to withdraw: "))
            if amt % 100 == 0:
                print("-" * 105)
                print(CreditDebit(amt, acc_no).debit())
            else:
                print("Please enter an amount in multiples of 100.")

        elif choice == '3':
            amt = int(input("Enter amount to deposit: "))
            if amt >= 500:
                print("-" * 105)
                print(CreditDebit(amt, acc_no).credit())
            else:
                print("Minimum deposit amount is 500!")

        elif choice == '4':
            old_pin = input("Enter your old PIN: ")
            cursor.execute("SELECT pin FROM users WHERE account_no = %s", (acc_no,))
            stored_pin = cursor.fetchone()
            if old_pin == stored_pin[0]:
                new_pin = input("Enter new PIN: ")
                cursor.execute("UPDATE users SET pin = %s WHERE account_no = %s",
                               (new_pin, acc_no))
                conn.commit()
                print("PIN changed successfully.")
            else:
                print("Wrong old PIN! Try again.")

        elif choice == '5':
            start_date = input("Enter start date (yyyy-mm-dd): ")
            end_date = input("Enter end date (yyyy-mm-dd): ")
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                datetime.strptime(end_date, "%Y-%m-%d")
                cursor.execute(
                    "SELECT * FROM transactions WHERE account_no = %s AND txn_date BETWEEN %s AND %s",
                    (acc_no, start_date, end_date)
                )
                txns = cursor.fetchall()
                print("Transaction ID".ljust(21), "Type".ljust(21), "Amount".ljust(21),
                      "Date".ljust(21), "Closing Balance".ljust(21))
                print("-" * 105)
                for txn in txns:
                    for i, val in enumerate(txn):
                        if i != 1:
                            print(str(val).ljust(22), end="")
                    print()
            except ValueError:
                print("Invalid date format!")

        elif choice == '6':
            cursor.close()
            conn.close()
            break

        else:
            print("Invalid option! Try again.")

        cursor.close()
        conn.close()

#  User Login/Signup
def user_login_signup():
    while True:
        print("-" * 105)
        print("1. Login")
        print("2. Signup")
        print("3. Back to main menu")
        choice = input("Enter option: ")

        conn = get_connection()
        if not conn:
            print("Database error!")
            return
        cursor = conn.cursor()

        if choice == '1':
            acc_no = input("Enter your account number: ")
            pin = input("Enter your PIN: ")
            cursor.execute("SELECT * FROM users WHERE account_no = %s AND pin = %s",
                           (acc_no, pin))
            user = cursor.fetchone()
            if user:
                print("✅ Login successful! Welcome,", user[1])
                user_menu(acc_no)
            else:
                print("❌ Invalid account number or PIN.")

        elif choice == '2':
            name = input("Enter your name: ")
            acc_type = input("Account type (savings/current): ")
            pin = input("Set your PIN: ")
            cursor.execute(
                "INSERT INTO users(name, account_type, pin) VALUES(%s, %s, %s)",
                (name, acc_type, pin)
            )
            conn.commit()
            new_account_no = cursor.lastrowid
            print("✅ Account created successfully!")
            print(f"Your account number is: {new_account_no}")
            print("Please login with the created account.")

        elif choice == '3':
            cursor.close()
            conn.close()
            break

        else:
            print("Invalid option! Try again.")

        cursor.close()
        conn.close()

# Admin Menu 
def admin_menu():
    while True:
        admin_id = input("Enter admin ID (or 'back' to main menu): ")
        if admin_id.lower() == 'back':
            break
        conn = get_connection()
        if not conn:
            print("Database error!")
            return
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE admin_id = %s", (admin_id,))
        admin_details = cursor.fetchone()
        if admin_details:
            password = input("Enter your password: ")
            if password == admin_details[1]:
                print("✅ Admin login successful!")
                while True:
                    print("-" * 105)
                    print("1. View all users")
                    print("2. View specific user details")
                    print("3. View user transactions")
                    print("4. View transactions by date")
                    print("5. Logout")
                    choice = input("Choose one option: ")

                    if choice == '1':
                        cursor.execute("SELECT * FROM users")
                        users = cursor.fetchall()
                        print("Account No".ljust(21), "Name".ljust(21), "Type".ljust(21),
                              "PIN".ljust(21), "Balance".ljust(21))
                        print("-" * 105)
                        for rec in users:
                            for val in rec:
                                print(str(val).ljust(22), end="")
                            print()

                    elif choice == '2':
                        user_acc = input("Enter user account number: ")
                        cursor.execute("SELECT * FROM users WHERE account_no = %s", (user_acc,))
                        user = cursor.fetchone()
                        if user:
                            print("-" * 105)
                            print("Account No".ljust(21), "Name".ljust(21), "Type".ljust(21),
                                  "PIN".ljust(21), "Balance".ljust(21))
                            print("-" * 105)
                            for val in user:
                                print(str(val).ljust(22), end="")
                            print()
                        else:
                            print("User not found.")

                    elif choice == '3':
                        user_acc = input("Enter user account number: ")
                        cursor.execute("SELECT * FROM transactions WHERE account_no = %s", (user_acc,))
                        txns = cursor.fetchall()
                        print("Txn ID".ljust(21), "Action".ljust(21), "Amount".ljust(21),
                              "Date".ljust(21), "Closing Balance".ljust(21))
                        print("-" * 105)
                        for txn in txns:
                            for i, val in enumerate(txn):
                                if i != 1:
                                    print(str(val).ljust(22), end="")
                            print()

                    elif choice == '4':
                        input_date = input("Enter date (yyyy-mm-dd): ")
                        try:
                            datetime.strptime(input_date, "%Y-%m-%d")
                            cursor.execute(
                                "SELECT * FROM transactions WHERE DATE(txn_date) = %s",
                                (input_date,)
                            )
                            txns = cursor.fetchall()
                            print("Txn ID".ljust(21), "Account".ljust(21), "Action".ljust(21),
                                  "Amount".ljust(21), "Closing Balance".ljust(21))
                            print("-" * 105)
                            for txn in txns:
                                for i, val in enumerate(txn):
                                    if i != 4:
                                        print(str(val).ljust(22), end="")
                                print()
                        except ValueError:
                            print("Invalid date format!")

                    elif choice == '5':
                        main_menu()
                    else:
                        print("Invalid option! Try again.")
            else:
                print("❌ Wrong password!")
        else:
            print("❌ Admin ID not found!")

        cursor.close()
        conn.close()

# Entry Point
if __name__ == "__main__":
    main_menu()
