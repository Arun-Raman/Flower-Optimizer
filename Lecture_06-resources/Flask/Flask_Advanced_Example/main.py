import flask
import sqlite3


app = flask.Flask(__name__)


@app.route("/grocery/all", methods=['GET', 'POST'])
def grocery_all(): # URL: http://127.0.0.1:8001/grocery/all
	db_dict = {}
	conn = sqlite3.connect('data/grocery.db')
	c = conn.cursor()
	# Can fetch all the rows matching the query
	fetchall = c.execute("SELECT * from grocery").fetchall()
	for element in fetchall:
		db_dict.update({element[1]: element[2]})
	return db_dict


@app.route("/grocery/alljinja", methods=['GET', 'POST'])
def grocery_alljinja(): # URL:http://127.0.0.1:8001/grocery/alljinja
	db_dict = grocery_all()  # Reusing existing backend code (is a python function)
	print(db_dict)
	db_as_list = list(db_dict.items())  # Convert the dictionary to a list of tuples
	return flask.render_template('jinjaexample.html', data = db_dict, db_as_list = db_as_list)


@app.route("/grocery/view", methods=['GET', 'POST'])
def grocery_display(): # URL:http://127.0.0.1:8001/grocery/view?gcode=101
	"""Example showing arguments to GET request"""
	id = flask.request.args.get('gcode')
	print(f"Received a request for grocery with id {id}")
	# Can redirect and reuse an existing API
	return flask.redirect(f'/grocery/view/{id}')


@app.route("/grocery/view/<gcode>", methods=['GET', 'POST'])
def grocery_display_dynamic(gcode): #URL:http://127.0.0.1:8001/grocery/view/101
	"""Example showing dynamic routing"""
	id = gcode
	print(f"Received a dynamic routing request for grocery with id {id}")
	grocery = fetch_grocery(id)
	message = f"We need {grocery[1]} {grocery[0]} "
	return message


def fetch_grocery(gcode):
	conn = sqlite3.connect('data/grocery.db')
	c = conn.cursor()
	grocery = None
	id = gcode
	# A parameterized query
	grocery = (c.execute("SELECT name,count from grocery where id = ?", (id,)).fetchone())
	# A regular query
	# from sqlite3 import Error as SQLError
	# try:
	# grocery = (c.execute(f"SELECT name,count from grocery where id = {id}").fetchone())
	# except SQLError as e:
	# 	raise SQLError(f"Provide a valid grocery code instead of {gcode}. {e}")
	
	# if grocery is None:
	# 	raise ValueError(f"Grocery with id {id} not found")

	c.close()  # Good practice to close the cursor
	conn.close() # Good practice to close the connection
	return grocery


@app.route("/grocery/add", methods=['GET'])
def grocery_add_form(): #URL:http://127.0.0.1:8001/grocery/add
	"""Example showing a form for adding to the database"""
	return flask.render_template("add.html")

"""Example showing modifying the database via a POST request. 
We do not use GET for modifying the database as it is not safe and is not a good practice. 
This is because GET requests are cached by users and can be bookmarked, 
which can lead to accidental modifications of the database."""


@app.route("/grocery/add", methods=['POST'])
def grocery_add(): 
	"""Example showing modifying the database via a POST request"""
	grocery = flask.request.form['grocery']
	count = flask.request.form['count']
	id = flask.request.form['id']
	print(f"Received a request to add grocery {grocery} with count {count} and id {id}")
	add_grocery(grocery, count, id)
	return f"Added {count} {grocery} to the database with id {id}"


def add_grocery(name, count, id):
	"""Adding to the database"""
	conn = sqlite3.connect('data/grocery.db')
	c = conn.cursor()
	c.execute(f"INSERT INTO grocery (name, count, id) VALUES ('{name}', {count}, {id})")
	c.close()
	# conn.commit()  # Commit the changes since we are modifying the database
	conn.close()


if __name__ == '__main__':
	# Start the server
	app.run(port=8001, host='127.0.0.1', debug=True, use_evalex=False)