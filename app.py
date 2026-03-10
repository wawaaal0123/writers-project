from flask import Flask
import sqlite3

app = Flask(__name__)
DATABASE_PATH = 'karelian_writers.db'

def get_authors_with_works():
    """Получаем авторов с их произведениями"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            authors.id,
            authors.full_name,
            GROUP_CONCAT(texts.title, '; ') as works_list
        FROM authors
        LEFT JOIN texts ON authors.id = texts.author_id
        GROUP BY authors.id
        ORDER BY authors.full_name
    """)

    results = cursor.fetchall()
    conn.close()
    return results

@app.route('/')
def index():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            authors.full_name,
            GROUP_CONCAT(
                texts.title || ' (' || COALESCE(texts.year_written, '?') ||
                ', ' || texts.type || ')',
                '; '
            ) as works_list
        FROM authors
        LEFT JOIN texts ON authors.id = texts.author_id
        GROUP BY authors.id
        ORDER BY authors.full_name
    """)

    authors = cursor.fetchall()
    conn.close()

    # Формируем текст для <pre> тега
    text_output = "КАРЕЛЬСКИЕ ПИСАТЕЛИ И ИХ ПРОИЗВЕДЕНИЯ:\n\n"

    for author in authors:
        text_output += f"{author[0]}\n"
        if author[1]:
            works = author[1].split('; ')
            for work in works:
                text_output += f"   • {work}\n"
        else:
            text_output += "   (произведения не добавлены)\n"
        text_output += "\n"

    text_output += f"Всего авторов: {len(authors)}"

    # Возвращаем с <pre> для форматирования И ссылкой внизу
    return f'''
    <pre>{text_output}</pre>
    <div style="margin-top: 20px; padding: 10px; background: #f5f5f5; border-radius: 5px;">
        <strong>Администрация:</strong>
        <a href="/admin" style="margin-left: 10px; color: #0066cc;">Перейти в админку</a>
        (добавить автора или произведение)
    </div>
    '''


# ===== АДМИНКА =====
from flask import request

@app.route('/admin')
def admin_index():
    return '''
    <h1>Админка</h1>
    <p>Добавление данных в базу</p>
    <ul>
        <li><a href="/admin/add_author">Добавить автора</a></li>
        <li><a href="/admin/add_text">Добавить произведение</a></li>
        <li><a href="/">← На сайт</a></li>
    </ul>
    '''

@app.route('/admin/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        full_name = request.form['full_name']
        birth_place = request.form.get('birth_place', '')

        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO authors (full_name, birth_place) VALUES (?, ?)",
            (full_name, birth_place)
        )
        conn.commit()
        conn.close()

        return '''
            <h2>✅ Автор добавлен!</h2>
            <p><a href="/admin/add_author">Добавить ещё</a> |
            <a href="/admin">В админку</a> |
            <a href="/">На сайт</a></p>
        '''

    return '''
    <h2>Добавить автора</h2>
    <form method="post">
        <p><b>ФИО:</b><br>
        <input type="text" name="full_name" required size="40"></p>

        <button type="submit">✅ Добавить автора</button>
    </form>
    <p><a href="/admin">← Назад</a></p>
    '''

@app.route('/admin/add_text', methods=['GET', 'POST'])
def add_text():
    if request.method == 'POST':
        title = request.form['title']
        text_type = request.form['type']
        author_id = request.form['author_id']
        year = request.form.get('year', '') or None

        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO texts (title, type, author_id, year_written, year_published)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, text_type, author_id, year, year))
        conn.commit()
        conn.close()

        return '''
            <h2>✅ Произведение добавлено!</h2>
            <p><a href="/admin/add_text">Добавить ещё</a> |
            <a href="/admin">В админку</a> |
            <a href="/">На сайт</a></p>
        '''

    # Получаем список авторов для выпадающего списка
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name FROM authors ORDER BY full_name")
    authors = cursor.fetchall()
    conn.close()

    options = ''
    for author in authors:
        options += f'<option value="{author[0]}">{author[1]}</option>'

    return f'''
    <h2>Добавить произведение</h2>
    <form method="post">
        <p><b>Название:</b><br>
        <input type="text" name="title" required size="50"></p>

        <p><b>Тип:</b><br>
        <select name="type">
            <option value="произведение автора">произведение автора</option>
            <option value="критическая статья">критическая статья</option>
            <option value="биографическая заметка">биографическая заметка</option>
            <option value="перевод">перевод</option>
        </select></p>

        <p><b>Автор:</b><br>
        <select name="author_id" required>
            <option value="">-- Выберите автора --</option>
            {options}
        </select></p>

        <p><b>Год написания:</b><br>
        <input type="number" name="year" min="1000" max="2025"></p>

        <button type="submit">✅ Добавить произведение</button>
    </form>
    <p><a href="/admin">← Назад</a></p>
    '''

if __name__ == '__main__':
    app.run(debug=True)
