import flask
import flask_cors

app = flask.Flask(__name__)
flask_cors.CORS(app, origins=["http://localhost:5173"]) # Allows CORS requests from http://localhost:5173 only (will need to change this URL once the frontend is deployed as an actual site)

@app.route("/", methods=['GET'])
def index():  # URL: http://
    return flask.redirect(flask.url_for('home'))  # Redirect to home

@app.route("/home", methods=['GET'])
def home():  # URL: http://127.0.0.1:8001/home
    return flask.render_template("")  # insert home template

@app.route("/home", methods=['POST'])
def submit():
    # x = flask.request.form[] # Commented this out because it caused an error

    return flask.redirect(flask.url_for('results'))  # Redirect to results

@app.route("/results", methods=['GET', 'POST'])
def results():
    return flask.render_template("")  # insert results template

@app.route("/test", methods=['GET']) # Basic endpoint which returns a string for GET requests to /test
def test():
    return "hello from the backend"

if __name__ == '__main__':
    # Start the server
    app.run(port=8001, host='127.0.0.1', debug=True, use_evalex=False)
