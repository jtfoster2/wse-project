from venv import create

from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)

# This function utilizes a database.db file if it exists in the root directory, otherwise it should create one with a fields table.
# I wrote this python script before I settled on what the database would "store" for this assignment,
# I didn't want to refactor the entire code, so the table name is staying as generic "field".
def create_db():
    query_qb('''
        CREATE TABLE IF NOT EXISTS fields (
            id INTEGER PRIMARY KEY,
            name TEXT,
            occupation TEXT,
            hire_date TEXT,
            salary NUMERIC,
            employed BOOLEAN
        )
    ''')

# This function handles the SQL queries to the database, so we're not repeating database code across the operations.
# I know in class we were taught MySQL, but I thought sqlite3 was simpler, and a better match for a small flask project. Plus I haven't used it before.
def query_qb(query, params=(), fetch=False):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    if fetch:
        result = cursor.fetchall()
    else:
        result = None
    conn.commit()
    conn.close()
    return result

# Loads the client.html file when the user accesses the hosting URL.
@app.route('/')
def index():
    return render_template('client.html')

# POST Operation; the C in CRUD. When the user hits "add" on the client.html page, this function grabs all the data and submits it to the table.
@app.route('/add', methods=['POST'])
def add_field():
    name = request.form['name']
    occupation = request.form['occupation']
    hire_date = request.form['hire_date']
    salary = request.form['salary']
    employed = request.form['employed'] == 'true'

    query_qb('INSERT INTO fields (name, occupation, hire_date, salary, employed) VALUES (?, ?, ?, ?, ?)',
             (name, occupation, hire_date, salary, employed))

    # Doing a redirect here so the page is automatically refreshed with the new entry showing in the database view.
    return redirect(url_for('index'))

# GET Operation; the R in CRUD. This function is called by the fetch method. On load, it grabs all the data from the 'fields' table and returns it as JSON to display.
@app.route('/fields', methods=['GET'])
def get_fields():
    fields = query_qb('SELECT id, name, occupation, hire_date, salary, employed FROM fields', fetch=True)
    fields = [{'id': row[0], 'name': row[1], 'occupation': row[2], 'hire_date': row[3], 'salary': row[4], 'employed': row[5]} for row in fields]
    return jsonify({'fields': fields})

# PUT Operation; the U in CRUD. Called by the editField, and submitEdit functions. Runs a simple UPDATE query to change the data in the fields table.
# I think I could have combined this function and add_field by using "INSERT OR UPDATE" SQL command, but figured I should keep them separate in this assignment for both simplicity and clarity.
@app.route('/edit/<int:id>', methods=['PUT'])
def edit_field(id):
    data = request.json
    query_qb('UPDATE fields SET name = ?, occupation = ?, hire_date = ?, salary = ?, employed = ? WHERE id = ?',
             (data['name'], data['occupation'], data['hire_date'], data['salary'], data['employed'], id))
    return jsonify({'success': True})

# DELETE Operation; the D in CRUD. Only used by the deleteField function, similar to edit_field, its a simple DELETE query to the fields table.
@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_field(id):
    query_qb('DELETE FROM fields WHERE id = ?', (id,))
    return jsonify({'success': True})

if __name__ == '__main__':
    create_db()
    app.run(debug=True)