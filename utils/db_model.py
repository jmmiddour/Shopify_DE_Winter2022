from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Create a function to initialize the database and create the tables
def db_init(app):
    db.init_app(app)

    # Create the table if the database does not already exist
    with app.app_context():
        db.create_all()


# Create a table to hold the user data
class User(db.Model):
    """
    Schema for the user table in the database

    Column Descriptions:
        - id         : *int* : auto populated id for each user registered through app
        - first_name : *str* : the first name the user entered when registering
        - last_name  : *str* : the last name the user entered when registering
        - username   : *str* : name the user entered when registering as their username for login
        - password   : *str* : the hashed password the user entered
        - email      : *str* : the users registered email address for forgotten username/password
    """
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String(300), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.first_name


# Create a table to hold all the image data
class Image(db.Model):
    """
    Schema for the image table in the database

    Column Descriptions:
        - id       : *int*  : auto-populated unique number to identify image
        - img      : *str*  : image BLOB data
        - name     : *str*  : name of the image
        - img_type : *str*  : type of image (i.e. jpeg, png, gif, etc.)
        - public   : *bool* : if user will allow image to be publicly displayed
        - owner    : *str*  : who the image was take by or where it came from
    """
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    img_type = db.Column(db.Text, nullable=False)
    public = db.Column(db.BOOLEAN, nullable=False)
    owner = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('image', lazy=True))

    def __repr__(self):
        return '<Image %r>' % self.name
