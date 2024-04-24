# import sqlite3

# # Connect to the database (or create it if it doesn't exist)
# conn = sqlite3.connect('library.db')
# cursor = conn.cursor()

# # Create tables
# def create_schema():
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS log (
#             email VARCHAR(255) PRIMARY KEY,
#             password VARCHAR(255)
#         )
#     ''')

#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS credit_card (
#             credit_card_number VARCHAR(16) PRIMARY KEY,
#             ccv_number VARCHAR(3),
#             address VARCHAR(255)
#         )
#     ''')

#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS client (
#             email VARCHAR(255) PRIMARY KEY,
#             overdue_fees DECIMAL(10, 2),
#             name VARCHAR(255),
#             log_email VARCHAR(255),
#             FOREIGN KEY (log_email) REFERENCES log(email)
#         )
#     ''')

#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS client_addresses (
#             email VARCHAR(255),
#             address VARCHAR(255),
#             PRIMARY KEY (email, address),
#             FOREIGN KEY (email) REFERENCES client(email)
#         )
#     ''')

#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS client_credit_cards (
#             email VARCHAR(255),
#             credit_card_number VARCHAR(16),
#             PRIMARY KEY (email, credit_card_number),
#             FOREIGN KEY (email) REFERENCES client(email)
#         )
#     ''')

#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS client_loans (
#             email VARCHAR(255),
#             isbn VARCHAR(13),
#             PRIMARY KEY (email, isbn),
#             FOREIGN KEY (email) REFERENCES client(email)
#         )
#     ''')

#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS librarian (
#             SSN VARCHAR(255) PRIMARY KEY,
#             name VARCHAR(255),
#             email VARCHAR(255),
#             salary DECIMAL(10, 2),
#             log_email VARCHAR(255),
#             FOREIGN KEY (log_email) REFERENCES log(email)
#         )
#     ''')

#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS librarian_client (
#             librarian_SSN VARCHAR(255),
#             client_email VARCHAR(255),
#             PRIMARY KEY (librarian_SSN, client_email),
#             FOREIGN KEY (librarian_SSN) REFERENCES librarian(SSN),
#             FOREIGN KEY (client_email) REFERENCES client(email)
#         )
#     ''')

#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS document (
#             copy_number INT PRIMARY KEY,
#             on_loan BOOLEAN,
#             year INT
#         )
#     ''')

#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS journal_article (
#             title VARCHAR(255) PRIMARY KEY,
#             journal_name VARCHAR(255),
#             isbn VARCHAR(13),
#             issue_number INT,
#             publisher VARCHAR(255)
#         )
#     ''')

#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS journal_article_authors (
#             title VARCHAR(255),
#             author VARCHAR(255),
#             PRIMARY KEY (title, author),
#             FOREIGN KEY (title) REFERENCES journal_article(title)
#         )
#     ''')

#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS bound_document (
#             isbn VARCHAR(13) PRIMARY KEY,
#             publisher VARCHAR(255)
#         )
#     ''')

#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS magazine (
#             isbn VARCHAR(13) PRIMARY KEY,
#             publisher VARCHAR(255),
#             magazine_name VARCHAR(255),
#             month VARCHAR(255)
#         )
#     ''')

#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS book (
#             isbn VARCHAR(13) PRIMARY KEY,
#             publisher VARCHAR(255),
#             title VARCHAR(255),
#             edition VARCHAR(255),
#             num_pages INT
#         )
#     ''')

#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS book_authors (
#             isbn VARCHAR(13),
#             author VARCHAR(255),
#             PRIMARY KEY (isbn, author),
#             FOREIGN KEY (isbn) REFERENCES book(isbn)
#         )
#     ''')

#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS client_documents (
#             email VARCHAR(255),
#             copy_number INT,
#             PRIMARY KEY (email, copy_number),
#             FOREIGN KEY (email) REFERENCES client(email),
#             FOREIGN KEY (copy_number) REFERENCES document(copy_number)
#         )
#     ''')

#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS librarian_documents (
#             SSN VARCHAR(255),
#             copy_number INT,
#             PRIMARY KEY (SSN, copy_number),
#             FOREIGN KEY (SSN) REFERENCES librarian(SSN),
#             FOREIGN KEY (copy_number) REFERENCES document(copy_number)
#         )
#     ''')

#     # Commit changes and close connection
#     conn.commit()
#     conn.close()

#     print("Database schema created successfully.")

import sqlite3

def create_schema():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    # Logins for both librarians and clients
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS log (
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')

    # Librarian information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS librarian (
            SSN TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            salary REAL NOT NULL,
            FOREIGN KEY (email) REFERENCES log(email)
        )
    ''')

    # Client information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS client (
            email TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            overdue_fees REAL DEFAULT 0,
            FOREIGN KEY (email) REFERENCES log(email)
        )
    ''')

    # Addresses associated with clients
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_email TEXT NOT NULL,
            address TEXT NOT NULL,
            FOREIGN KEY (client_email) REFERENCES client(email)
        )
    ''')

    # Credit cards associated with client addresses
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credit_cards (
            credit_card_number TEXT PRIMARY KEY,
            ccv_number TEXT NOT NULL,
            client_email TEXT NOT NULL,
            address_id INTEGER NOT NULL,
            FOREIGN KEY (client_email) REFERENCES client(email),
            FOREIGN KEY (address_id) REFERENCES addresses(id)
        )
    ''')

    # Books
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS book (
            isbn TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            publisher TEXT NOT NULL,
            edition TEXT,
            num_pages INTEGER
        )
    ''')

    # Authors of books
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS book_authors (
            isbn TEXT NOT NULL,
            author TEXT NOT NULL,
            PRIMARY KEY (isbn, author),
            FOREIGN KEY (isbn) REFERENCES book(isbn)
        )
    ''')

    # Document generalization for all types of documents
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS document (
            copy_number INTEGER PRIMARY KEY,
            isbn TEXT NOT NULL,
            on_loan BOOLEAN NOT NULL DEFAULT 0,
            FOREIGN KEY (isbn) REFERENCES book(isbn)
        )
    ''')

    # Client loans for tracking which clients have which documents out
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS client_loans (
            email TEXT NOT NULL,
            copy_number INTEGER NOT NULL,
            due_date TEXT NOT NULL,
            returned INTEGER DEFAULT 0,
            PRIMARY KEY (email, copy_number),
            FOREIGN KEY (email) REFERENCES client(email),
            FOREIGN KEY (copy_number) REFERENCES document(copy_number)
        )
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print("Database schema created successfully.")

if __name__ == "__main__":
    create_schema()
