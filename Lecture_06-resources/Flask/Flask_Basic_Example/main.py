import flask

app = flask.Flask(__name__)


@app.route("/", methods=['GET'])
def index():  # URL: http://
    return flask.redirect(flask.url_for('home'))  # Redirect to home

@app.route("/home", methods=['GET', 'POST'])
def home():  # URL: http://127.0.0.1:8001/home
    dictionary = {"Hello": "World"}
    return dictionary


@app.route("/calculate", methods=['POST'])
def calculate():  # http://127.0.0.1:8001/calculate (will not work as no GET method defined for this API)
    return "Still need to make a calculator!"

# @app.route("/calculate", methods=['GET'])
# def calculateget():
#     return "Try making a POST request!"


@app.route("/form", methods=['GET'])
def form():
    return flask.render_template("form.html")


# The same URL can act differntly for a GET or POST method
@app.route("/form", methods=['POST'])
def submit_form():
    # Uses the name of the form element to get the value
    first_name = flask.request.form['firstname']
    last_name = flask.request.form['lastname']
    # Print received info to flask output
    print(f'{first_name=}')
    print(f'{last_name=}')
    # return "Thank you for submitting the form"
    return flask.render_template('thank_you.html',
                                 first_name=first_name,
                                 last_name=last_name)


if __name__ == '__main__':
    # Start the server
    app.run(port=8001, host='127.0.0.1', debug=True, use_evalex=False)
