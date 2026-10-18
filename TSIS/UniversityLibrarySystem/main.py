import random  # Chooses sample members for borrowing records.
import re  # Checks whether a member email has a valid format.
import sqlite3  # Connects the program to its SQLite database.

# These are the files used to store the database and exported report.
DATABASE = "project.db"
RESULTS = "results.txt"


# A Book object stores one book's details and can print them as a table row.
class Book:
    def __init__(self, book_id, title, author, genre, available):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.genre = genre
        self.available = available 

    def show(self):
        # Convert the database value (1 or 0) into a readable status.
        status = "Yes" if self.available == 1 else "No"
        # The numbers set column widths; < means left-aligned.
        print("{:<4} | {:<42} | {:<34} | {:<20} | {:<9}".format(
            self.book_id, self.title, self.author, self.genre, status
        ))

# A Member object stores one member's details and can print a table row.
class Member:
    def __init__(self, member_id, name, email, program):
        self.member_id = member_id
        self.name = name
        self.email = email
        self.program = program

    def show(self):
        # Print the member fields in aligned columns.
        print("{:<4} | {:<25} | {:<42} | {:<22}".format(
            self.member_id, self.name, self.email, self.program
        ))

# Create the three related database tables if they do not already exist.
def create_tables(connection):
    cursor = connection.cursor()
    # Books are stored here; book_id identifies each book.
    cursor.execute("CREATE TABLE IF NOT EXISTS books (book_id INTEGER PRIMARY KEY, title TEXT, author TEXT, genre TEXT, available INTEGER)")
    # Members are stored here; UNIQUE prevents duplicate email addresses.
    cursor.execute("CREATE TABLE IF NOT EXISTS members (member_id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, program TEXT)")
    # Each borrowing connects one book and one member by their IDs.
    cursor.execute("CREATE TABLE IF NOT EXISTS borrowings (borrowing_id INTEGER PRIMARY KEY, book_id INTEGER, member_id INTEGER, returned INTEGER, FOREIGN KEY(book_id) REFERENCES books(book_id), FOREIGN KEY(member_id) REFERENCES members(member_id))")
    # Save the table-creation commands.
    connection.commit()


# Add the starter dataset once, when the books table is empty.
def add_sample_data(connection):
    cursor = connection.cursor()
    # COUNT(*) returns the number of book records already saved.
    cursor.execute("SELECT COUNT(*) FROM books")
    # If books exist, skip the starter data so it is not added again.
    if cursor.fetchone()[0] > 0:
        return

    # Each tuple contains a book title, author, and genre.
    books = [
        ("Python Crash Course", "Eric Matthes", "Programming"),
        ("Automate the Boring Stuff with Python", "Al Sweigart", "Programming"),
        ("Think Python", "Allen B. Downey", "Programming"),
        ("Fluent Python", "Luciano Ramalho", "Programming"),
        ("Effective Python", "Brett Slatkin", "Programming"),
        ("Python for Data Analysis", "Wes McKinney", "Data Science"),
        ("Learning Python", "Mark Lutz", "Programming"),
        ("Head First Python", "Paul Barry", "Programming"),
        ("Python Tricks", "Dan Bader", "Programming"),
        ("Python Cookbook", "David Beazley and Brian K. Jones", "Programming"),
        ("Clean Code", "Robert C. Martin", "Programming"),
        ("The Pragmatic Programmer", "Andrew Hunt and David Thomas", "Programming"),
        ("Code Complete", "Steve McConnell", "Programming"),
        ("Design Patterns", "Erich Gamma and others", "Programming"),
        ("Introduction to Algorithms", "Thomas H. Cormen and others", "Computer Science"),
        ("Data Structures and Algorithms in Python", "Michael T. Goodrich and others", "Computer Science"),
        ("Database System Concepts", "Abraham Silberschatz and others", "Computer Science"),
        ("Computer Networking: A Top-Down Approach", "James Kurose and Keith Ross", "Computer Science"),
        ("The Linux Command Line", "William Shotts", "Computer Science"),
        ("The C Programming Language", "Brian Kernighan and Dennis Ritchie", "Programming"),
        ("The Hobbit", "J. R. R. Tolkien", "Fantasy"),
        ("Dune", "Frank Herbert", "Science Fiction"),
        ("1984", "George Orwell", "Classic Fiction"),
        ("Pride and Prejudice", "Jane Austen", "Classic Fiction"),
        ("The Great Gatsby", "F. Scott Fitzgerald", "Classic Fiction"),
        ("To Kill a Mockingbird", "Harper Lee", "Fiction"),
        ("The Little Prince", "Antoine de Saint-Exupery", "Fiction"),
        ("Crime and Punishment", "Fyodor Dostoevsky", "Classic Fiction"),
        ("The Alchemist", "Paulo Coelho", "Fiction"),
        ("Atomic Habits", "James Clear", "Personal Development"),
        ("Sapiens", "Yuval Noah Harari", "History"),
        ("Educated", "Tara Westover", "Memoir"),
        ("And Then There Were None", "Agatha Christie", "Mystery"),
        ("The Kite Runner", "Khaled Hosseini", "Fiction"),
        ("The Book Thief", "Markus Zusak", "Historical Fiction"),
        ("The Silent Patient", "Alex Michaelides", "Mystery"),
        ("The Midnight Library", "Matt Haig", "Fiction"),
        ("A Brief History of Time", "Stephen Hawking", "Science"),
        ("Cosmos", "Carl Sagan", "Science"),
        ("The Diary of a Young Girl", "Anne Frank", "Memoir"),
        ("Words of Edification", "Abai Qunanbaiuly", "Kazakh Literature"),
        ("The Path of Abai", "Mukhtar Auezov", "Kazakh Literature"),
        ("The Nomads", "Ilyas Esenberlin", "Kazakh Literature"),
        ("One Hundred Years of Solitude", "Gabriel Garcia Marquez", "Fiction"),
        ("The Old Man and the Sea", "Ernest Hemingway", "Fiction"),
        ("The Catcher in the Rye", "J. D. Salinger", "Fiction"),
        ("The Name of the Rose", "Umberto Eco", "Mystery"),
        ("A Thousand Splendid Suns", "Khaled Hosseini", "Fiction"),
        ("The Art of War", "Sun Tzu", "History"),
        ("Man's Search for Meaning", "Viktor E. Frankl", "Memoir"),
    ]
    # Sample members; their emails and study programs are generated below.
    names = [
        "Aibek Sarsenov", "Aida Nurgaliyeva", "Alikhan Tolegen", "Amina Zhaksylyk", "Aruzhan Kassen",
        "Asel Mukan", "Askar Bekturov", "Ayan Zhumabay", "Bakyt Ermek", "Danel Akhmet",
        "Diana Abilova", "Dias Kairat", "Dinara Saparova", "Eldar Bek", "Elmira Kazybek",
        "Erasyl Tursyn", "Farida Omarova", "Gulmira Ibrayeva", "Ilyas Sadyk", "Inkar Alimova",
        "Islam Nurtay", "Kamila Balgabek", "Karina Dulat", "Madina Serik", "Miras Akhan",
        "Nurlan Aitbay", "Raushan Kenzhe", "Rustem Bayazit", "Samal Altynbek", "Sanjar Malikov",
        "Sholpan Kadir", "Sultan Zhanibek", "Tamara Ospan", "Timur Kairbek", "Tomiris Mukan",
        "Ulan Nurtay", "Yerlan Akhmet", "Zhanar Mukhtar", "Zhanibek Saken", "Zhibek Aman",
    ]
    # Study programs are assigned to members in repeating order.
    programs = ["Computer Science", "Mathematics", "Engineering", "Economics", "Languages"]

    # Add each sample book. The final 1 means it starts as available.
    for title, author, genre in books:
        cursor.execute("INSERT INTO books (title, author, genre, available) VALUES (?, ?, ?, 1)", (title, author, genre))

    # Create a member email and assign a program for every sample name.
    for i in range(len(names)):
        email = names[i].lower().replace(" ", ".") + "@kbtu.kz"
        program = programs[i % len(programs)]
        cursor.execute("INSERT INTO members (name, email, program) VALUES (?, ?, ?)", (names[i], email, program))

    # Number of loans for books 1–12; these values add up to 30.
    loan_counts = [8, 5, 4, 3, 2, 2] + [1] * 6
    for book_number in range(len(loan_counts)):
        # List positions start at zero, but database book IDs start at one.
        book_id = book_number + 1
        # Create the number of borrowing records listed for this book.
        for copy_number in range(loan_counts[book_number]):
            # Pick a sample member ID at random.
            member_id = random.randint(1, len(names))
            # Start by treating the sample loan as returned.
            returned = 1
            # Make the last loan for each book an active (not returned) loan.
            if book_number < 12 and copy_number == loan_counts[book_number] - 1:
                returned = 0
                # A book with an active loan is marked unavailable.
                cursor.execute("UPDATE books SET available=0 WHERE book_id=?", (book_id,))
            # Save this borrowing with its book, member, and return status.
            cursor.execute("INSERT INTO borrowings (book_id, member_id, returned) VALUES (?, ?, ?)", (book_id, member_id, returned))
    # Save all sample records and availability changes.
    connection.commit()


# Ask for book details, check that none are blank, and save the book.
def add_book(connection):
    title = input("Book title: ")
    author = input("Author: ")
    genre = input("Genre: ")
    if title == "" or author == "" or genre == "":
        print("Please fill in all book details.")
        return
    # ? placeholders keep user input separate from the SQL command.
    connection.execute("INSERT INTO books (title, author, genre, available) VALUES (?, ?, ?, 1)", (title, author, genre))
    connection.commit()
    print("Book added.")


# Ask for member details, validate the email, then save the member.
def add_member(connection):
    name = input("Member name: ")
    email = input("Member email: ")
    program = input("Study program: ")
    # Reject missing details or an email that does not match the pattern.
    if name == "" or program == "" or re.match(r"^[\w.-]+@[\w.-]+\.\w+$", email) is None:
        print("Enter a name, study program, and valid email.")
        return
    # Check whether this email has already been registered.
    existing = connection.execute("SELECT member_id FROM members WHERE email=?", (email,)).fetchone()
    if existing is not None:
        print("That email is already registered.")
        return
    connection.execute("INSERT INTO members (name, email, program) VALUES (?, ?, ?)", (name, email, program))
    connection.commit()
    print("Member added.")


# Format and print book rows; show a message if the search found none.
def show_book_table(rows):
    if len(rows) == 0:
        print("No books found.")
        return
    print("{:<4} | {:<42} | {:<34} | {:<20} | {:<9}".format(
        "ID", "TITLE", "AUTHOR", "GENRE", "AVAILABLE"
    ))
    print("-" * 122)
    for row in rows:
        # Make a Book object from this database row, then print it.
        book = Book(row[0], row[1], row[2], row[3], row[4])
        book.show()


# Format and print member rows; show a message if there are no matches.
def show_member_table(rows):
    if len(rows) == 0:
        print("No members found.")
        return
    print("{:<4} | {:<25} | {:<42} | {:<22}".format(
        "ID", "NAME", "EMAIL", "PROGRAM"
    ))
    print("-" * 105)
    for row in rows:
        # Make a Member object from this row, then print it.
        member = Member(row[0], row[1], row[2], row[3])
        member.show()


# Read all books from SQLite and pass them to the book-table formatter.
def display_books(connection):
    print("\nBOOKS")
    rows = connection.execute("SELECT book_id, title, author, genre, available FROM books").fetchall()
    show_book_table(rows)


# Read all members from SQLite and pass them to the member-table formatter.
def display_members(connection):
    print("\nMEMBERS")
    rows = connection.execute("SELECT member_id, name, email, program FROM members").fetchall()
    show_member_table(rows)


# Read and print borrowing records with a readable Returned/Borrowed status.
def display_borrowings(connection):
    print("\nBORROWINGS")
    print("{:<4} | {:<9} | {:<10} | {:<10}".format(
        "ID", "BOOK ID", "MEMBER ID", "STATUS"
    ))
    print("-" * 43)
    rows = connection.execute("SELECT borrowing_id, book_id, member_id, returned FROM borrowings").fetchall()
    for row in rows:
        # The database uses 1 for returned and 0 for still borrowed.
        status = "Returned" if row[3] == 1 else "Borrowed"
        print("{:<4} | {:<9} | {:<10} | {:<10}".format(row[0], row[1], row[2], status))
    if len(rows) == 0:
        print("No borrowing records found.")


# Let the user choose whether to display books, members, or borrowings.
def display_records(connection):
    print("1. Books")
    print("2. Members")
    print("3. Borrowings")
    choice = input("Choose records to display: ")
    if choice == "1":
        display_books(connection)
    elif choice == "2":
        display_members(connection)
    elif choice == "3":
        display_borrowings(connection)
    else:
        print("Invalid choice.")


# Search books by title, or members by name or ID.
def search_records(connection):
    print("1. Search book by title")
    print("2. Search member by name or ID")
    choice = input("Choose search: ")
    if choice == "1":
        title = input("Enter part of the title: ")
        # % before and after the text allow a partial title match.
        rows = connection.execute("SELECT book_id, title, author, genre, available FROM books WHERE title LIKE ?", ("%" + title + "%",)).fetchall()
        print("\nSEARCH RESULTS: BOOKS")
        show_book_table(rows)
    elif choice == "2":
        name = input("Enter a name or member ID: ")
        # Match part of a name or match the member ID exactly.
        rows = connection.execute("SELECT member_id, name, email, program FROM members WHERE name LIKE ? OR member_id=?", ("%" + name + "%", name)).fetchall()
        print("\nSEARCH RESULTS: MEMBERS")
        show_member_table(rows)
    else:
        print("Invalid choice.")


# Check a book and member, create a loan, and mark the book unavailable.
def borrow_book(connection):
    book_id = input("Book ID: ")
    member_id = input("Member ID: ")
    # IDs must contain digits before they can be used in database lookups.
    if not book_id.isdigit() or not member_id.isdigit():
        print("Please enter numbers for the IDs.")
        return
    # Look up the book's availability and confirm the member exists.
    book = connection.execute("SELECT available FROM books WHERE book_id=?", (book_id,)).fetchone()
    member = connection.execute("SELECT member_id FROM members WHERE member_id=?", (member_id,)).fetchone()
    if book is None or member is None:
        print("Book or member not found.")
    elif book[0] == 0:
        print("That book is already borrowed.")
    else:
        # returned=0 means the book is currently borrowed.
        connection.execute("INSERT INTO borrowings (book_id, member_id, returned) VALUES (?, ?, 0)", (book_id, member_id))
        # Keep the book's availability consistent with the new loan.
        connection.execute("UPDATE books SET available=0 WHERE book_id=?", (book_id,))
        connection.commit()
        print("Borrowing saved.")


# Mark an active borrowing as returned and make its book available again.
def return_book(connection):
    borrowing_id = input("Borrowing ID to return: ")
    if not borrowing_id.isdigit():
        print("Please enter a number.")
        return
    # Find which book is connected to this borrowing and its current status.
    row = connection.execute("SELECT book_id, returned FROM borrowings WHERE borrowing_id=?", (borrowing_id,)).fetchone()
    if row is None:
        print("Borrowing not found.")
    elif row[1] == 1:
        print("This book was already returned.")
    else:
        # returned=1 means the borrowing is finished.
        connection.execute("UPDATE borrowings SET returned=1 WHERE borrowing_id=?", (borrowing_id,))
        # The returned book can now be borrowed again.
        connection.execute("UPDATE books SET available=1 WHERE book_id=?", (row[0],))
        connection.commit()
        print("Book returned.")


# Change the title and author of an existing book.
def update_book(connection):
    book_id = input("Book ID to update: ")
    title = input("New title: ")
    author = input("New author: ")
    if not book_id.isdigit() or title == "" or author == "":
        print("Enter a number and fill in the title and author.")
        return
    # Update the matching ID; rowcount below tells us whether it was found.
    cursor = connection.execute("UPDATE books SET title=?, author=? WHERE book_id=?", (title, author, book_id))
    connection.commit()
    if cursor.rowcount == 0:
        print("Book not found.")
    else:
        print("Book updated.")


# Cancel a borrowing; an active loan makes its book available again.
def delete_record(connection):
    borrowing_id = input("Borrowing ID to cancel: ")
    if not borrowing_id.isdigit():
        print("Please enter a number.")
        return
    # Read the status before deleting so we know whether to free the book.
    row = connection.execute("SELECT book_id, returned FROM borrowings WHERE borrowing_id=?", (borrowing_id,)).fetchone()
    if row is None:
        print("Borrowing not found.")
    else:
        # Remove this borrowing record from the database.
        connection.execute("DELETE FROM borrowings WHERE borrowing_id=?", (borrowing_id,))
        if row[1] == 0:
            connection.execute("UPDATE books SET available=1 WHERE book_id=?", (row[0],))
        connection.commit()
        print("Borrowing cancelled.")


def show_statistics(connection):
    # Count all borrowing records.
    total = connection.execute("SELECT COUNT(*) FROM borrowings").fetchone()[0]
    # Count loans where returned=0, meaning the books are still out.
    current = connection.execute("SELECT COUNT(*) FROM borrowings WHERE returned=0").fetchone()[0]
    # Count loans per book, sort largest first, and take the top result.
    top_book = connection.execute("SELECT book_id, COUNT(*) FROM borrowings GROUP BY book_id ORDER BY COUNT(*) DESC LIMIT 1").fetchone()
    print("Total borrowing records:", total)
    print("Books currently borrowed:", current)
    if top_book is not None:
        # Look up the title so the result shows a name instead of only an ID.
        title = connection.execute("SELECT title FROM books WHERE book_id=?", (top_book[0],)).fetchone()
        print("Most frequently borrowed book:", title[0], "-", top_book[1], "loans")


def export_results(connection):
    # Write mode creates the file or replaces its previous contents.
    with open(RESULTS, "w") as file:
        # Get current totals from the database for the exported summary.
        total = connection.execute("SELECT COUNT(*) FROM borrowings").fetchone()[0]
        current = connection.execute("SELECT COUNT(*) FROM borrowings WHERE returned=0").fetchone()[0]
        top_book = connection.execute("SELECT book_id, COUNT(*) FROM borrowings GROUP BY book_id ORDER BY COUNT(*) DESC LIMIT 1").fetchone()
        file.write("UNIVERSITY LIBRARY SUMMARY\n")
        file.write("{:<30}: {}\n".format("Books", connection.execute("SELECT COUNT(*) FROM books").fetchone()[0]))
        file.write("{:<30}: {}\n".format("Members", connection.execute("SELECT COUNT(*) FROM members").fetchone()[0]))
        file.write("{:<30}: {}\n".format("Borrowing records", total))
        file.write("{:<30}: {}\n".format("Books currently borrowed", current))
        if top_book is not None:
            # Convert the top book's ID into its title for the report.
            title = connection.execute("SELECT title FROM books WHERE book_id=?", (top_book[0],)).fetchone()
            file.write("{:<30}: {} ({} loans)\n".format("Most frequently borrowed book", title[0], top_book[1]))
        file.write("\nBORROWING RECORDS\n")
        file.write("{:<4} | {:<7} | {:<9} | {}\n".format("ID", "BOOK ID", "MEMBER ID", "RETURNED"))
        file.write("-----+---------+-----------+---------\n")
        rows = connection.execute("SELECT borrowing_id, book_id, member_id, returned FROM borrowings")
        # Write one formatted line for each borrowing record.
        for row in rows:
            file.write("{:<4} | {:<7} | {:<9} | {}\n".format(row[0], row[1], row[2], row[3]))
    print("Results saved to results.txt.")


# Print all actions the user can choose from.
def show_menu():
    print("""
UNIVERSITY LIBRARY SYSTEM
1. Add a book
2. Add a member
3. Borrow a book
4. Display records
5. Search books or members
6. Update a book
7. Cancel a borrowing
8. Return a book
9. Show statistics
10. Export results.txt
0. Exit
""")


def main():
    # Open the database file; SQLite creates it if it is not there yet.
    connection = sqlite3.connect(DATABASE)
    # Turn on checks for the book and member links in the borrowing table.
    connection.execute("PRAGMA foreign_keys = ON")
    create_tables(connection)
    add_sample_data(connection)
    print("Library ready: 50 books, 40 members, and 30 borrowing records.")
    # Keep showing the menu until the user selects 0 to exit.
    while True:
        show_menu()
        choice = input("Choose an option: ")
        if choice == "1":
            add_book(connection)
        elif choice == "2":
            add_member(connection)
        elif choice == "3":
            borrow_book(connection)
        elif choice == "4":
            display_records(connection)
        elif choice == "5":
            search_records(connection)
        elif choice == "6":
            update_book(connection)
        elif choice == "7":
            delete_record(connection)
        elif choice == "8":
            return_book(connection)
        elif choice == "9":
            show_statistics(connection)
        elif choice == "10":
            export_results(connection)
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Choose a number from the menu.")
    # Close the database connection after leaving the menu loop.
    connection.close()


# Start the interactive program when this file is run.
main()
