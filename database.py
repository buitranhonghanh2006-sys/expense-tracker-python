import sqlite3

class ExpenseDatabase:
    def __init__(self, db_name='expenses.db'):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_expenses_table()

    def create_expenses_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )''')
        self.connection.commit()

    def add_expense(self, amount, description, date):
        self.cursor.execute('''INSERT INTO expenses (amount, description, date)
                              VALUES (?, ?, ?)''', (amount, description, date))
        self.connection.commit()

    def get_expenses(self):
        self.cursor.execute('SELECT * FROM expenses')
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()