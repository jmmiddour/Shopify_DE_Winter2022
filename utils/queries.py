from sqlalchemy import text

from .db_model import db, User, Image


def dup_user(name):
    """
    Look for a duplicate username in the data base

    :param
        name: str: preferred username

    :return:
        bool: True if username already in database; False if not found
    """
    if db.session.query(User.id).filter(User.username == name).count() > 0:
        db.session.close()
        return True

    else:
        return False


def dup_email(email):
    """
    Look for a duplicate email address in the data base

    :param
        email: str: email address entered by user

    :return:
        bool: True if email already in database; False if not found
    """
    if db.session.query(User.email).filter(User.email == email).count() > 0:
        db.session.close()
        return True

    else:
        return False


def add_user(first, last, user, hash_pass, email):
    """
    Add a new user into the user's database table

    :param
        - first     : *str* : user's first name
        - last      : *str* : user's last name
        - user      : *str* : user's preferred username
        - hash_pass : *str* : hashed password for the user's protection
        - email     : *str* : user's email address

    :return:
        Adds new user to the database user table
    """
    new_user = User(first_name=first, last_name=last, username=user,
                    password=hash_pass, email=email)
    db.session.add(new_user)
    db.session.commit()
    db.session.close()


def get_user_id(username):
    """
        Get the row where the username is in the database

        :param
            username: str: user's username

        :return:
            int : row number where the username is in the database
    """
    user = db.engine.execute(
        text("""
        SELECT *
        FROM "user"
        WHERE username = :username;
        """), username=username).all()
    db.session.close()
    return user


def user_details(user_id):
    """
    Query to get current user details from the database

    :param
        - user_id : int : id number of the user currently logged in

    :return:
        list with all the details for given user only
    """
    # Query the database joining the two tables with all the details
    single = db.engine.execute(text(
        """
        SELECT *
        FROM "user" 
        WHERE id = :id;
        """), id=user_id).all()

    # Close the session
    db.session.close()

    # Turn the tuple into a list
    single_list = [i for i in single[0]]

    return single_list


def edit_user(user_dict):
    """
    Query to edit details in the current user's account with all the
        optional parameters available.

    :param
        - user_dict : *dict* : Dictionary with all of the following as its keys:

            - id         : *int* : currently logged in user id
            - first_name : *str* : first name of the user
            - last_name  : *str* : last name of the user
            - username   : *str* : username of the user - can not be changed
            - password   : *str* : hashed user's password
            - email      : *str* : user's email address

    :return:
        Edits only the given parameters in the database
    """
    user = User.query.filter_by(id = user_dict['id']).first()

    user.first_name = user_dict['first_name']
    user.last_name = user_dict['last_name']
    user.password = user_dict['password']
    user.email = user_dict['email']

    # Commit the changes to the database
    db.session.commit()
    # Close the session
    db.session.close()


def dup_img(img_name, user_id):
    """
    Query to verify image name does not already exist

    :param
        - image_name : *str* : the preferred image name to be checked
        - user_id   : *int* : the user id of the user currently logged in

    :return:
        *bool* : True if image name already exists; False if not found
    """
    # Get all project names by the user
    img_names = db.session.query(Image.name).filter(
        Image.user_id == user_id).all()

    db.session.close()

    # Pull out all the names from the tuples and put them in a list
    name = [True for i in img_names if img_name in i]

    # Check if the project name is already used my the user
    return True in name


def get_last_ten(user_id):
    """
    Functionality to query the 10 most recently added projects in a table
    :param
        - user_id : int : id of the user currently logged in to the application
    :return:
        Array with select project details for the 10 most recently added
    """
    rows = db.engine.execute(
        text("""
            SELECT u.first_name, u.last_name, i.name, i.public, i.img_type, i.owner
            FROM "user" u
                JOIN "image" i ON i.user_id = u.id
            WHERE u.id = :user_id
            ORDER BY i.id DESC
            LIMIT 10;
        """), user_id=user_id).all()

    db.session.close()

    return rows


def add_new_image(img_dict: dict):
    """
    Function to add a new image with all the optional parameters available
        for input into the database for recovery later.

    :param
        - img_dict : *dict* : Dictionary with all of the following as its keys:
            - user_id  : *int*  : id number of user currently logged in
            - img      : *str*  : image BLOB data
            - name     : *str*  : name of the image
            - img_type : *str*  : type of image (i.e. jpeg, png, gif, etc.)
            - public   : *bool* : if user will allow image to be publicly displayed
            - owner    : *str*  : who the image was take by or where it came from

    :return:
        Adds all given parameters to the database
    """
    # Create new values to add to the project table based on given parameters
    new_img = Image(user_id=img_dict['user_id'],
                    img=img_dict['img'],
                    name=img_dict['name'],
                    img_type=img_dict['img_type'],
                    public=img_dict['public'],
                    owner=img_dict['owner']
                    )
    # Add the new values to the project table
    db.session.add(new_img)
    # Commit those changes so we can get the new project id number
    db.session.commit()
    db.session.close()


def get_all(user_id):
    """
    Functionality to run the query to get all images for user specified

    :param
        - user_id : int : id of currently signed in user

    :return:
        Array with all products in user account and details
    """
    all_imgs = db.engine.execute(text(
        """
        SELECT *
        FROM "image"
        WHERE user_id = :user_id;
        """), user_id=user_id).all()

    db.session.close()

    return all_imgs


def del_img(img_name, user_id):
    """
    Queries the database to remove a single record with the provide image name

    :param
        - img_name : str : the name of the image record to be removed
        - user_id   : int : id of the user who added the project record

    :return:
        Database with the record removed that had the given id.
    """
    # Get the image id from the parameters given
    img_id = db.engine.execute(
        text("""
        SELECT id
        FROM "image"
        WHERE name = :name AND user_id = :user;
        """), name=img_name, user=user_id).one()

    # Remove the image record from the table
    db.engine.execute(
        text("""
            DELETE FROM "image"
            WHERE id = :id;
            """), id=img_id[0])

    # Commit the changes to the database
    db.session.commit()
    # Close the database session
    db.session.close()
