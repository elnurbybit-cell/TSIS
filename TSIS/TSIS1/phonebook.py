contacts = []

def add_contact(name, phone):
    contacts.append({"name": name, "phone": phone})

def show_contacts():
    for c in contacts:
        print(c["name"], c["phone"])

while True:
    cmd = input("1 add, 2 show, 0 exit: ")

    if cmd == "1":
        name = input("Name: ")
        phone = input("Phone: ")
        add_contact(name, phone)

    elif cmd == "2":
        show_contacts()

    elif cmd == "0":
        break