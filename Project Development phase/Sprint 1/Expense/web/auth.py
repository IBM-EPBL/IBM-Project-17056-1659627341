from flask import Blueprint, redirect, render_template, url_for, session, request
import ibm_db
from .connect import connection
auth =  Blueprint("auth", __name__, url_prefix="/")
con = connection

@auth.route("/register", methods=['GET','POST'])
def register():
    if(request.method == 'GET'):
        if 'auth' in session:
            if session['auth']:
                return redirect(url_for('feature.dashboard'))
        return render_template("register.html")
    elif(request.method == 'POST'):
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        balance = request.form['balance']
        # TODO: check if account already exist
        qry = "INSERT INTO USER(name,email,password,balance) VALUES(?,?,?,?)"
        stmt = ibm_db.prepare(con,qry)
        ibm_db.bind_param(stmt,1,name)
        ibm_db.bind_param(stmt,2,email)
        ibm_db.bind_param(stmt,3,password)
        ibm_db.bind_param(stmt,4,balance)

        resp2 = ibm_db.execute(stmt)
        print(resp2)

        qry3 = "SELECT * FROM USER WHERE email=?"
        stmt3 = ibm_db.prepare(con,qry3)
        ibm_db.bind_param(stmt3,1,email)
        ibm_db.execute(stmt3)
        resp3=ibm_db.fetch_assoc(stmt3)

        qry2 = "INSERT INTO ACCOUNT(name,balance,acc_no,upi,creditCard,debitCard,cheque,user_id) VALUES(?,?,?,?,?,?,?,?)"
        stmt2 = ibm_db.prepare(con,qry2)
        ibm_db.bind_param(stmt2,1,"Cash")
        ibm_db.bind_param(stmt2,2,balance)
        ibm_db.bind_param(stmt2,3,"00")
        ibm_db.bind_param(stmt2,4,False)
        ibm_db.bind_param(stmt2,5,False)
        ibm_db.bind_param(stmt2,6,False)
        ibm_db.bind_param(stmt2,7,False)
        ibm_db.bind_param(stmt2,8,resp3['USER_ID'])


        resp2 = ibm_db.execute(stmt2)
        return redirect(url_for('auth.login'))
    else:
        return "404 not found"

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if(request.method == 'GET'):
        if 'auth' in session:
            if session['auth']:
                return redirect(url_for('feature.dashboard'))
        return render_template("login.html")
    elif(request.method == 'POST'):
        email=request.form['email']
        password=request.form['password']
        sql="SELECT * FROM USER WHERE email=? AND password=?"
        stmt=ibm_db.prepare(con,sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        resp=ibm_db.fetch_assoc(stmt)
        print("resp - ",resp)


        if resp:
            # qry="SELECT * FROM ACCOUNT WHERE user_id=?"
            # stmt1=ibm_db.prepare(con, qry)
            # ibm_db.bind_param(stmt1,1,resp['USER_ID'])
            # ibm_db.execute(stmt1)
            # resp2=ibm_db.fetch_assoc(stmt1)
            # # print("resp - ",resp2)
            # result = []

            # while resp2 != False:
            #     t = [resp2['NAME'],resp2['BALANCE']]
            #     result.append(t)
            #     resp2 = ibm_db.fetch_assoc(stmt1)

            # print(result)
            
            session['auth'] = True
            session['email'] = email
            session['name'] = resp['NAME']
            session['uid'] = resp['USER_ID']
            # session['rollno'] = rollno
            # create table expense (title varchar(30), description varchar(200), amount varchar(20),accountid int, paymentmode varchar(30), userid int, eid int primary key);
            return redirect(url_for('feature.dashboard'))
        else:
            return redirect(url_for('auth.login'))
    else:
        return "404 not found"


@auth.route('/logout')
def logout():
    session.pop('email',None)
    session.pop('name',None)
    session['auth'] = False
    return redirect(url_for('auth.login'))