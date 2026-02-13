from flask import Flask, url_for, render_template, Blueprint

home_bp = Blueprint('home', __name__, static_folder='static', template_folder='templates')

@home_bp.route('/')
@home_bp.route('/home')
def index():
    return render_template('home_index.html')
