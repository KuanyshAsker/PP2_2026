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
    print("9. View with pagination navigation")
    print("10. Filter by group")
    print("11. Search by email")
    print("12. Sort contacts")
    print("13. Export contacts to JSON")
    print("14. Import contacts from JSON")
    print("15. Import contacts from CSV")
    print("16. Add phone to contact")
    print("17. Move contact to group")
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
            page_size = get_int("Page size: ")

            if page_size <= 0:
                print("Page size must be greater than 0.")
                continue

            page = 0

            while True:
                offset = page * page_size
                rows = get_contacts_page(page_size, offset)

                print(f"\n--- Page {page + 1} ---")
                print_contacts_table(rows)

                command = input("next / prev / quit: ").strip().lower()

                if command in ("next", "n"):
                    if len(rows) < page_size:
                        print("You are already on the last page.")
                    else:
                        page += 1

                elif command in ("prev", "p"):
                    if page == 0:
                        print("You are already on the first page.")
                    else:
                        page -= 1

                elif command in ("quit", "q"):
                    break

                else:
                    print("Use next, prev, or quit.")

        elif choice == "10":
            groups = get_groups()
            print("Available groups:", ", ".join(groups))

            group_name = input("Enter group name: ")
            filter_by_group(group_name)

        elif choice == "11":
            email_pattern = input("Enter email search text: ")
            search_by_email(email_pattern)

        elif choice == "12":
            print("Sort by:")
            print("1. name")
            print("2. birthday")
            print("3. date added")

            sort_choice = input("Choose sort option: ")

            if sort_choice == "1":
                sort_contacts("name")
            elif sort_choice == "2":
                sort_contacts("birthday")
            elif sort_choice == "3":
                sort_contacts("date_added")
            else:
                print("Invalid sort option!")

        elif choice == "13":
            filename = input("Enter JSON filename to export to: ")

            if not filename.endswith(".json"):
                filename += ".json"

            export_to_json(filename)

        elif choice == "14":
            filename = input("Enter JSON filename to import from: ")
            import_from_json(filename)

        elif choice == "15":
            filename = input("Enter CSV filename to import from: ")
            insert_from_csv(filename)

        elif choice == "16":
            contact_name = input("Enter contact name: ")
            phone = input("Enter new phone: ")
            phone_type = input("Enter phone type (home/work/mobile): ")

            add_phone_to_contact(contact_name, phone, phone_type)

        elif choice == "17":
            contact_name = input("Enter contact name: ")
            group_name = input("Enter new group name: ")

            move_contact_to_group(contact_name, group_name)

        elif choice == "0":
            print("Goodbye 👋")
            break

        else:
            print("Invalid option!")

if __name__ == "__main__":
    run()