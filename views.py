from flask import render_template, flash, redirect, session, jsonify, request
from app import app
from forms import LoginForm


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        #flash('Login requested for Username="%s", remember_me=%s' %
        #       (form.username.data, str(form.remember_me.data)))
        session['username'] = form.username.data
        username = jsonify({'username': session['username']})
        test = request.form['username'] # redirect('/api/TestMe') #form.username.data
        return redirect('/api/TestMe')
    return render_template('login.html',
                           title='Sign In',
                           form=form)