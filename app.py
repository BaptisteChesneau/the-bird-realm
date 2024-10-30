from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/appointment')
def appointment():
    return render_template('appointment.html')

@app.route('/legal')
def legal():
    return render_template('legal.html')

if __name__ == "__main__":
    app.run(debug=True)
