from flask import Flask
import sqlite3
import os

app = Flask(__name__)

# Путь к базе данных
DATABASE_PATH = 'writers.db'

def init_db():
    """Создаем базу данных и таблицу"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS writers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL
        )
    ''')
    
    # Добавляем тестовых писателей
    cursor.execute("SELECT COUNT(*) FROM writers")
    if cursor.fetchone()[0] == 0:
        writers_data = [
            ('Дмитрий', 'Балашов'),
            ('Исаак', 'Бацер'),
            ('Владимир', 'Брендоев')
        ]
        for first_name, last_name in writers_data:
            cursor.execute("INSERT INTO writers (first_name, last_name) VALUES (?, ?)", 
                          (first_name, last_name))
    
    conn.commit()
    conn.close()

def get_writers():
    """Получаем всех писателей из БД"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM writers')
    writers = cursor.fetchall()
    conn.close()
    return writers

@app.route('/')
def index():
    writers = get_writers()
    
    # Простой текстовый вывод вместо HTML
    result = "СПИСОК ПИСАТЕЛЕЙ:\n\n"
    for writer in writers:
        result += f"{writer[0]}. {writer[1]} {writer[2]}\n"
    
    result += f"\nВсего писателей: {len(writers)}"
    
    return f"<pre>{result}</pre>"

if __name__ == '__main__':
    init_db()
    app.run(debug=True)