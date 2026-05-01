import csv
import json
from pathlib import Path

from connect import get_connection


class PhoneBook:
    def __init__(self):
        self.connection = get_connection()
        self.contacts = []
        self.next_id = 1

        if self.connection is None:
            print("Running in local mode without PostgreSQL.")
        else:
            print("Connected to PostgreSQL.")

    def add_contact(self, first_name, last_name, email, birthday, group, phone):
        if self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO groups(name)
                    VALUES (%s)
                    ON CONFLICT (name) DO NOTHING;
                    """,
                    (group,)
                )

                cursor.execute(
                    "SELECT id FROM groups WHERE name = %s;",
                    (group,)
                )
                group_id = cursor.fetchone()[0]

                cursor.execute(
                    """
                    INSERT INTO contacts(first_name, last_name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (first_name, last_name, email, birthday, group_id)
                )

                contact_id = cursor.fetchone()[0]

                cursor.execute(
                    """
                    INSERT INTO phones(contact_id, phone)
                    VALUES (%s, %s);
                    """,
                    (contact_id, phone)
                )

                self.connection.commit()

            return

        contact = {
            "id": self.next_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "birthday": birthday,
            "group": group,
            "phones": [phone]
        }

        self.contacts.append(contact)
        self.next_id += 1

    def show_contacts(self):
        contacts = self.get_all_contacts()

        if not contacts:
            print("No contacts.")
            return

        for contact in contacts:
            print(contact)

    def get_all_contacts(self):
        if self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        c.id,
                        c.first_name,
                        c.last_name,
                        c.email,
                        c.birthday,
                        g.name,
                        p.phone
                    FROM contacts c
                    LEFT JOIN groups g ON g.id = c.group_id
                    LEFT JOIN phones p ON p.contact_id = c.id
                    ORDER BY c.id;
                    """
                )

                rows = cursor.fetchall()

            result = []

            for row in rows:
                result.append({
                    "id": row[0],
                    "first_name": row[1],
                    "last_name": row[2],
                    "email": row[3],
                    "birthday": str(row[4]),
                    "group": row[5],
                    "phone": row[6]
                })

            return result

        return self.contacts

    def search_contacts(self, pattern):
        pattern = pattern.lower()

        if self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        c.id,
                        c.first_name,
                        c.last_name,
                        c.email,
                        c.birthday,
                        g.name,
                        p.phone
                    FROM contacts c
                    LEFT JOIN groups g ON g.id = c.group_id
                    LEFT JOIN phones p ON p.contact_id = c.id
                    WHERE
                        c.first_name ILIKE %s
                        OR c.last_name ILIKE %s
                        OR c.email ILIKE %s
                        OR g.name ILIKE %s
                        OR p.phone ILIKE %s;
                    """,
                    tuple([f"%{pattern}%"] * 5)
                )

                rows = cursor.fetchall()

            for row in rows:
                print(row)

            return

        for contact in self.contacts:
            phones_text = " ".join(contact["phones"]).lower()

            if (
                pattern in contact["first_name"].lower()
                or pattern in contact["last_name"].lower()
                or pattern in contact["email"].lower()
                or pattern in contact["group"].lower()
                or pattern in phones_text
            ):
                print(contact)

    def update_contact(self, contact_id, field, value):
        if self.connection:
            allowed_fields = ["first_name", "last_name", "email", "birthday"]

            if field not in allowed_fields:
                print("Invalid field for database update.")
                return

            with self.connection.cursor() as cursor:
                cursor.execute(
                    f"UPDATE contacts SET {field} = %s WHERE id = %s;",
                    (value, contact_id)
                )
                self.connection.commit()

            return

        for contact in self.contacts:
            if contact["id"] == contact_id:
                if field in contact:
                    contact[field] = value
                    return

        print("Contact not found.")

    def delete_contact(self, contact_id):
        if self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM contacts WHERE id = %s;",
                    (contact_id,)
                )
                self.connection.commit()

            return

        self.contacts = [
            contact for contact in self.contacts
            if contact["id"] != contact_id
        ]

    def add_phone_to_contact(self, contact_id, phone):
        if self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO phones(contact_id, phone)
                    VALUES (%s, %s);
                    """,
                    (contact_id, phone)
                )
                self.connection.commit()

            return

        for contact in self.contacts:
            if contact["id"] == contact_id:
                contact["phones"].append(phone)
                return

        print("Contact not found.")

    def move_to_group(self, contact_id, group):
        if self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO groups(name)
                    VALUES (%s)
                    ON CONFLICT (name) DO NOTHING;
                    """,
                    (group,)
                )

                cursor.execute(
                    "SELECT id FROM groups WHERE name = %s;",
                    (group,)
                )
                group_id = cursor.fetchone()[0]

                cursor.execute(
                    """
                    UPDATE contacts
                    SET group_id = %s
                    WHERE id = %s;
                    """,
                    (group_id, contact_id)
                )

                self.connection.commit()

            return

        for contact in self.contacts:
            if contact["id"] == contact_id:
                contact["group"] = group
                return

        print("Contact not found.")

    def export_json(self, filename):
        data = self.get_all_contacts()

        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

        print(f"Exported to {filename}")

    def import_csv(self, filename):
        path = Path(filename)

        if not path.exists():
            print("CSV file not found.")
            return

        with open(path, "r") as file:
            reader = csv.DictReader(file)

            for row in reader:
                self.add_contact(
                    row["first_name"],
                    row["last_name"],
                    row["email"],
                    row["birthday"],
                    row["group"],
                    row["phone"]
                )

        print("CSV imported.")

    def paginate(self, page, page_size):
        data = self.get_all_contacts()

        start = (page - 1) * page_size
        end = start + page_size

        for contact in data[start:end]:
            print(contact)

    def sort_contacts(self, field):
        data = self.get_all_contacts()

        try:
            data.sort(key=lambda contact: str(contact.get(field, "")))
        except Exception:
            print("Cannot sort by this field.")
            return

        for contact in data:
            print(contact)


def print_menu():
    print()
    print("1. Add contact")
    print("2. Show contacts")
    print("3. Search")
    print("4. Update contact")
    print("5. Delete contact")
    print("6. Add phone")
    print("7. Move to group")
    print("8. Import CSV")
    print("9. Export JSON")
    print("10. Pagination")
    print("11. Sort")
    print("0. Exit")


def main():
    phonebook = PhoneBook()

    while True:
        print_menu()
        command = input("Choose: ")

        if command == "1":
            first_name = input("First name: ")
            last_name = input("Last name: ")
            email = input("Email: ")
            birthday = input("Birthday YYYY-MM-DD: ")
            group = input("Group: ")
            phone = input("Phone: ")

            phonebook.add_contact(first_name, last_name, email, birthday, group, phone)

        elif command == "2":
            phonebook.show_contacts()

        elif command == "3":
            pattern = input("Search pattern: ")
            phonebook.search_contacts(pattern)

        elif command == "4":
            contact_id = int(input("Contact id: "))
            field = input("Field first_name/last_name/email/birthday/group: ")
            value = input("New value: ")

            if field == "group":
                phonebook.move_to_group(contact_id, value)
            else:
                phonebook.update_contact(contact_id, field, value)

        elif command == "5":
            contact_id = int(input("Contact id: "))
            phonebook.delete_contact(contact_id)

        elif command == "6":
            contact_id = int(input("Contact id: "))
            phone = input("Phone: ")
            phonebook.add_phone_to_contact(contact_id, phone)

        elif command == "7":
            contact_id = int(input("Contact id: "))
            group = input("New group: ")
            phonebook.move_to_group(contact_id, group)

        elif command == "8":
            phonebook.import_csv("contacts.csv")

        elif command == "9":
            phonebook.export_json("contacts.json")

        elif command == "10":
            page = int(input("Page: "))
            page_size = int(input("Page size: "))
            phonebook.paginate(page, page_size)

        elif command == "11":
            field = input("Sort by first_name/last_name/email/birthday/group: ")
            phonebook.sort_contacts(field)

        elif command == "0":
            break

        else:
            print("Unknown command.")


if __name__ == "__main__":
    main()