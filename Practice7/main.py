from phonebook import *

create_table()

while True:
    print("\n--- PhoneBook Menu ---")
    print("1. Add contact")
    print("2. View contacts")
    print("3. Search by name")
    print("4. Search by phone prefix")
    print("5. Update contact")
    print("6. Delete by name")
    print("7. Delete by phone")
    print("8. Exit")

    choice = input("Choose option: ")

    if choice == "1":
        insert_from_input()

    elif choice == "2":
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
        name = input("Enter name: ")
        delete_contact(name)

    elif choice == "7":
        phone = input("Enter phone: ")
        delete_by_phone(phone)

    elif choice == "8":
        break

    else:
        print("Invalid option")