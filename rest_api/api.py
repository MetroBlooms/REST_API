#!/usr/bin/env python

# from https://github.com/miguelgrinberg/REST-auth/blob/master/api.py

from flask import abort, request, jsonify, g, url_for, session
from forms import LoginForm
from htsql import HTSQL
from htsql.core.fmt.emit import emit
from flask.ext.httpauth import HTTPBasicAuth, HTTPDigestAuth
from app import app, db, sql_models as models
from flask_cors import cross_origin
# from rest_api.security.email.email_recovery import EmailRecovery
from security.email.email_recovery import EmailRecovery

auth = HTTPBasicAuth()
#auth = HTTPDigestAuth()

# Classes used in API calls
User = models.User
Person = models.Person
Evaluation = models.Evaluation
Address = models.Address
Site = models.Site
Geoposition = models.Geoposition
Evaluation = models.Evaluation
Person = models.Person

mode = 'test' # live or test for use in debugging

@app.route("/")
def index():
    return '<a href="/login">Click me to log in!</a>'

from flask import Response
from flask import jsonify

# NOTE: Must be prevalidated email address
@app.route("/api/sendPasswordRecoveryEmail", methods=['POST'])
def sendPasswordRecoveryEmail():
    emailAddress = request.get_json(force=True)['emailAddress']

    emailRecovery = EmailRecovery()
    emailRecovery.sendEmail(emailAddress)

    result = {
      'result' : 'success'
    }

    resp = jsonify(result)
    resp.status_code = 200

    return resp

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
    username = request.get_json(force=True)['username']
    password = request.get_json(force=True)['password']
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


@app.route('/api/token', methods=['GET','POST','OPTIONS'])
@cross_origin() # allow all origins all methods
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})

# Testing 1, 2, 3....

# test Ajax
@app.route('/api/resource', methods=['GET','POST','OPTIONS'])
@cross_origin() # allow all origins all methods
@auth.login_required
def get_resource():
    # Get the parsed contents of the form data
    # submitted via Ajax request
    json = request.json

    # define dictionary item for entire object
    site = json['site']

    # define address dictionary object
    address = json['site']['address']

    # define geolocation dictionary object
    geolocation = json['site']['geolocation']

    # define person dictionary object
    person = json['site']['person']

    evaluation = json['site']['evaluation']

    # insert into tables
    a = Address(address = address["address"],
                city = address["address"],
                state = address["state"],
                zip = address["zip"],
                neighborhood = address["neighborhood"],
                county = address["county"])

    g = Geoposition(latitude = geolocation["latitude"],
                    longitude = geolocation["longitude"],
                    accuracy = geolocation["accuracy"])

    p = Person(first_name = person["first_name"],
               type = person["type"])

    e = Evaluation(comments = evaluation["comments"],
                   exists = evaluation["exists"],
                   evaluator = p)

    s = Site(site_name=site["site_name"],
             address = a,
             geoposition = g,
             evaluations = [e])


    if mode == 'test':
        # print entire object
        print 'site:'
        print json['site']
        print 'site name:'
        print site["site_name"]
        print 'address:'
        print site['address']
        print address["address"]
        print 'geolocation:'
        print geolocation["accuracy"]
        print 'person:'
        print person["first_name"]
        print 'comments:'
        print evaluation["comments"]

    db.session.add(a)
    db.session.add(g)
    db.session.add(p)
    db.session.add(e)
    db.session.add(s)
    db.session.commit()

    # Render template
    return jsonify(json)

# test HTSQL
#  & and | for logical operators
@app.route('/api/htsql/', methods=['GET','POST','OPTIONS'])
@cross_origin() # allow all origins all methods
def get_htsql():
    test = HTSQL("pgsql://test:test@localhost/test")
    rows = test.produce("/evaluation{*,site{*,address,geoposition},evaluator}")
    with test:
        text = ''.join(emit('x-htsql/json', rows))

    if mode == 'test':
        print text, rows

    return text

# test nested data
@app.route('/api/nested/', methods=['GET','POST','OPTIONS'])
@cross_origin() # allow all origins all methods

def get_nested():
    test = HTSQL("mysql://nester:nesting@localhost/nestedsetspoc")
    rows = test.produce("/clinical_data{id, patient_sid :as sid,string_value :as value,attribute{attribute_value}}")

    with test:
        text = ''.join(emit('x-htsql/json', rows))

    #print text, rows
    return text


# test HTSQL with REST proxy call
@app.route('/api/factor', methods=['GET','POST','OPTIONS'])
@cross_origin() # allow all origins all methods
#@auth.login_required
def get_factor():
    #test = HTSQL("mysql://gms:test@localhost/test")
    test = HTSQL("pgsql://test:test@localhost/test")
    rows = test.produce("/factor")

    with test:
        text = ''.join(emit('x-htsql/json', rows))

    if mode == 'test':
        print text, rows

    return text


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


@app.route('/api/testMe', methods=['GET','POST'])
def TestMe():

    form = LoginForm()
    if request.headers['Content-Type'] == 'text/plain':
        return "Text Message: " + request.data

    return jsonify({'username': form.username.data})

if __name__ == '__main__':
    # Start app
    app.run(debug=True, use_reloader=True)
