"""
Routes and views for the flask application.
"""

from datetime import datetime
from distutils.log import log
from flask import render_template
from flask import Flask, g
from flask_oidc import OpenIDConnect
from flask import request
from keycloak import KeycloakOpenID
import logging
from ToDoWebProject import app
import pymysql

connection = pymysql.connect(host="localhost", port=3306, user="root", passwd="", database="todo_flask")
cur = connection.cursor()

logging.basicConfig(level=logging.DEBUG)
app.config.update({
    'SECRET_KEY': 'zjMrY9cbKh4UCsvpGOZQ0xkZGuRBNDh3',
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_OPENID_REALM': 'TODO-FLASK',
    'OIDC_SCOPES': ['openid', 'email', 'profile'],
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post'
})
oidc = OpenIDConnect(app)
keycloak_openid = KeycloakOpenID(server_url="http://localhost:8080/",
    client_id="TODO-FLASK",
    realm_name="TODO-FLASK",
    client_secret_key='zjMrY9cbKh4UCsvpGOZQ0xkZGuRBNDh3')
@app.route('/')
@app.route('/home')
@oidc.require_login
def home():
    """Renders the home page."""
    if oidc.user_loggedin:
        cur.execute("SELECT `id`, `title`, `description`, `time` FROM `todo`")

        return render_template(
            'index.html',
            title='Home Page',
            year=datetime.now().year,
            data = cur,
            username= oidc.user_getfield('name')
        )
    else:
        app.route('/logout')

@app.route('/post', methods=['POST'])
def post():
    sql = """INSERT INTO `todo` (`id`, `title`, `description`, `time`, `created_by`, `created_at`, `updated_by`, `updated_at`) VALUES 
    (NULL, %s, %s, %s, %s, current_timestamp(), %s, current_timestamp());
        """
    cur.execute(sql,(request.form['title'],request.form['description'],request.form['time'], oidc.user_getfield('name'), oidc.user_getfield('name')))
    connection.commit()

    cur.execute("SELECT `id`, `title`, `description`, `time` FROM `todo`")
    return render_template(
            'index.html',
            title='Home Page',
            year = datetime.now().year,
            data = cur,
            username= oidc.user_getfield('name')
        )

@app.route('/delete', methods=['GET'])
def delete():
    cur.execute("DELETE FROM `todo` where id ="+ request.args.get("id"))
    connection.commit()
    cur.execute("SELECT `id`, `title`, `description`, `time` FROM `todo`")
    return render_template(
            'index.html',
            title='Home Page',
            year = datetime.now().year,
            data = cur,
            username= oidc.user_getfield('name')
        )


@app.route('/logout')
def logout():
    refresh_token = oidc.get_refresh_token()
    oidc.logout()
    if refresh_token is not None:
        keycloak_openid.logout(refresh_token)
    
    oidc.logout()
    g.oidc_id_token=None
    return 'Hi, you have been logged out! <a href="/">Go to homepage</a>'
