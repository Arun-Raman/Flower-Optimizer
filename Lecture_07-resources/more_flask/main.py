import flask
import hashlib
from datetime import datetime
import os


def create_app():
    """Create a Flask application instance. 

    This is a safer way to create the app instance (than in Lecture 06) since it does not run the app on import.
    Creating the app globally can cause issues with the debugger and reloader.
    Global variables (defined outside of a function) are not a good idea in general because they can be changed from anywhere.
    """
    app = flask.Flask(__name__)

    # All the routes are defined in this function as nested functions

    @app.route('/favicon.ico')
    def favicon():
        """Special URL for the favicon.

        By default, the flask will only serve files on the /static endpoint
        A favicon is a graphic image (icon) associated with a particular Web page and/or Web site."""
        return flask.send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @app.route("/", methods=['GET', 'POST'])
    def root():
        """Root URL.

        This is the root of the website. It will redirect to the form."""
        return flask.redirect("/form")

    @app.route("/home", methods=['GET', 'POST'])
    def home():  # URL: http://127.0.0.1:8001/home
        dictionary = {"Hello": "World"}
        return dictionary

    @app.route("/calculate", methods=['POST'])
    def calculate():  # http://127.0.0.1:8001/calculate (will not work as no GET method defined for this API)
        return "Still need to make a calculator!"

    @app.route("/form", methods=['GET', 'POST'])
    def form():
        """Form URL.

        This is the first form that will hash the first name and redirect to the next form."""
        return flask.render_template("form.html")

    @app.route("/form_submit", methods=['POST'])
    def submit_form():
        """Submit Form URL.

        This is the function that will process the first form.
        It will also print the date from the browser and the date from the server."""
        first_name = flask.request.form['fname']
        last_name = flask.request.form['lname']
        date = flask.request.form['date']
        # Print to flask output
        print(f"FirstName {first_name} LastName {last_name}")
        # Get browser time since the standard base time known as "the epoch". This format is known as POSIX time or Unix time.
        print(f'Date in ms: {date}')
        # load in python
        py_date = datetime.fromtimestamp(int(date)/1000.0)
        print(f'Python Date From Browser: {py_date}')
        python_date_now = datetime.now()
        print(f'Python Date Now: {python_date_now}')

        # Hashing example
        # A hash function is any function that can be used to map data of arbitrary size to fixed-size values
        # The values returned by a hash function are called hash values, hash codes, digests, or simply hashes.
        # The values are intended to be unique for each different input (collision-resistant) or at least unique for each different input (pre-image resistance)
        # SHA256 is more secure (256-bits) than MD5 (128-bits) but it is slower to compute.
        # hashed_id = hashlib.sha256(first_name.encode('utf-8')).hexdigest()
        # MD5 is easy to use and fast but it is not secure for passwords because it is easy to crack.
        hashed_id = hashlib.md5(first_name.encode('utf-8')).hexdigest()
        print(f'HashedName {hashed_id}')
        # Redirect to the next form while showing the data from the previous form in a nicer way
        extra_info = {'first_name': first_name, 'last_name': last_name,
                      'date': str(py_date.replace(microsecond=0))}
        return flask.render_template('form2.html', extra_info=extra_info,
                                     hashed_id=hashed_id)

    @app.route("/form2_submit", methods=['POST'])
    def submit_form2():
        """This is the second form that will check if the hashed_id matches the file if the file exists.
        If the file does not exist, it will write the hashed_id to the file."""
        uni = flask.request.form['uni']
        email = flask.request.form['email']
        hashed_id = flask.request.form['hash_id']
        # Print to flask output
        print(uni)
        print(email)
        # Hash uni and hashed_id
        hashed_uni_plus_name = hashlib.md5(
            (hashed_id+uni).encode('utf-8')).hexdigest()
        # Check if the hashed_id matches the file if the file exists
        with open('data/data.txt', 'r+') as file:
            data = file.read()
            if hashed_uni_plus_name == data:
                print("Hashed ID matches")
                matches = True
            else:
                print("Hashed ID does not match")
                matches = False
                # Write the hashed_id to the file if it is empty
                if len(data) == 0:
                    file.write(hashed_uni_plus_name)

        # Hashing example
        # change matches to a string so that it can be used easily in the jinja2 template
        return flask.render_template('thank_you.html', uni=uni, email=email, hashed_id=hashed_id, matches=str(matches).lower())

    @app.route("/loop", methods=['GET', 'POST'])
    def loop():
        """More on Jinja2 loops and JavaScript"""
        data_example = {"Apple": 1, "Banana": 2, "Cherry": 3, "Date": 4}
        list_example = ["Apple", "Banana", "Cherry", "Date"]
        return flask.render_template("jinjaexample.html", data=data_example, data_list=list_example)

    # Remember to return the app instance
    return app


if __name__ == '__main__':
    # Start the server
    app = create_app()
    app.run(port=8001, host='127.0.0.1', debug=True,
            use_evalex=False, use_reloader=False)
