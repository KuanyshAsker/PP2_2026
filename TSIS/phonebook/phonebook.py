from connect import get_connection
from pathlib import Path
import csv
import json

def create_table():
    conn = get_connection()
    cur = conn.cursor()

    schema_path = Path(__file__).with_name("schema.sql")

    with open(schema_path, "r", encoding="utf-8") as file:
        cur.execute(file.read())

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

def insert_from_csv(filename):
    conn = get_connection()
    cur = conn.cursor()

    try:
        with open(filename, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            imported_count = 0

            for row in reader:
                name = row.get("name", "").strip()
                main_phone = row.get("phone", "").strip()
                email = row.get("email", "").strip() or None
                birthday = row.get("birthday", "").strip() or None
                group_name = row.get("group", "Other").strip() or "Other"

                home_phone = row.get("home_phone", "").strip()
                work_phone = row.get("work_phone", "").strip()

                # Optional support if a CSV uses phone_type column
                main_phone_type = row.get("phone_type", "mobile").strip() or "mobile"

                if not name:
                    print(f"Skipped invalid row: {row}")
                    continue

                group_id = get_or_create_group(cur, group_name)

                cur.execute(
                    """
                    INSERT INTO contacts (name, phone, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (name, main_phone, email, birthday, group_id)
                )

                contact_id = cur.fetchone()[0]

                insert_phone(cur, contact_id, main_phone, main_phone_type)
                insert_phone(cur, contact_id, home_phone, "home")
                insert_phone(cur, contact_id, work_phone, "work")

                imported_count += 1

        conn.commit()
        print(f"CSV imported successfully! Imported contacts: {imported_count}")

    except Exception as e:
        conn.rollback()
        print("CSV import failed:", e)

    finally:
        cur.close()
        conn.close()

def get_or_create_group(cur, group_name):
    if not group_name:
        group_name = "Other"

    cur.execute(
        """
        INSERT INTO groups (name)
        VALUES (%s)
        ON CONFLICT (name) DO NOTHING;
        """,
        (group_name,)
    )

    cur.execute(
        "SELECT id FROM groups WHERE name = %s;",
        (group_name,)
    )

    return cur.fetchone()[0]

def insert_phone(cur, contact_id, phone, phone_type):
    if not phone:
        return

    allowed_types = ["home", "work", "mobile"]

    if phone_type not in allowed_types:
        phone_type = "mobile"

    cur.execute(
        """
        INSERT INTO phones (contact_id, phone, type)
        VALUES (%s, %s, %s)
        ON CONFLICT (contact_id, phone, type) DO NOTHING;
        """,
        (contact_id, phone, phone_type)
    )

def print_contacts_table(rows):
    if not rows:
        print("No contacts found.")
        return

    headers = ["ID", "Name", "Email", "Birthday", "Group", "Phones"]

    table = [
        [
            str(row[0]),
            str(row[1]),
            str(row[2]),
            str(row[3]),
            str(row[4]),
            str(row[5])
        ]
        for row in rows
    ]

    col_widths = []
    for i in range(len(headers)):
        max_width = max(len(headers[i]), max(len(row[i]) for row in table))
        col_widths.append(max_width)

    def print_separator():
        print("+" + "+".join("-" * (width + 2) for width in col_widths) + "+")

    def print_row(row):
        print(
            "| "
            + " | ".join(row[i].ljust(col_widths[i]) for i in range(len(row)))
            + " |"
        )

    print_separator()
    print_row(headers)
    print_separator()

    for row in table:
        print_row(row)

    print_separator()

def fetch_contacts(group_name=None, email_pattern=None, sort_by="id", limit=None, offset=None):
    conn = get_connection()
    cur = conn.cursor()

    sort_options = {
        "id": "c.id ASC",
        "name": "LOWER(c.name) ASC",
        "birthday": "c.birthday ASC NULLS LAST",
        "date": "c.created_at DESC NULLS LAST",
        "date_added": "c.created_at DESC NULLS LAST",
        "created_at": "c.created_at DESC NULLS LAST"
    }

    sort_key = sort_by.strip().lower().replace(" ", "_")
    order_sql = sort_options.get(sort_key, "c.id ASC")

    where_parts = []
    params = []

    if group_name:
        where_parts.append("LOWER(g.name) = LOWER(%s)")
        params.append(group_name)

    if email_pattern:
        where_parts.append("c.email ILIKE %s")
        params.append(f"%{email_pattern}%")

    where_sql = ""
    if where_parts:
        where_sql = "WHERE " + " AND ".join(where_parts)

    limit_sql = ""
    if limit is not None:
        limit_sql += " LIMIT %s"
        params.append(limit)

    if offset is not None:
        limit_sql += " OFFSET %s"
        params.append(offset)

    query = f"""
        SELECT
            c.id,
            c.name,
            COALESCE(c.email, '-') AS email,
            COALESCE(c.birthday::TEXT, '-') AS birthday,
            COALESCE(g.name, '-') AS group_name,
            COALESCE(
                string_agg(
                    p.type || ': ' || p.phone,
                    ', '
                    ORDER BY
                        CASE p.type
                            WHEN 'mobile' THEN 1
                            WHEN 'home' THEN 2
                            WHEN 'work' THEN 3
                            ELSE 4
                        END
                ),
                '-'
            ) AS phones
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON p.contact_id = c.id
        {where_sql}
        GROUP BY c.id, c.name, c.email, c.birthday, g.name, c.created_at
        ORDER BY {order_sql}, c.id ASC
        {limit_sql};
    """

    cur.execute(query, params)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows

def get_contacts():
    rows = fetch_contacts()
    print_contacts_table(rows)

def get_groups():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT name FROM groups ORDER BY id;")
    groups = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return groups

def filter_by_group(group_name):
    rows = fetch_contacts(group_name=group_name)
    print_contacts_table(rows)

def search_by_email(email_pattern):
    rows = fetch_contacts(email_pattern=email_pattern)
    print_contacts_table(rows)

def sort_contacts(sort_by):
    rows = fetch_contacts(sort_by=sort_by)
    print_contacts_table(rows)

def get_contacts_page(limit, offset):
    """
    Uses the old Practice 8 pagination function to get page IDs,
    then joins with the extended TSIS 1 tables for nice output.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            WITH page AS (
                SELECT id
                FROM get_contacts_paginated(%s, %s)
            )
            SELECT
                c.id,
                c.name,
                COALESCE(c.email, '-') AS email,
                COALESCE(c.birthday::TEXT, '-') AS birthday,
                COALESCE(g.name, '-') AS group_name,
                COALESCE(
                    string_agg(
                        p.type || ': ' || p.phone,
                        ', '
                        ORDER BY
                            CASE p.type
                                WHEN 'mobile' THEN 1
                                WHEN 'home' THEN 2
                                WHEN 'work' THEN 3
                                ELSE 4
                            END
                    ),
                    '-'
                ) AS phones
            FROM page pg
            JOIN contacts c ON c.id = pg.id
            LEFT JOIN groups g ON c.group_id = g.id
            LEFT JOIN phones p ON p.contact_id = c.id
            GROUP BY c.id, c.name, c.email, c.birthday, g.name
            ORDER BY c.id;
            """,
            (limit, offset)
        )

        rows = cur.fetchall()

    except Exception:
        conn.rollback()
        cur.close()
        conn.close()

        # Fallback if the old DB function has a different return structure.
        return fetch_contacts(sort_by="id", limit=limit, offset=offset)

    cur.close()
    conn.close()

    return rows

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

    print_contacts_table(rows)

    cur.close()
    conn.close()

def insert_or_update_user(name, phone):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL insert_or_update_user(%s, %s);", (name, phone)) # calling function from procedures 

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
   
def export_to_json(filename):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            c.id,
            c.name,
            c.email,
            c.birthday::TEXT,
            COALESCE(g.name, 'Other') AS group_name,
            p.phone,
            p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON p.contact_id = c.id
        ORDER BY c.id,
            CASE p.type
                WHEN 'mobile' THEN 1
                WHEN 'home' THEN 2
                WHEN 'work' THEN 3
                ELSE 4
            END;
        """
    )

    rows = cur.fetchall()

    contacts_dict = {}

    for row in rows:
        contact_id = row[0]

        if contact_id not in contacts_dict:
            contacts_dict[contact_id] = {
                "name": row[1],
                "email": row[2],
                "birthday": row[3],
                "group": row[4],
                "phones": []
            }

        if row[5]:
            contacts_dict[contact_id]["phones"].append(
                {
                    "phone": row[5],
                    "type": row[6]
                }
            )

    contacts = list(contacts_dict.values())

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(contacts, file, indent=4, ensure_ascii=False)

    cur.close()
    conn.close()

    print(f"Exported {len(contacts)} contacts to {filename}")

def import_from_json(filename):
    conn = get_connection()
    cur = conn.cursor()

    try:
        with open(filename, "r", encoding="utf-8") as file:
            contacts = json.load(file)

        if isinstance(contacts, dict) and "contacts" in contacts:
            contacts = contacts["contacts"]

        imported_count = 0
        skipped_count = 0
        overwritten_count = 0

        for contact in contacts:
            name = contact.get("name", "").strip()
            email = contact.get("email") or None
            birthday = contact.get("birthday") or None
            group_name = contact.get("group", "Other")
            phones = contact.get("phones", [])

            if not name:
                print("Skipped contact without name.")
                skipped_count += 1
                continue

            cur.execute(
                "SELECT id FROM contacts WHERE LOWER(name) = LOWER(%s);",
                (name,)
            )

            existing_contact = cur.fetchone()

            action = None

            if existing_contact:
                while True:
                    action = input(
                        f"Contact '{name}' already exists. Skip or overwrite? (skip/overwrite): "
                    ).strip().lower()

                    if action in ["skip", "s", "overwrite", "o"]:
                        break

                    print("Please enter skip or overwrite.")

                if action in ["skip", "s"]:
                    skipped_count += 1
                    continue

            group_id = get_or_create_group(cur, group_name)

            main_phone = None

            for phone_data in phones:
                if phone_data.get("type") == "mobile":
                    main_phone = phone_data.get("phone")
                    break

            if not main_phone and phones:
                main_phone = phones[0].get("phone")

            if existing_contact and action in ["overwrite", "o"]:
                contact_id = existing_contact[0]

                cur.execute(
                    """
                    UPDATE contacts
                    SET phone = %s,
                        email = %s,
                        birthday = %s,
                        group_id = %s
                    WHERE id = %s;
                    """,
                    (main_phone, email, birthday, group_id, contact_id)
                )

                cur.execute(
                    "DELETE FROM phones WHERE contact_id = %s;",
                    (contact_id,)
                )

                overwritten_count += 1

            else:
                cur.execute(
                    """
                    INSERT INTO contacts (name, phone, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (name, main_phone, email, birthday, group_id)
                )

                contact_id = cur.fetchone()[0]
                imported_count += 1

            for phone_data in phones:
                phone = phone_data.get("phone")
                phone_type = phone_data.get("type", "mobile")

                insert_phone(cur, contact_id, phone, phone_type)

        conn.commit()

        print("JSON import finished!")
        print(f"Imported: {imported_count}")
        print(f"Overwritten: {overwritten_count}")
        print(f"Skipped: {skipped_count}")

    except Exception as e:
        conn.rollback()
        print("JSON import failed:", e)

    finally:
        cur.close()
        conn.close()

def add_phone_to_contact(contact_name, phone, phone_type):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "CALL add_phone(%s, %s, %s);",
            (contact_name, phone, phone_type)
        )

        conn.commit()
        print("Phone added successfully!")

    except Exception as e:
        conn.rollback()
        print("Failed to add phone:", e)

    finally:
        cur.close()
        conn.close()

def move_contact_to_group(contact_name, group_name):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "CALL move_to_group(%s, %s);",
            (contact_name, group_name)
        )

        conn.commit()
        print("Contact moved successfully!")

    except Exception as e:
        conn.rollback()
        print("Failed to move contact:", e)

    finally:
        cur.close()
        conn.close()


