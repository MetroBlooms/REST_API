#!/usr/bin/env python

# from https://github.com/miguelgrinberg/REST-auth/blob/master/api.py

import os
from flask import Flask, abort, request, jsonify, g, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext import restful

# load extensions
from app import db, app, models

api = restful.Api(app)

auth = HTTPBasicAuth()

# Classes used in API calls
User = models.User
Person = models.Person
Evaluation = models.Evaluation

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

# test JSON for use in APIs
def results():
    results = db.session.query(Person).\
        join(User, User.person_id==Person.id).\
        join(Evaluation, Evaluation.evaluator_id==Person.id)

    json_results = []

    for result in results:
      d = {'username': result.user.username,
            'id': result.id,
            'type': result.type,
            'comment': result.evaluation.comments},
      json_results.append(d)

    return jsonify(items=json_results)


@app.route('/api/test', methods=['GET'])
def stuff():
  if request.method == 'GET':
    json = results()
    return json


class TestMe(restful.Resource):
    def get(self):
        json = results()
        return json

api.add_resource(TestMe, '/api/TestMe')

if __name__ == '__main__':
    # Start app
    app.run(debug=True, use_reloader=True)
