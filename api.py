#!/usr/bin/env python

# from https://github.com/miguelgrinberg/REST-auth/blob/master/api.py

import os
from flask import Flask, abort, request, jsonify, g, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
import flask.ext.restless

# load extensions
from app import db, app, models

auth = HTTPBasicAuth()

# Classes used in API calls
User = models.User
Person = models.Person
#TestMe = models.TestMe

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})

# Testing 1, 2, 3....

# Create the Flask-Restless API manager.
restless_manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
restless_manager.create_api(User, methods=['GET', 'POST', 'DELETE'])

# joins in output

@app.route('/api/test', methods=['GET'])
def stuff():
  if request.method == 'GET':
    results = db.session.query(User).join(Person, User.person_id==Person.id)

    json_results = []
    for result in results:
      d = {'username': result.username,
           'id': result.id,
           'type': result.person.type},
      json_results.append(d)

    return jsonify(items=json_results)



#restless_manager.create_api(TestMe, methods=['GET', 'POST', 'DELETE'])


if __name__ == '__main__':
    # Start app
    app.run(debug=True, use_reloader=True)
