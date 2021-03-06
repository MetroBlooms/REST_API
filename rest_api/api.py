#!/usr/bin/env python

# from https://github.com/miguelgrinberg/REST-auth/blob/master/api.py

from flask import abort, request, jsonify, g, url_for, session
from forms import LoginForm
from htsql import HTSQL
from htsql.core.fmt.emit import emit
from flask.ext.httpauth import HTTPBasicAuth, HTTPDigestAuth

# test

# load extensions
#from  app import app, db, mb_models as models
from  app import app, s, test_models as models
from flask_cors import cross_origin


auth = HTTPBasicAuth()
#auth = HTTPDigestAuth()

# Classes used in API calls
User = models.User
Person = models.Person
Evaluation = models.Evaluation
#Address = models.Address
Site = models.Site
Geoposition = models.Geoposition
Evaluation = models.Evaluation
Address = models.Address

mode = 'test' # live or test for use in debugging

@app.route("/")
def index():
    return '<a href="/login">Click me to log in!</a>'


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
    #db.session.add(user)
    #db.session.commit()
    s.add(user)
    s.commit()
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
'''
curl -u gms:python -i -X POST http://127.0.0.1:5000/api/resource -H "Content-Type: application/json" -d '{ "site": { "id": "37251", "site_name": "TestSite 2", "address": {
"address": "1235 Blaisdell Ave", "city": "Minneapolis", "state": "MN", "zip":
"55456", "neighborhood": "Kingfield", "county": "Hennepin" }, "geolocation": {
"latitude":  "41.6544", "longitude":  "73.3323", "accuracy": "46" }, "person":
{ "type": "evaluator", "first_name": "you" }, "evaluation": { "comments":
"Another test...", "exists": true } } }
'
'''

@app.route('/api/resource', methods=['GET','POST','OPTIONS'])
@cross_origin() # allow all origins all methods
#@auth.login_required
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
                   exist = evaluation["exists"],
                   evaluator = p)

    st = Site(site_name=site["site_name"],
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

    s.add(a)
    s.add(g)
    s.add(p)
    s.add(e)
    s.add(st)
    s.commit()


    #if mode == 'test':
        #print s.address.count(address) # 1
        #print s.address[0] # <Address object at 0x10c098ed0>
        #print s.address.filter_by(address = address["address"]).count(address) # 1

    # Render template
    return jsonify(json)
    #return jsonify({'data': 'Hello, %s!' % g.user.username})

# test HTSQL
#  & and | for logical operators
@app.route('/api/htsql/', methods=['GET','POST','OPTIONS'])
@cross_origin() # allow all origins all methods
#@auth.login_required
#def get_htsql(criterion):
def get_htsql():
    #if mode == 'test':
    #    print criterion
    test = HTSQL("mysql://gms:test123@localhost/test")
    #test = HTSQL("pgsql://test:test@localhost/test")
    #rows = test.produce("/evaluation{*,site{*,address,geoposition},evaluator}?" + criterion)
    #rows = test.produce("/evaluation{*,site{*,address,geoposition},evaluator}")

    #test = HTSQL("mysql://gms:test@localhost/test")
    #rows = test.produce("/evaluation{site{geoposition},evaluator}")
    rows = test.produce("/evaluation{*,site{*,address,geoposition},evaluator}")

# http://127.0.0.1:8080/evaluation{comments,site{geoposition{id}?latitude=46&longitude%3E47},site{geoposition{accuracy}?latitude=46&longitude%3E47},evaluator{first_name}}?evaluator.first_name='you'/:sql
# http://127.0.0.1:8080/site{site_name :as location, count(evaluation) :as 'N visits'}
# http://127.0.0.1:8080/site{site_name :as location, count(evaluation) :as 'N visits'}?site_name!='Home'
# http://127.0.0.1:8080/person{first_name + ' ' + last_name :as name, count(evaluation) :as 20'N visits'}?count(evaluation)>0

# /evaluation{comments,site{geoposition?accuracy=46.0&latitude%3C42},evaluator{first_name}}?evaluator.first_name='you'
#
# SELECT "evaluation"."comments",
#        "site"."?_1",
#        "site"."?_2",
#        "site"."id_1",
#        "site"."latitude",
#        "site"."longitude",
#        "site"."accuracy",
#        "site"."timestamp",
#        "person_2"."?",
#        "person_2"."first_name"
# FROM "evaluation"
#      LEFT OUTER JOIN "person" AS "person_1"
#                      ON ("evaluation"."evaluator_id" = "person_1"."id")
#      LEFT OUTER JOIN (SELECT TRUE AS "?_1",
#                              "geoposition"."?" AS "?_2",
#                              "geoposition"."id" AS "id_1",
#                              "geoposition"."latitude",
#                              "geoposition"."longitude",
#                              "geoposition"."accuracy",
#                              "geoposition"."timestamp",
#                              "site"."id" AS "id_2"
#                       FROM "site"
#                            LEFT OUTER JOIN (SELECT TRUE AS "?",
#                                                    "geoposition"."id",
#                                                    "geoposition"."latitude",
#                                                    "geoposition"."longitude",
#                                                    "geoposition"."accuracy",
#                                                    "geoposition"."timestamp"
#                                             FROM "geoposition"
#                                             WHERE ("geoposition"."accuracy" = 46.0::FLOAT8)
#                                                   AND ("geoposition"."latitude" < 42.0::FLOAT8)) AS "geoposition"
#                                            ON ("site"."geoposition_id" = "geoposition"."id")) AS "site"
#                      ON ("evaluation"."site_id" = "site"."id_2")
#      LEFT OUTER JOIN (SELECT TRUE AS "?",
#                              "person"."first_name",
#                              "person"."id"
#                       FROM "person") AS "person_2"
#                      ON ("evaluation"."evaluator_id" = "person_2"."id")
# WHERE ("person_1"."first_name" = 'you')
# ORDER BY "evaluation"."id" ASC
    with test:
        text = ''.join(emit('x-htsql/json', rows))

    if mode == 'test':
        print text, rows

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
    #results = db.session.query(Person).\
    results = s.query(Person).\
        join(User, User.person_id==Person.user_id).\
        join(Evaluation, Evaluation.evaluator_id==Person.user_id)

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


# class TestMe(restful.Resource):
@app.route('/api/TestMe', methods=['GET','POST'])
def TestMe():
        #json = results()
        #return json
    #if request.method == 'POST':
    form = LoginForm()
    if request.headers['Content-Type'] == 'text/plain':
        return "Text Message: " + request.data

    return jsonify({'username': session['username']}) #form.username.data})
    #else:
            #return 'Invalid username/password'

#api.add_resource(TestMe, '/api/TestMe')

from flask_mail import Message

@app.route("/api/test_msg")
def test_msg():

    msg = Message("Hello",
                  sender="Me",
                  recipients=[""])

    mail.send(msg)

if __name__ == '__main__':
    # Start app
    app.run(debug=True, use_reloader=True)
