import json
import os
import re
import sys

# Reconfigure stdout to use UTF-8 to support emojis/colors cleanly on Windows terminal
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ANSI escape codes for coloring terminal output
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"

DB_FILE = "contacts.json"

def clear_screen():
    print("\033[H\033[J", end="")

def load_contacts():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"{RED}Error loading database. Starting with empty contact list.{RESET}")
        return []

def save_contacts(contacts):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(contacts, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"{RED}Failed to save contacts: {e}{RESET}")

def validate_phone(phone):
    # Matches simple international/national number formats (digits, spaces, hyphens, plus)
    return bool(re.match(r'^\+?[\d\s-]{7,15}$', phone))

def validate_email(email):
    if not email:
        return True  # Email is optional
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))

def add_contact(contacts):
    print(f"\n{CYAN}{BOLD}--- Add New Contact ---{RESET}")
    
    # Get Name
    while True:
        name = input(f"{BOLD}Name (Required):{RESET} ").strip()
        if name:
            break
        print(f"{RED}Name cannot be empty!{RESET}")
    
    # Check if name already exists
    for c in contacts:
        if c['name'].lower() == name.lower():
            print(f"{YELLOW}Warning: A contact named '{c['name']}' already exists.{RESET}")
            if not input("Do you still want to add this contact? (y/n): ").strip().lower().startswith('y'):
                return

    # Get Phone
    while True:
        phone = input(f"{BOLD}Phone Number (Required):{RESET} ").strip()
        if not phone:
            print(f"{RED}Phone number cannot be empty!{RESET}")
            continue
        if validate_phone(phone):
            break
        print(f"{RED}Invalid phone format. (e.g. +123456789 or 9876543210){RESET}")

    # Get Email (Optional)
    while True:
        email = input(f"{BOLD}Email Address (Optional):{RESET} ").strip()
        if validate_email(email):
            break
        print(f"{RED}Invalid email format. (e.g. name@example.com){RESET}")

    # Get Address (Optional)
    address = input(f"{BOLD}Address (Optional):{RESET} ").strip()

    # Get Notes (Optional)
    notes = input(f"{BOLD}Notes/Company (Optional):{RESET} ").strip()

    contacts.append({
        "name": name,
        "phone": phone,
        "email": email,
        "address": address,
        "notes": notes
    })
    
    # Sort contacts alphabetically by name
    contacts.sort(key=lambda x: x['name'].lower())
    save_contacts(contacts)
    print(f"\n{GREEN}{BOLD}🎉 Contact '{name}' added successfully!{RESET}")

def display_contacts(contacts):
    print(f"\n{CYAN}{BOLD}--- Contact List ({len(contacts)} total) ---{RESET}")
    if not contacts:
        print(f"{YELLOW}No contacts stored yet. Add some!{RESET}")
        return

    # Dynamic Column Width Calculation for Table
    col_idx_w = 4
    col_name_w = max(len(c['name']) for c in contacts)
    col_name_w = max(col_name_w, 15)
    col_phone_w = max(len(c['phone']) for c in contacts)
    col_phone_w = max(col_phone_w, 12)
    col_email_w = max(len(c['email']) for c in contacts)
    col_email_w = max(col_email_w, 20)

    # Table Header
    header = f"{'#' : <{col_idx_w}} | {'Name' : <{col_name_w}} | {'Phone' : <{col_phone_w}} | {'Email' : <{col_email_w}}"
    border = "-" * len(header)
    
    print(f"{BLUE}{BOLD}{border}{RESET}")
    print(f"{BLUE}{BOLD}{header}{RESET}")
    print(f"{BLUE}{BOLD}{border}{RESET}")

    for idx, c in enumerate(contacts, 1):
        email_str = c['email'] if c['email'] else "-"
        print(f"{idx : <{col_idx_w}} | {c['name'] : <{col_name_w}} | {c['phone'] : <{col_phone_w}} | {email_str : <{col_email_w}}")
    
    print(f"{BLUE}{BOLD}{border}{RESET}\n")

def view_contact_details(contacts):
    if not contacts:
        print(f"{YELLOW}No contacts available to view details.{RESET}")
        return
        
    display_contacts(contacts)
    try:
        choice = input(f"{BOLD}Enter the '#' of the contact to view details (or press Enter to return):{RESET} ").strip()
        if not choice:
            return
        idx = int(choice) - 1
        if 0 <= idx < len(contacts):
            c = contacts[idx]
            print(f"\n{MAGENTA}{BOLD}==========================================")
            print(f"               CONTACT DETAILS")
            print(f"=========================================={RESET}")
            print(f"{BOLD}Name:    {RESET}{c['name']}")
            print(f"{BOLD}Phone:   {RESET}{c['phone']}")
            print(f"{BOLD}Email:   {RESET}{c['email'] if c['email'] else '-'}")
            print(f"{BOLD}Address: {RESET}{c['address'] if c['address'] else '-'}")
            print(f"{BOLD}Notes:   {RESET}{c['notes'] if c['notes'] else '-'}")
            print(f"{MAGENTA}{BOLD}=========================================={RESET}")
        else:
            print(f"{RED}Invalid index number.{RESET}")
    except ValueError:
        print(f"{RED}Please enter a valid index number.{RESET}")

def search_contacts(contacts):
    print(f"\n{CYAN}{BOLD}--- Search Contacts ---{RESET}")
    query = input(f"{BOLD}Enter search query (Name / Phone / Email):{RESET} ").strip().lower()
    if not query:
        print(f"{RED}Search query cannot be empty!{RESET}")
        return

    results = []
    for c in contacts:
        if (query in c['name'].lower() or 
            query in c['phone'] or 
            (c['email'] and query in c['email'].lower())):
            results.append(c)

    if results:
        print(f"\n{GREEN}{BOLD}Found {len(results)} matching contact(s):{RESET}")
        display_contacts(results)
    else:
        print(f"{YELLOW}No matching contacts found for '{query}'.{RESET}")

def update_contact(contacts):
    print(f"\n{CYAN}{BOLD}--- Update Contact ---{RESET}")
    if not contacts:
        print(f"{YELLOW}No contacts available to update.{RESET}")
        return

    display_contacts(contacts)
    try:
        choice = input(f"{BOLD}Enter the '#' of the contact to update (or press Enter to cancel):{RESET} ").strip()
        if not choice:
            return
        idx = int(choice) - 1
        if not (0 <= idx < len(contacts)):
            print(f"{RED}Invalid index number.{RESET}")
            return
    except ValueError:
        print(f"{RED}Please enter a valid index number.{RESET}")
        return

    c = contacts[idx]
    print(f"\n{YELLOW}Updating '{c['name']}'. Press Enter to keep current value.{RESET}\n")

    # Update Name
    new_name = input(f"{BOLD}New Name ({c['name']}):{RESET} ").strip()
    if new_name:
        c['name'] = new_name

    # Update Phone
    while True:
        new_phone = input(f"{BOLD}New Phone ({c['phone']}):{RESET} ").strip()
        if not new_phone:
            break
        if validate_phone(new_phone):
            c['phone'] = new_phone
            break
        print(f"{RED}Invalid phone format.{RESET}")

    # Update Email
    while True:
        new_email = input(f"{BOLD}New Email ({c['email']}):{RESET} ").strip()
        if not new_email:
            break
        if validate_email(new_email):
            c['email'] = new_email
            break
        print(f"{RED}Invalid email format.{RESET}")

    # Update Address
    new_address = input(f"{BOLD}New Address ({c['address']}):{RESET} ").strip()
    if new_address:
        c['address'] = new_address

    # Update Notes
    new_notes = input(f"{BOLD}New Notes ({c['notes']}):{RESET} ").strip()
    if new_notes:
        c['notes'] = new_notes

    # Resort list alphabetically
    contacts.sort(key=lambda x: x['name'].lower())
    save_contacts(contacts)
    print(f"\n{GREEN}{BOLD}✓ Contact updated successfully!{RESET}")

def delete_contact(contacts):
    print(f"\n{CYAN}{BOLD}--- Delete Contact ---{RESET}")
    if not contacts:
        print(f"{YELLOW}No contacts available to delete.{RESET}")
        return

    display_contacts(contacts)
    try:
        choice = input(f"{BOLD}Enter the '#' of the contact to delete (or press Enter to cancel):{RESET} ").strip()
        if not choice:
            return
        idx = int(choice) - 1
        if 0 <= idx < len(contacts):
            c = contacts[idx]
            confirm = input(f"{RED}{BOLD}Are you sure you want to delete '{c['name']}'? (y/n): {RESET}").strip().lower()
            if confirm.startswith('y'):
                deleted_name = contacts.pop(idx)['name']
                save_contacts(contacts)
                print(f"\n{GREEN}{BOLD}✓ Contact '{deleted_name}' deleted successfully.{RESET}")
            else:
                print(f"{YELLOW}Deletion cancelled.{RESET}")
        else:
            print(f"{RED}Invalid index number.{RESET}")
    except ValueError:
        print(f"{RED}Please enter a valid index number.{RESET}")

def print_menu():
    print(f"{MAGENTA}{BOLD}============================================")
    print("              📇 CONTACT BOOK")
    print(f"============================================{RESET}")
    print(f"  {BLUE}{BOLD}1.{RESET} Add New Contact")
    print(f"  {BLUE}{BOLD}2.{RESET} View All Contacts")
    print(f"  {BLUE}{BOLD}3.{RESET} View Contact Details")
    print(f"  {BLUE}{BOLD}4.{RESET} Search Contacts")
    print(f"  {BLUE}{BOLD}5.{RESET} Update Contact")
    print(f"  {BLUE}{BOLD}6.{RESET} Delete Contact")
    print(f"  {BLUE}{BOLD}7.{RESET} Exit")
    print(f"{MAGENTA}{BOLD}============================================{RESET}")

def main():
    contacts = load_contacts()
    
    while True:
        clear_screen()
        print_menu()
        choice = input(f"\n{BOLD}Choose an option (1-7):{RESET} ").strip()
        
        if choice == '1':
            clear_screen()
            add_contact(contacts)
        elif choice == '2':
            clear_screen()
            display_contacts(contacts)
        elif choice == '3':
            clear_screen()
            view_contact_details(contacts)
        elif choice == '4':
            clear_screen()
            search_contacts(contacts)
        elif choice == '5':
            clear_screen()
            update_contact(contacts)
        elif choice == '6':
            clear_screen()
            delete_contact(contacts)
        elif choice == '7':
            print(f"\n{GREEN}Thank you for using Contact Book! Goodbye! 👋{RESET}\n")
            break
        else:
            print(f"{RED}Invalid choice! Please select between 1 and 7.{RESET}")
        
        input(f"\n{CYAN}Press Enter to return to main menu...{RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Program interrupted. Goodbye!{RESET}")
        sys.exit(0)
