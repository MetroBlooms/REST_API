REST-API
========

REST API for managing BMP evaluation data

Uses Flask, SQLAlchemy and various libraries

## First Time Setup 

### Install And Activate virtualenv

> virtualenv is a tool to create isolated Python environments.
>
> The basic problem being addressed is one of dependencies and versions, and indirectly permissions. Imagine you have an application that needs version 1 of LibFoo, but another application requires version 2. How can you use both these applications? If you install everything into /usr/lib/python2.7/site-packages (or whatever your platform’s standard location is), it’s easy to end up in a situation where you unintentionally upgrade an application that shouldn’t be upgraded.
> 
> https://virtualenv.pypa.io/en/latest/

1. Set current directory to 'REST_API/rest_api'
2. $ virtualenv venv --distribute #install virtualenv
3. $ source venv/bin/activate #activate created virtualenv

### Install App Dependencies

1. Ensure you are running in venv. See above.
2. $ pip install -r ../requirements.txt # ensure all requirements are installed in venv

### Create Database

 $./db_create.py
 
***

## Fabric Usage

> Fabric is a Python (2.5-2.7) library and command-line tool for streamlining the use of SSH for application deployment or systems administration tasks.
> 
> https://www.fabfile.org/

### Show Available Commands
$ fab --list

## Running This App

### With Fab
$ fab api
 
### From Command Line
$ python ./api.py

### Create A User

#### To create a user submit the following:

URL: http://localhost:5000/api/users
Request Header: 
&nbsp;&nbsp;&nbsp;&nbsp;Name: Content-Type
&nbsp;&nbsp;&nbsp;&nbsp;Value: application/x-www-form-urlencoded
Method: POST
Payload: { "username": "new-user-name", "password": "test" }

If the username already exists the server will respond '400 (bad request).

####  To fetch user '5' submit the following

URL: http://localhost:5000/api/users/5
Method: GET
fabz

###  To Send the Password Recovery Email
Note: The only complicated part of this is the baseUrl. When a user gets an email for password recovery they will open the email. Inside they will find a link. 
When they click the link a browser (or app) will open and take then to the password recovery page. The base URL is the just the url
to that page. The base url might look like this:

    http://foo.com/recovery_section/foo?some_key:some_value

The token will be appended like so:

    http://foo.com/recovery_section/foo?some_key:some_value&token=1234i2143uio4321uio4321uio4312


URL: http://localhost:5000/api/sendPasswordRecoveryEmail 
Method: POST
Expected Request JSON: { "emailAdddress": "<usersEmailAddress>", "baseUrl": "<BASE URL TO WHICH WE WILL APPEND SECURE TOKEN>" }
Expected Response (Successful): { "result": "success" }

