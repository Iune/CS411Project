from flask import Flask
from flask import render_template, abort, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', title="Home")

@app.route('/classroom')
def view_classroom():
    return render_template('classroom.html', title="Classroom")


if __name__ == "__main__":
    app.run(debug=True)