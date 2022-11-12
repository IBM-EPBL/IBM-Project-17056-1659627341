# from flask import Flask,render_template,request,session,redirect,url_for
# from connect import get_db_connection

# from controllers.auth import auth

# app = Flask(__name__)
# app.secret_key = 'abcde'
# con = 0


# @app.route('/')
# def home():
#     if 'auth' in session:
#         if not session['auth']:
#             return redirect(url_for('login'))
#     return render_template("home.html")

# def connection():
#     return con

from web import createApp

if(__name__=="__main__"):
    # con = get_db_connection()
    # app.register_blueprint(auth, url_prefix="/")
    app = createApp()
    app.run(host="0.0.0.0",port=int("5000"),debug=True)