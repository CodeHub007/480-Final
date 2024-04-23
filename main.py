import sqlite3
import createDB
from datetime import datetime

def librarian_menu():
    print("Librarian Menu:")
    print("1. Manage Documents")
    print("2. Client Management")
    print("3. Exit")
    choice = input("Enter your choice: ")
    return choice

def manage_documents_menu():
    print("Manage Documents:")
    print("1. Insert New Document")
    print("2. Update Document")
    print("3. Delete Document Copy")
    print("4. Go Back to Librarian Menu")
    choice = input("Enter your choice: ")
    return choice

def insert_new_book():
    print("Insert New Book:")
    isbn = input("Enter ISBN: ")
    title = input("Enter title: ")
    publisher = input("Enter publisher: ")
    edition = input("Enter edition: ")
    num_pages = input("Enter number of pages: ")
    authors = input("Enter authors (comma-separated): ").split(',')

    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT isbn FROM book WHERE isbn = ?", (isbn,))
        if cursor.fetchone():
            print("A book with this ISBN already exists.")
            return
        try:
            cursor.execute("INSERT INTO book (isbn, publisher, title, edition, num_pages) VALUES (?, ?, ?, ?, ?)",
                           (isbn, publisher, title, edition, num_pages))
            for author in authors:
                cursor.execute("INSERT INTO book_authors (isbn, author) VALUES (?, ?)", (isbn, author))
            conn.commit()
            print("Book inserted successfully.")
        except sqlite3.IntegrityError as e:
            print(f"Failed to insert the book. Error: {e}")


def update_document():
    isbn = input("Enter the ISBN of the document to update: ")
    print("What would you like to update?")
    print("1. Title")
    print("2. Publisher")
    print("3. Number of Pages")
    update_choice = input("Enter your choice: ")

    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        if update_choice == "1":
            new_title = input("Enter the new title: ")
            cursor.execute("UPDATE book SET title = ? WHERE isbn = ?", (new_title, isbn))
        elif update_choice == "2":
            new_publisher = input("Enter the new publisher: ")
            cursor.execute("UPDATE book SET publisher = ? WHERE isbn = ?", (new_publisher, isbn))
        elif update_choice == "3":
            new_num_pages = input("Enter the new number of pages: ")
            if new_num_pages.isdigit():  # Ensure that the input is a number
                cursor.execute("UPDATE book SET num_pages = ? WHERE isbn = ?", (int(new_num_pages), isbn))
            else:
                print("Invalid input for number of pages. It must be a number.")
                return

        if cursor.rowcount == 0:
            print("No document found with the given ISBN or update failed.")
        else:
            conn.commit()
            print("Document updated successfully.")

def return_document():
    email = input("Enter your email: ")
    isbn = input("Enter the ISBN of the document to return: ")
    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT due_date FROM client_loans WHERE isbn = ? AND email = ?", (isbn, email))
        result = cursor.fetchone()
        if result:
            due_date = datetime.strptime(result[0], '%Y-%m-%d')
            return_date = datetime.now()
            overdue_days = (return_date - due_date).days
            if overdue_days > 0:
                overdue_fee = 5 * overdue_days
                cursor.execute("UPDATE client SET overdue_fees = overdue_fees + ? WHERE email = ?", (overdue_fee, email))
                print(f"Document is overdue. Fee charged: ${overdue_fee:.2f}")
            cursor.execute("UPDATE document SET on_loan = 0 WHERE isbn = ?", (isbn,))
            conn.commit()
            print("Document returned successfully.")
        else:
            print("No loan record found for this document and client.")


def update_client_information():
    email = input("Enter the client's email to update: ")
    new_name = input("Enter the new name for the client: ")
    
    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE client SET name = ? WHERE email = ?", (new_name, email))
        if cursor.rowcount == 0:
            print("No client found with the given email.")
        else:
            conn.commit()
            print("Client information updated successfully.")


def register_new_client():
    print("Register New Client:")
    name = input("Enter client's name: ")
    email = input("Enter client's email: ")
    addresses = input("Enter client's addresses (comma-separated): ").split(',')
    payment_methods = input("Enter payment card numbers (comma-separated): ").split(',')

    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM client WHERE email = ?", (email,))
        if cursor.fetchone():
            print("A client with this email already exists.")
            return
        try:
            cursor.execute("INSERT INTO client (email, name) VALUES (?, ?)", (email, name))
            for address in addresses:
                cursor.execute("INSERT INTO client_addresses (email, address) VALUES (?, ?)", (email, address))
            for card_number in payment_methods:
                cursor.execute("INSERT INTO client_credit_cards (email, credit_card_number) VALUES (?, ?)", (email, card_number))
            conn.commit()
            print("Client registered successfully with multiple addresses and payment methods.")
        except sqlite3.IntegrityError as e:
            print(f"Failed to register client. Error: {e}")


def search_documents_by_title():
    title_search = input("Enter the title to search for: ")
    
    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT isbn, title, publisher FROM book WHERE title LIKE ?", ('%' + title_search + '%',))
        books = cursor.fetchall()
        if books:
            for book in books:
                print(f"ISBN: {book[0]}, Title: {book[1]}, Publisher: {book[2]}")
        else:
            print("No books found with the given title.")

def search_documents_advanced():
    print("Advanced Document Search:")
    search_type = input("Search by (title/author/isbn/publisher/year): ").lower()
    search_query = input("Enter search value: ")

    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        query = {
            'title': "SELECT isbn, title, publisher FROM book WHERE title LIKE ?",
            'author': "SELECT b.isbn, b.title, b.publisher FROM book b JOIN book_authors ba ON b.isbn = ba.isbn WHERE ba.author LIKE ?",
            'isbn': "SELECT isbn, title, publisher FROM book WHERE isbn = ?",
            'publisher': "SELECT isbn, title, publisher FROM book WHERE publisher LIKE ?",
            'year': "SELECT isbn, title, publisher FROM book WHERE year = ?"
        }
        execute_query = query.get(search_type, "SELECT isbn, title, publisher FROM book WHERE title LIKE ?")  # Default to title search
        cursor.execute(execute_query, ('%' + search_query + '%',) if search_type != 'isbn' and search_type != 'year' else (search_query,))
        books = cursor.fetchall()
        if books:
            for book in books:
                print(f"ISBN: {book[0]}, Title: {book[1]}, Publisher: {book[2]}")
        else:
            print("No books found matching the criteria.")


def delete_document_copy():
    copy_number = input("Enter the copy number of the document to delete: ")
    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT on_loan FROM document WHERE copy_number = ?", (copy_number,))
        result = cursor.fetchone()
        if result and not result[0]:  # Checking if the document is not on loan
            cursor.execute("DELETE FROM document WHERE copy_number = ?", (copy_number,))
            conn.commit()
            print("Document copy deleted successfully.")
        elif result:
            print("Cannot delete the document copy as it is currently on loan.")
        else:
            print("Document copy not found.")

def borrow_document():
    email = input("Enter your email: ")
    isbn = input("Enter the ISBN of the book to borrow: ")
    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT on_loan FROM document WHERE isbn = ?", (isbn,))
        document = cursor.fetchone()
        if document and not document[0]:  # Check if the document is not currently on loan
            cursor.execute("UPDATE document SET on_loan = 1 WHERE isbn = ?", (isbn,))
            conn.commit()
            print("Document successfully borrowed.")
        else:
            print("This document is currently unavailable.")


def client_management_menu():
    print("Client Management:")
    print("1. Register New Client")
    print("2. Update Client Information")
    print("3. Delete Client")
    print("4. Go Back to Librarian Menu")
    choice = input("Enter your choice: ")
    return choice

def client_menu():
    print("Client Menu:")
    print("1. Search for Documents")
    print("2. Borrow a Document")
    print("3. Return a Document")
    print("4. Pay Overdue Fees")
    print("5. Manage Payment Methods")
    print("6. Exit")
    choice = input("Enter your choice: ")
    return choice

def search_documents_menu():
    print("Search for Documents:")
    print("1. Search by Title")
    print("2. Search by Author")
    print("3. Search by ISBN")
    print("4. Search by Publisher")
    print("5. Search by Edition")
    print("6. Search by Year")
    print("7. Go Back to Client Menu")
    choice = input("Enter your choice: ")
    return choice

def manage_payment_methods_menu():
    print("Manage Payment Methods:")
    print("1. Add Payment Method")
    print("2. Delete Payment Method")
    print("3. Go Back to Client Menu")
    choice = input("Enter your choice: ")
    return choice


def main():
    # Calling the function to create the database schema
    createDB.create_schema()
    # Main loop
    while True:
        user_type = input("Are you a librarian or a client? (L/C): ").upper()
        
        if user_type == "L":
            while True:
                choice = librarian_menu()
                if choice == "1":
                    while True:
                        doc_choice = manage_documents_menu()
                        if doc_choice == "1":
                            insert_new_book()
                            # Implementing the insert document functionality
                        elif doc_choice == "2":
                            update_document()
                            # Implementing the update document functionality
                        elif doc_choice == "3":
                            delete_document_copy()
                            # Implementing the x delete document copy functionality
                        elif doc_choice == "4":
                            break
                        else:
                            print("Invalid choice. Please try again.")
                elif choice == "2":
                    while True:
                        client_choice = client_management_menu()
                        if client_choice == "1":
                            print("Registering new client...")
                            # Implementing the register new client functionality
                        elif client_choice == "2":
                            update_client_information()
                            # Implementing the  update client information functionality
                        elif client_choice == "3":
                            print("Deleting client...")
                            # Implementing the  delete client functionality
                        elif client_choice == "4":
                            break
                        else:
                            print("Invalid choice. Please try again.")
                elif choice == "3":
                    print("Exiting the program...")
                    exit()
                else:
                    print("Invalid choice. Please try again.")

        elif user_type == "C":
            while True:
                choice = client_menu()
                if choice == "1":
                    while True:
                        search_choice = search_documents_menu()
                        if search_choice == "1":
                            search_documents_by_title()
                            # Implement search documents by title functionality
                        elif search_choice == "2":
                            print("Searching documents by author...")
                            # Implement search documents by author functionality
                        elif search_choice == "3":
                            print("Searching documents by ISBN...")
                            # Implement search documents by ISBN functionality
                        elif search_choice == "4":
                            print("Searching documents by publisher...")
                            # Implement search documents by publisher functionality
                        elif search_choice == "5":
                            print("Searching documents by edition...")
                            # Implement search documents by edition functionality
                        elif search_choice == "6":
                            print("Searching documents by year...")
                            # Implement search documents by year functionality
                        elif search_choice == "7":
                            break
                        else:
                            print("Invalid choice. Please try again.")
                elif choice == "2":
                    print("Borrowing a document...")
                    # Implement borrow document functionality
                elif choice == "3":
                    print("Returning a document...")
                    # Implement return document functionality
                elif choice == "4":
                    print("Paying overdue fees...")
                    # Implement pay overdue fees functionality
                elif choice == "5":
                    while True:
                        payment_choice = manage_payment_methods_menu()
                        if payment_choice == "1":
                            print("Adding payment method...")
                            # Implement add payment method functionality
                        elif payment_choice == "2":
                            print("Deleting payment method...")
                            # Implement delete payment method functionality
                        elif payment_choice == "3":
                            break
                        else:
                            print("Invalid choice. Please try again.")
                elif choice == "6":
                    print("Exiting the program...")
                    exit()
                else:
                    print("Invalid choice. Please try again.")

        else:
            print("Invalid choice. Please enter 'L' for librarian or 'C' for client.")

if __name__ == "__main__":
    main()