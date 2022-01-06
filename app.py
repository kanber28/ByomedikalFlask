from flask import Flask, flash
from flask import render_template
app = Flask(__name__, template_folder='templates')

app.config.update(
    TESTING=True,
    SECRET_KEY='192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
)
@app.route('/')
def homepage():
    return '<h3>Hello Flask</h3>'


@app.route('/showHtl', methods=['GET', 'POST'])
def showHtml():
    name = "Mustafa"
    flash('Hata!!')
    flash('hata2!!')
    return render_template('index.html', name=name)
