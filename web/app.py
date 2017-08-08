import os
import sys

from flask import Flask, render_template, request

parent = os.path.dirname
sys.path.append(parent(parent(os.path.abspath(__file__))))
from scmpy import InPort, parse, represent, evaluate


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        code = request.form.get('code')
        inport = InPort(code)
        exp = parse(inport)
        val = evaluate(exp)
        result = represent(val)
        return render_template('index.html', result=result)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
