from flask import Flask, request, render_template, Response, session, \
    redirect, flash
from flask_session import Session
from tempfile import mkdtemp
from sqlalchemy import text
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from base64 import b64encode

from utils.helpers import apology, login_required
from utils.db_model import db, db_init, Image
from utils.queries import add_user, dup_user, get_user_id, get_last_ten, \
    user_details, edit_user, dup_img, add_new_image, get_all

# Initialize my application
app = Flask(__name__)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_init(app)

# Ensure the templates are auto-reloaded
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configure session to use filesystem (instead of signed cookies)
# Will store the session on the users disk vs digitially signed cookies,
#   which is done by default with Flask
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Set up main route
@app.route('/')
@login_required
def index():
    # Check to make sure the user is already logged in
    if not session.get("user_id"):
        # If the user is not logged in, redirect them to the login page
        return redirect("/login")

    # Get the user's first name from the database
    first = db.engine.execute(text(
        'SELECT first_name FROM "user" WHERE id = :user_id'
    ), user_id=session.get("user_id")).one()

    # Get the dataframe with the list of projects for the user
    last_ten_imgs = get_last_ten(session.get("user_id"))

    # Show the user the index page
    return render_template('index.html', first=first[0], imgs=last_ten_imgs)


# Create the registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Allows the user to register for an account to login to the application.

    The user fills out a form with:
        - first and last name
        - a user name
        - password and confirmation password
        - email address
    """
    # Forget any user_id
    session.clear()

    # If POST is sent as the request method...
    if request.method == "POST":
        first = request.form.get('first')  # Get user's first name
        last = request.form.get('last')  # Get user's last name
        name = request.form.get('username')  # Get user's username
        password = request.form.get('password')  # Get user's password
        conf_pass = request.form.get('confirmation')  # Confirm matching password
        email_add = request.form.get('email_add')  # Get user's email address

        # If the user does not enter a first name...
        if not first:
            return apology("Need to enter a first name.\nPlease try again!")

        # If the user does not enter a last name...
        if not last:
            return apology("Need to enter a last name.\nPlease try again!")

        # If the user does not enter a username...
        if not name:
            return apology("Need to enter a username.\nPlease try again!")

        # If the user did not enter their password twice...
        if not password or not conf_pass:
            return apology(
                "Need to enter your password twice.\nPlease try again!"
            )

        # If the user does not enter an email address...
        if not email_add:
            return apology("Need to enter an email address.\nPlease try again!")

        # If the user's passwords do not match
        if password != conf_pass:
            return apology("Your passwords do not match.\nPlease try again!")

        # If that username is already in the data base
        if dup_user(name):
            return apology(
                "Username already exists.\nLog in or try another username."
            )

        else:
            # Hash the user's password to store in the database
            hashed_pw = generate_password_hash(password)
            # Add the username and hashed password into the user database table
            add_user(first, last, name, hashed_pw, email_add)

            # Get the row where the username is in the data base
            rows = get_user_id(name)
            print(rows)

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(
                    rows[0]["password"], request.form.get("password")
            ):
                return apology("invalid username and/or password", 403)

            # Remember which user has logged in
            # Stores the users "id" in the Flask session by taking the 1 and only
            #   row in the rows list and grabbing the value from the "id" column
            session["user_id"] = rows[0]['id']

            # Display a message on the home page to let the user know their
            #   project was successfully added to the database
            flash(
                f'Your registration is complete and you have been logged in successfully!'
            )
            # Send the user to the portfolio page
            return redirect("/")

    else:  # Otherwise, sent a GET request, need to send to register form
        return render_template('register.html')


# Create login route
@app.route('/login', methods=["GET", "POST"])
def login():
    """
    Log the user into the application
    """
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        row = db.engine.execute(
            text('SELECT * FROM "user" WHERE username = :name'),
            name=request.form.get("username")).all()

        # Ensure username exists and password is correct
        if len(row) != 1 or not check_password_hash(row[0]['password'], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        # Stores the users "id" in the Flask session by taking the 1 and only
        #   row in the rows list and grabbing the value from the "id" column
        session["user_id"] = row[0]["id"]

        # Display a message on the home page to let the user know their
        #   project was successfully added to the database
        flash(f'You have been logged in successfully!')
        # Redirect user to home page
        return redirect('/')

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template('login.html')


# Create a route for the user to logout
@app.route('/logout')
def logout():
    """
    Log user out of the application
    """
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect('/')


# Create a route for editing account information
@app.route('/edit_act', methods=["GET", "POST"])
@login_required
def edit_act():
    """
    Functionality for user to edit their account details
    """
    # Check to make sure the user is already logged in
    if not session.get("user_id"):
        # If not logged in, redirect the user to the login page
        return redirect("/login")

    # Create a dictionary to hold all parameters needed
    user_dict = {
        'id': None,
        'first_name': None,
        'last_name': None,
        'username': None,
        'password': None,
        'email': None
    }

    # Grab the user information from the database
    user = user_details(session.get("user_id"))

    # Iterate through the dictionary to add the values from the database for
    #   the project specified
    i = 0  # Create a counter to increment
    for k, _ in user_dict.items():
        # Change the value in the dictionary to the value at the current location
        user_dict[k] = user[i]
        i += 1  # Increment the index location value by 1

    if request.method == "POST":
        # Iterate through the dictionary of project parameters
        for key, val in user_dict.items():
            if key != 'id' and key != 'username':
                if key == 'password':
                    # Get user's new password
                    password = request.form.get('password')
                    # Confirm matching new password
                    conf_pass = request.form.get('confirmation')

                    # If the user's passwords do not match
                    if password != conf_pass:
                        return apology("Your passwords do not match. Please try again!")

                    # Hash the user's password to store in the database
                    hashed_pw = generate_password_hash(password)

                    # Add new hashed password to user dictionary
                    user_dict['password'] = hashed_pw

                # Get the values from the form if they are different
                elif request.form.get(key) != user_dict[key]:
                    user_dict[key] = request.form.get(key)

                # Otherwise, continue iterating and change nothing
                user_dict[key] = user_dict[key]

        # Add the new project to the database using function from queries.py
        edit_user(user_dict)

        # Display a message on the home page to let the user know their
        #   project was successfully added to the database
        flash(f'Your account has been edited successfully!')
        # Redirect user to the home page
        return redirect('/')

    return render_template('edit_act.html', user=user_dict)


# Set up route to upload image
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # Check to make sure the user is already logged in
    if not session.get("user_id"):
        # If not logged in, redirect the user to the login page
        return redirect("/login")

    # Get the current user id
    user_id = session.get('user_id')

    if request.method == "POST":

        pic = request.files['pic']

        if pic is None:
            return apology('No image was submitted.\nPlease try again.')

        filename = secure_filename(pic.filename)
        img_type = pic.mimetype.split('/')
        print(img_type)

        # If project name is already in the data base
        if dup_img(filename, user_id):
            return apology(
                "This is not a Unique File Name.\nPlease change the file name and try again."
            )

        else:
            public = None

            if request.form.get('public') == 'True':
                public = True

            if request.form.get('public') == 'False':
                public = False

            # Create a dictionary to store details of image upload
            img_dict = {
                'img': pic.read(), 'name': filename, 'img_type': img_type[1],
                'public': public,
                'owner': request.form.get('owner'),
                'user_id': user_id
            }

            # Add the new project to the database using function from queries.py
            add_new_image(img_dict)

            # Display a message on the home page to let the user know their
            #   project was successfully added to the database
            flash(f'Your Image "{filename}" has been added successfully!')
            # Redirect user to the home page
            return redirect('/')

    return render_template('upload.html')


# Create a route to select an image based on name
@app.route('/select', methods=['GET', 'POST'])
@login_required
def select():
    """
    Functionality to display just one image in the users account
    """
    # Check to make sure the user is already logged in
    if not session.get("user_id"):
        # If not logged in, redirect the user to the login page
        return redirect("/login")

    # Create a list of project names for dropdown selection
    images = get_all(session.get("user_id"))
    user_imgs = [row[1] for row in images]

    if request.method == "POST":
        if request.form.get('image') is None:
            return apology(
                'Whoops, You forgot to Select an Image.\n'
                'Please go back and try again.')
        # Get the image id of the selected image
        img_id = db.session.query(Image.id).filter(
            Image.name == request.form.get("image")).one()
        # Redirect user to the edit page
        return redirect(f'/display/{img_id[0]}')

    # If the request method is 'GET' show the form to add a project
    return render_template('select.html', names=user_imgs)


# Create a route for displaying all images currently in database
@app.route('/all_imgs')
@login_required
def all_imgs():
    pass


# Create a route for displaying a single image and details
@app.route('/display/<img_id>')
@login_required
def display(img_id):
    img = Image.query.filter_by(id=img_id).first()

    if not img:
        return apology('No Image has been found with that ID')

    display_img = b64encode(img.img).decode('utf-8')

    return render_template('display.html', image=img, display_img=display_img)


# Create a route to delete an image
@app.route('/remove', methods=['GET', 'POST'])
@login_required
def remove():
    pass


# # Set up route to display image
# @app.route('/<int:id>')
# def get_img(id):
#


# Make it easier to run the application from the terminal
if __name__ == '__main__':
    app.run(debug=True)
