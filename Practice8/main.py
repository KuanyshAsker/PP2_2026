from phonebook import *

def get_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Enter a valid number!")

def menu():
    print("\n📱 PhoneBook Menu")
    print("1. Add contact")
    print("2. View all contacts")
    print("3. Search by name")
    print("4. Search by phone prefix")
    print("5. Update contact")
    print("6. Delete (by name or phone)")
    print("7. Search by pattern (SQL function)")
    print("8. Insert or update (SQL procedure)")
    print("9. View with pagination")
    print("0. Exit")

def run():
    create_table()

    while True:
        menu()
        choice = input("Choose option: ")

        if choice == "1":
            insert_from_input()

        elif choice == "2":
            print("\n")
            get_contacts()

        elif choice == "3":
            name = input("Enter name: ")
            search_by_name(name)

        elif choice == "4":
            prefix = input("Enter phone prefix: ")
            search_by_prefix(prefix)

        elif choice == "5":
            name = input("Enter name: ")
            new_phone = input("Enter new phone: ")
            update_contact(name, new_phone)

        elif choice == "6":
            value = input("Enter name OR phone: ")
            delete_user(value)

        elif choice == "7":
            pattern = input("Enter pattern: ")
            search_pattern(pattern)

        elif choice == "8":
            name = input("Enter name: ")
            phone = input("Enter phone: ")
            insert_or_update_user(name, phone)

        elif choice == "9":
            limit = get_int("Limit: ")
            offset = get_int("Offset: ")

            conn = get_connection()
            cur = conn.cursor()

            cur.execute(
                "SELECT * FROM get_contacts_paginated(%s, %s);",
                (limit, offset)
            )

            rows = cur.fetchall()
            for row in rows:
                print(row)

            cur.close()
            conn.close()

        elif choice == "0":
            print("Goodbye 👋")
            break

        else:
            print("Invalid option!")

if __name__ == "__main__":
    run()