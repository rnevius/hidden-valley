from datetime import datetime
from flask import Flask, render_template
from snotel import Snotel
app = Flask(__name__)
snotels = Snotel()

@app.route('/')
def index():
    return render_template('index.html', snow_depth=snotels.get_range_for_stations())
