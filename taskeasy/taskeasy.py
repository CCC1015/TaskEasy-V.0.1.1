import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g, jsonify

app = Flask(__name__)

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def initialize_database():
    db = get_db()
    cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='goals'")
    table_exists = cursor.fetchone()
    if not table_exists:
        init_db()


@app.route('/')
def home():
    db = get_db()
    cur = db.execute('SELECT * FROM goals')
    goals = cur.fetchall()
    return render_template('index.html', goals=goals)
#@app.route('/')
#def home():
    #db = get_db()
    #cur_incomplete = db.execute('SELECT * FROM goals WHERE completed = 0')
    #incomplete_goals = cur_incomplete.fetchall()
    #cur_complete = db.execute('SELECT * FROM goals WHERE completed = 1')
    #completed_goals = cur_complete.fetchall()
    #return render_template('index.html', incomplete_goals=incomplete_goals, completed_goals=completed_goals)

@app.route('/add_goal', methods=['POST'])
def add_goal():
    goal = request.form.get('goal')
    db = get_db()
    db.execute('INSERT INTO goals (goal) VALUES (?)', (goal,))
    db.commit()
    return redirect(url_for('home'))
    #if not goal or goal.strip() == "":

#@app.route('/complete_goal', methods=['POST'])
#def complete_goal():
    #data = request.get_json()
    #goal_id = data.get('id')
    #db = get_db()
    #db.execute('UPDATE goals SET completed = 1 WHERE id = ?', (goal_id,))
    #db.commit()
    #return jsonify(success=True)

@app.route('/delete_goal', methods=['POST'])
def delete_goal():
    data = request.get_json()
    goal_id = data.get('id')
    db = get_db()
    db.execute('DELETE FROM goals WHERE id = ?', (goal_id,))
    db.commit()
    return jsonify(success=True)



if __name__ == '__main__':
    app.run(debug=True)
