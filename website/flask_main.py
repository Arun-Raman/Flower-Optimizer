import flask

app = flask.Flask(__name__)


@app.route("/", methods=['GET'])
def index():  # URL: http://
    return flask.redirect(flask.url_for('home'))  # Redirect to home

@app.route("/home", methods=['GET'])
def home():  # URL: http://127.0.0.1:8001/home
    return flask.render_template("")  # insert home template

@app.route("/home", methods=['POST'])
def submit():
    x = flask.request.form[]

    return flask.redirect(flask.url_for('results'))  # Redirect to results

@app.route("/results", methods=['GET', 'POST'])
def results():
    return flask.render_template("")  # insert results template

if __name__ == '__main__':
    # Start the server
    app.run(port=8001, host='127.0.0.1', debug=True, use_evalex=False)
