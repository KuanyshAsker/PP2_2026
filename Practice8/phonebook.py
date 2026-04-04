from connect import get_connection
import csv 

def create_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id SERIAL PRIMARY KEY,
        name TEXT,
        phone TEXT
    );
    """)
    #serial refers to auto incremention which starts from 1 
    #I mean primary key should be unique, no?
    conn.commit()
    cur.close()
    conn.close()

def insert_contact(name, phone):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO contacts (name, phone) VALUES (%s, %s);",
        (name, phone)
    ) #%s is just a placeholder for next variables like (name, phone) on upper sql code 

    conn.commit() #changes permanently btw 
    cur.close()
    conn.close()

def get_contacts():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM contacts;")
    rows = cur.fetchall() #fetchall refers to running the sql code 

    for row in rows:
        print(row)

    cur.close()
    conn.close()

def insert_from_csv(filename):

    conn = get_connection()
    cur = conn.cursor() #cursor for controlling the objects like values

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # skip header which is name, phone on csv file

        for row in reader:
            cur.execute(
                "INSERT INTO contacts (name, phone) VALUES (%s, %s);",
                (row[0], row[1])
            )

    conn.commit()
    cur.close()
    conn.close()

def insert_from_input():
    name = input("Enter name: ")
    phone = input("Enter phone: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO contacts (name, phone) VALUES (%s, %s);",
        (name, phone)
    )

    conn.commit()
    cur.close()
    conn.close()

def update_contact(name, new_phone):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE contacts SET phone = %s WHERE name = %s;",
        (new_phone, name)
    )

    conn.commit()
    cur.close()
    conn.close()

    print("Contact updated!")

def search_by_name(name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM contacts WHERE name = %s;",
        (name,)
    )

    results = cur.fetchall()
    for row in results:
        print(row)

    cur.close()
    conn.close()

def search_by_prefix(prefix):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM contacts WHERE phone LIKE %s;", #pattern matching operator 
        (prefix + "%",) # so since prefix goes first then it searches for matching phone which starts from prefix 
    )

    results = cur.fetchall()
    for row in results:
        print(row)

    cur.close()
    conn.close()

def delete_contact(name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM contacts WHERE name = %s;",
        (name,)
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Contact deleted!")

def delete_by_phone(phone):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM contacts WHERE phone = %s;",
        (phone,)
    )

    conn.commit()
    cur.close()
    conn.close()

    print("Contact deleted by phone!")

def search_pattern(pattern):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_contacts(%s);", (pattern,))
    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()

def insert_or_update_user(name, phone):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL insert_or_update_user(%s, %s);", (name, phone))

    conn.commit()
    cur.close()
    conn.close()

    print("User inserted or updated!")

def delete_user(value):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL delete_user(%s);", (value,))

    conn.commit()
    cur.close()
    conn.close()

    print("Deleted!")
   


