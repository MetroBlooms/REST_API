# Author: Gouthaman Balaraman
# http://gouthamanbalaraman.com/minimal-flask-login-example.html

from flask import Response
from flask.ext.login import LoginManager, UserMixin, login_required
from flask_cors import cross_origin

#app = Flask(__name__)
from rest_api import app

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    # proxy for a database of users
    user_database = {"JohnDoe": ("JohnDoe", "John"),
               "JaneDoe": ("JaneDoe", "Jane")}

    def __init__(self, username, password):
        self.id = username
        self.password = password

    @classmethod
    def get(cls,id):
        return cls.user_database.get(id)


@login_manager.request_loader
def load_user(request):
    token = request.headers.get('X-Auth-Token')
    if token is None:
        token = request.args.get('token')

    print token

    if token is not None:
        username,password = token.split(":") # naive token
        user_entry = User.get(username)
        if (user_entry is not None):
            user = User(user_entry[0],user_entry[1])
            if (user.password == password):
                return user
    return None


@app.route("/",methods=["GET", "ORIGIN"])
@cross_origin()
def index():
    return Response(response="Hello World!",status=200)


@app.route("/protected/",methods=["GET", "ORIGIN"])
@cross_origin()
@login_required
def protected():
    return Response(response="Hello Protected World!", status=200)


if __name__ == '__main__':
    app.config["SECRET_KEY"] = "ITSASECRET"
    app.run(port=5000,debug=True)