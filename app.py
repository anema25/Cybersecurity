from flask import Flask, request, render_template, redirect
from database import get_db_connection

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


# ======================================================
# 1️⃣ LOGIN (String Concatenation Injection)
# ======================================================
@app.route('/vulnerable/login', methods=['GET', 'POST'])
def login_vulnerable():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        print("Executing:", query)
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()

        if result:
            msg = f"✅ Welcome {username}!"
        else:
            msg = "❌ Invalid credentials"

    return render_template('login_vulnerable.html', msg=msg)


@app.route('/secure/login', methods=['GET', 'POST'])
def login_secure():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        conn.close()

        if result:
            msg = f"✅ Welcome {username}!"
        else:
            msg = "❌ Invalid credentials"

    return render_template('login_secure.html', msg=msg)


# ======================================================
# 2️⃣ SEARCH (Union/Boolean Injection)
# ======================================================
@app.route('/vulnerable/search')
def search_vulnerable():
    term = request.args.get('q', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"SELECT username FROM users WHERE username LIKE '%{term}%'"
    print("Executing:", query)
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return render_template('search_vulnerable.html', term=term, results=results)


@app.route('/secure/search')
def search_secure():
    term = request.args.get('q', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT username FROM users WHERE username LIKE ?"
    cursor.execute(query, (f"%{term}%",))
    results = cursor.fetchall()
    conn.close()
    return render_template('search_secure.html', term=term, results=results)


# ======================================================
# 3️⃣ CRUD DEMO (Create / Read / Update / Delete)
# ======================================================
@app.route('/vulnerable/crud', methods=['GET', 'POST'])
def crud_vulnerable():
    msg = ''
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create
    if 'add' in request.form:
        username = request.form['username']
        password = request.form['password']
        query = f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')"
        print("Executing:", query)
        try:
            cursor.execute(query)
            conn.commit()
            msg = "✅ User added (vulnerable)"
        except Exception as e:
            msg = f"❌ {e}"

    # Delete
    if 'delete' in request.form:
        username = request.form['username']
        query = f"DELETE FROM users WHERE username = '{username}'"
        print("Executing:", query)
        cursor.execute(query)
        conn.commit()
        msg = "✅ User deleted (vulnerable)"

    # Read all
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()

    return render_template('crud_vulnerable.html', users=users, msg=msg)


@app.route('/secure/crud', methods=['GET', 'POST'])
def crud_secure():
    msg = ''
    conn = get_db_connection()
    cursor = conn.cursor()

    if 'add' in request.form:
        username = request.form['username']
        password = request.form['password']
        query = "INSERT INTO users (username, password) VALUES (?, ?)"
        cursor.execute(query, (username, password))
        conn.commit()
        msg = "✅ User added securely"

    if 'delete' in request.form:
        username = request.form['username']
        query = "DELETE FROM users WHERE username = ?"
        cursor.execute(query, (username,))
        conn.commit()
        msg = "✅ User deleted securely"

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template('crud_secure.html', users=users, msg=msg)


# ======================================================
# 4️⃣ Extra Attacks (10 Total)
# ======================================================
@app.route('/vulnerable/update', methods=['POST'])
def update_vulnerable():
    username = request.form['username']
    newpass = request.form['newpass']
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"UPDATE users SET password='{newpass}' WHERE username='{username}'"
    print("Executing:", query)
    cursor.execute(query)
    conn.commit()
    conn.close()
    return redirect('/vulnerable/crud')


@app.route('/secure/update', methods=['POST'])
def update_secure():
    username = request.form['username']
    newpass = request.form['newpass']
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE users SET password=? WHERE username=?"
    cursor.execute(query, (newpass, username))
    conn.commit()
    conn.close()
    return redirect('/secure/crud')


if __name__ == '__main__':
    app.run(debug=True)
