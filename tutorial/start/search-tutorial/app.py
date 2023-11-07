import re
from flask import Flask, render_template, request

app = Flask(__name__)


@app.get('/')
def index():
    return render_template('index.html')


@app.post('/')
def handle_search():
    query = request.form.get('query', '')
    return render_template(
        'index.html', query=query, results=[], from_=0, total=0)


@app.get('/document/<id>')
def get_document(id):
    return 'Document not found'
