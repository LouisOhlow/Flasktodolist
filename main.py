from flask import Flask, render_template, redirect, g, url_for
from flask_sqlalchemy import *
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, validators
from wtforms.widgets import TextArea
import sqlite3

app = Flask(__name__)
app.secret_key = 'my very secrete key'
app.config['SQLALCHEMY-DATABASE-URI'] = 'C:/Users/Lewis/Desktop/alles/Uni/Semester 3/Informatik 3/Graded2/sql/todos.db'
todo_db = SQLAlchemy(app)
TodoEntries = []
search_mode = False


# connect to the database todos.db
def get_db():
    if not hasattr(g, 'sqlite_db'):
        con = sqlite3.connect('todos.db')
        g.sqlite_db = con
    return g.sqlite_db


class TodoForm(FlaskForm):
    new_title = StringField('title', [validators.Length(min=4, max=25)], widget=TextArea())
    new_desc = StringField('desc', [validators.Length(min=6, max=35)], widget=TextArea())
    new_due = DateField('due', widget=TextArea())


# updates the list TodoEntries by getting the data from the database
def update_entries():
    TodoEntries.clear()
    todo = get_db()
    cur_todo = todo.cursor()
    cur_todo.execute('SELECT * FROM todo')
    rows = cur_todo.fetchall()
    for row in rows:
        checked = 'new'
        if row[3] == 1:
            checked = 'finished'
        TodoEntries.append({'title': row[0],
                            'due': row[1],
                            'description': row[2],
                            'state': checked,
                            })


# updates the index column from the todo table to be in order with the loop index from html
def update_index():
    i = 1
    todo = get_db()
    cur_todo = todo.cursor()
    cur_todo.execute('SELECT * FROM todo')
    rows = cur_todo.fetchall()
    for row in rows:
        cur_todo.execute('UPDATE todo SET indx =? WHERE title=? AND description=? AND due=?', (int(i),
                                                                                               str(row[0]),
                                                                                               str(row[1]),
                                                                                               str(row[2])))
        todo.commit()
        i += 1


# search_mode to decide if every entry or only the searched item should be shown
@app.route('/')
def show_entries():
    global search_mode
    if not search_mode:
        update_entries()
    search_mode = True
    return render_template('layout.html', entries=TodoEntries, form=TodoEntries)


# adds the form to the database and the entrylist
@app.route('/add', methods=['GET', 'POST'])
def add():
    title = request.form['title']
    description = request.form['desc']
    due = request.form['due']
    todo = get_db()
    cur_todo = todo.cursor()

    # saves the data in the table todo
    cur_todo.execute('insert into todo values (?,?,?,?,?)', (str(title),
                                                             str(description),
                                                             str(due),
                                                             0,
                                                             0))
    todo.commit()
    update_index()
    update_entries()
    return redirect('/')


# deletes the entry whose loop index matches the row index from todo
@app.route('/delete')
def delete_entry():
    update_index()
    entry_id = int(request.args.get('id'))
    todo = get_db()
    cur_todo = todo.cursor()
    cur_todo.execute('delete from todo where indx =?', (int(entry_id),))
    todo.commit()
    update_entries()
    update_index()
    return redirect('/')


# updates the TodoEntries list
# so only those will be displayed who contain the searchString
@app.route('/search', methods=['GET', 'POST'])
def search():
    global search_mode
    search_mode = True
    search_string = request.form['searchString']
    local_save = TodoEntries.copy()
    TodoEntries.clear()
    for entry in local_save:
        if search_string in entry.get('title'):
            TodoEntries.append(entry)
    return redirect('/')


@app.route('/changestate')
def change_state():
    update_index()
    entry_id = int(request.args.get('id'))
    todo = get_db()
    cur_todo = todo.cursor()
    cur_todo.execute('SELECT * from todo')
    rows = cur_todo.fetchall()
    for row in rows:
        if row[4] == entry_id and row[3] == 0:
            cur_todo.execute('UPDATE todo SET checked = 1 WHERE indx=?', (int(entry_id),))
        elif row[4] == entry_id and row[3] == 1:
            cur_todo.execute('UPDATE todo SET checked = 0 WHERE indx=?', (int(entry_id),))
    todo.commit()
    update_entries()
    update_index()
    return redirect('/')


app.run(debug=True)
