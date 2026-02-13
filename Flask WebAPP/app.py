from flask import Flask, render_template
from blueprints.home.home import home_bp
from blueprints.expression.expression import expression_bp
from blueprints.speech.speech import speech_bp

app = Flask(__name__)

app.register_blueprint(home_bp, url_prefix='/home')
app.register_blueprint(expression_bp, url_prefix='/expression-age')
app.register_blueprint(speech_bp, url_prefix='/speech')

@app.route('/')
def root():
    return render_template('home_index.html')

if __name__=='__main__':
    app.run()