"""
Holds all tests to test all routes in this application

*** NOTE: ***

When running the test need to change the relative imports in:

- `app.py`

    - `utils.helpers` --> `.utils.helpers`
    - `utils.db_model` --> `.utils.db_model`
    - `utils.queries` --> `.utils.queries`

Otherwise the test file will throw an error. However, when running the app
    locally having the `.` at the beginning does not work and throws an error.
    I was unable to fix this bug in the time I had for this challenge.

** Note About Incomplete Test File: **

I will admit that I need to do more learning on testing. I have wrote some
tests on work I have done in the past but they were not as complicated as I
would need to write for this application. I have even taken a beginner course
on TDD. However, I will admit that I am not very efficient in TDD yet but I am
up for the challenge of learning more about it and improving my skills. I
understand the basic concept behind TDD and it makes sense but, being I just
found out about this opening and challenge yesterday, I wanted to make sure I
was able to build out the functionality in the time I had left and still be
able to submit a working application so I could demonstrate my abilities that
I do currently have.
"""
import os
import tempfile
import json

import pytest

from flask import Flask, request
from sqlalchemy import text

from .app import config_routes
from .utils.db_model import db, User, Image
from .utils.queries import get_user_id, dup_user


@pytest.fixture
def client():
    """
    Creates the client needed for each test

    :return:
        client : provides a user interface so you can test a web-based application
    """
    # Initialize the Flask application
    app = Flask(__name__)
    # Call on the function to configure the routes
    config_routes(app)
    # Create the client for testing
    client = app.test_client()

    return client


mock_user1 = {'first': 'Test',
              'last': 'Case',
              'username': 'testuser',
              'password': 'pass1234',
              'confirmation': 'pass1234',
              'email_add': 'testing@gmail.com'
}


def valid(client):
    with client.session_transaction() as sess:
        sess['user_id'] = get_user_id(mock_user1['username'])[0][0]

    return sess


# mock_image1 = {
#     'img': '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',
#     'name': 'Harvard Logo',
#     'img_type': 'png',
#     'public': 0,
#     'owner': 'Harvard University',
#     'user_id': valid(client)
# }


def invalid(client):
    with client.session_transaction() as sess:
        sess['user_id'] = None

    return sess


# # Can not figure out how to get this test to work properly
def test_reg(client):
    # # Could not get this code to delete the test user to work but I can
    # #   get the test to pass if I manually delete the record from the
    # #   database and then run this test. So there is something wrong in
    # #   my code to delete the user if it already exist.
    # if dup_user(mock_user1['username']):
    #     db.engine.execute(
    #         text(
    #             """
    #             DELETE FROM "user"
    #             WHERE "id" = :id;
    #             """
    #         ), id=user_exists[0][0]
    #     )
    #     db.session.commit()

    response = client.post('/register', data=mock_user1,
                           follow_redirects=True)
    assert response.get_data(
        b'Your registration is complete and you have been logged in successfully!'
    )
    assert response.request.path == '/'


def test_home_valid_login(client):
    # Test that we get the proper status code when valid user is logged in
    valid(client)
    response = client.get('/')
    assert response.status_code == 200


def test_home_no_login(client):
    # Test home when no user is logged in
    invalid(client)
    response = client.get('/', follow_redirects=True)
    assert response.request.path == '/login'
    assert response.status_code == 200


def test_edit_act_login(client):
    # Test that we get the proper status code when valid user is logged in
    valid(client)
    response = client.get('/edit_act')
    assert response.status_code == 200


def test_edit_act_no_login(client):
    # Test that we get the proper status code when valid user is logged in
    invalid(client)
    response = client.get('/edit_act', follow_redirects=True)
    assert response.request.path == '/login'
    assert response.status_code == 200


def test_upload_login(client):
    # Test that we get the proper status code when valid user is logged in
    valid(client)
    response = client.get('/upload')
    assert response.status_code == 200


def test_upload_no_login(client):
    # Test that we get the proper status code when valid user is logged in
    invalid(client)
    response = client.get('/upload', follow_redirects=True)
    assert response.request.path == '/login'
    assert response.status_code == 200


# def test_upload(client):
#     valid(client)
#     response = client.post('/upload', data=mock_image1,
#                            follow_redirects=True)
#     assert response.get_data(
#         b'Your Image "Harvard Logo" has been added successfully!'
#     )
#     assert response.request.path == '/'


def test_select_login(client):
    # Test that we get the proper status code when valid user is logged in
    valid(client)
    response = client.get('/select')
    assert response.status_code == 200


def test_select_no_login(client):
    # Test that we get the proper status code when valid user is logged in
    invalid(client)
    response = client.get('/select', follow_redirects=True)
    assert response.request.path == '/login'
    assert response.status_code == 200


def test_all_imgs_login(client):
    # Test that we get the proper status code when valid user is logged in
    valid(client)
    response = client.get('/all_imgs')
    assert response.status_code == 200


def test_all_imgs_no_login(client):
    # Test that we get the proper status code when valid user is logged in
    invalid(client)
    response = client.get('/all_imgs', follow_redirects=True)
    assert response.request.path == '/login'
    assert response.status_code == 200


def test_display_login(client):
    # Test that we get the proper status code when valid user is logged in
    valid(client)
    response = client.get('/display/1')
    assert response.status_code == 200


def test_display_no_login(client):
    # Test that we get the proper status code when valid user is logged in
    invalid(client)
    response = client.get('/display/1', follow_redirects=True)
    assert response.request.path == '/login'
    assert response.status_code == 200


def test_remove_login(client):
    # Test that we get the proper status code when valid user is logged in
    valid(client)
    response = client.get('/remove')
    assert response.status_code == 200


# def test_remove_img(client):
#     valid(client)
#     response = client.post('/remove', data={'name': })


def test_remove_no_login(client):
    # Test that we get the proper status code when valid user is logged in
    invalid(client)
    response = client.get('/remove', follow_redirects=True)
    assert response.request.path == '/login'
    assert response.status_code == 200
