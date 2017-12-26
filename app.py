from flask import Flask, render_template
from snotel import Snotel

app = Flask(__name__)

STATIONS = [
    '322:CO:SNTL',  # Bear Lake
    '870:CO:SNTL',  # Willow Park
    # '1042:CO:SNTL', # Wild Basin
]
snotels = Snotel(stations=STATIONS)

@app.route('/')
def index():
    return render_template('index.html', snow_depth=snotels.get_snow_depth_range())
