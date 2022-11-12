from flask import Blueprint, redirect, render_template, url_for, session, request
import ibm_db
from datetime import datetime
from .connect import connection
feature =  Blueprint("feature", __name__, url_prefix="/")
con = connection


@feature.route('/dashboard')
def dashboard():
    if 'auth' in session:
            if session['auth']:
                qry="SELECT * FROM ACCOUNT WHERE user_id=?"
                stmt1=ibm_db.prepare(con, qry)
                ibm_db.bind_param(stmt1,1,session['uid'])
                ibm_db.execute(stmt1)
                resp2=ibm_db.fetch_assoc(stmt1)

                uid = session['uid']
                q = "SELECT * from EXPENSE WHERE user_id=?"
                s = ibm_db.prepare(con,q)
                ibm_db.bind_param(s,1,uid)
                ibm_db.execute(s)

                r = ibm_db.fetch_assoc(s)
                expList = []
                while r!=False:
                    li=[r['TITLE'],r['AMOUNT'], r['DATE_TIME'],r['PAYMENT_MODE']]
                    expList.append(li)
                    r = ibm_db.fetch_assoc(s)
                
                print("expense List")
                print(expList)

                result = []
                paymentmethods = []
                pay = {}
                total_balance = 0
                while resp2 != False:
                    t = [resp2['NAME'],resp2['BALANCE'],resp2['ACC_NO']]
                    name=resp2['NAME']
                    acno = str(resp2['ACC_NO'])
                    accid = str(resp2['ACC_ID'])
                    upi = resp2['UPI']
                    cc = resp2['CREDITCARD']
                    dc = resp2['DEBITCARD']
                    cheque = resp2['CHEQUE']
                    temp = []
                    if upi:
                        temp.append("UPI")
                        paymentmethods.append([name+"-UPI",resp2['ACC_ID']])
                    if cc:
                        temp.append("Credit Card")
                        paymentmethods.append([name+"-Credit",resp2['ACC_ID']])
                    if dc:
                        temp.append("Debit Card")
                        paymentmethods.append([name+"-Debit",resp2['ACC_ID']])
                    if cheque:
                        temp.append("Cheque")
                        paymentmethods.append([name+"-Cheque",resp2['ACC_ID']])
                    if acno=="00":
                        temp.append("Cash")
                    temp.append(accid)
                    pay[name+' - '+acno] = temp
                    total_balance+=float(resp2['BALANCE'])
                    result.append(t)
                    resp2 = ibm_db.fetch_assoc(stmt1)
                print(result)
                print(pay)
                print(paymentmethods)
                session['accounts'] = result
                session['balance'] = total_balance
                session['payment'] = paymentmethods
                return render_template('dashboard.html',pay=pay,expense=expList)
    return redirect(url_for('auth.login'))

@feature.route('/addAccount', methods=['GET','POST'])
def addAccountDetail():
    if(request.method == 'POST'):
        if 'auth' in session:
            if session['auth']:
                
                print(request.form)

                name = request.form['accname']
                accno = request.form['accno']
                balance = request.form['balance']
                upi = True if bool(request.form['upi'] if 'upi' in request.form else False) else False
                cc =  True if bool(request.form['cc'] if 'cc' in request.form else False) else False
                dc = True if bool(request.form['dc'] if 'dc' in request.form else False) else False
                cheque = True if bool(request.form['Cheque'] if 'Cheque' in request.form else False) else False
                uid = session['uid']

                qry2 = "INSERT INTO ACCOUNT(name,balance,acc_no,upi,creditCard,debitCard,cheque,user_id) VALUES(?,?,?,?,?,?,?,?)"
                stmt2 = ibm_db.prepare(con,qry2)
                ibm_db.bind_param(stmt2,1,name)
                ibm_db.bind_param(stmt2,2,balance)
                ibm_db.bind_param(stmt2,3,accno)
                ibm_db.bind_param(stmt2,4,upi)
                ibm_db.bind_param(stmt2,5,cc)
                ibm_db.bind_param(stmt2,6,dc)
                ibm_db.bind_param(stmt2,7,cheque)
                ibm_db.bind_param(stmt2,8,uid)


                resp2 = ibm_db.execute(stmt2)
                
                print(resp2)
                return redirect(url_for('feature.dashboard'))
        return render_template("login.html")
    elif request.method == 'GET':
        return render_template("accountDetails.html")


@feature.route('/addExpense', methods=['GET', 'POST'])
def addExpense():
    if(request.method == 'POST'):
        if 'auth' in session:
            if session['auth']:

                title = request.form['title']
                amount = request.form['price']
                description = request.form['description']
                paymenttype = request.form['paymenttype']

                accdet = paymenttype.split('--')
                accid = accdet[-1]
                paymode = accdet[0]
                uid = session['uid']
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

                print(title," -- ",amount," -- ",description," -- ",accid," -- ",paymode)

                qry = "INSERT INTO EXPENSE(title,description,amount,payment_mode,date_time,acc_id,user_id) VALUES(?,?,?,?,?,?,?)"

                stmt = ibm_db.prepare(con,qry)

                ibm_db.bind_param(stmt,1,str(title))
                ibm_db.bind_param(stmt,2,description)
                ibm_db.bind_param(stmt,3,amount)
                ibm_db.bind_param(stmt,4,paymode)
                ibm_db.bind_param(stmt,5,dt_string)
                ibm_db.bind_param(stmt,6,accid)
                ibm_db.bind_param(stmt,7,uid)

                resp = ibm_db.execute(stmt)
                print(resp)

                qry2 = "UPDATE ACCOUNT SET BALANCE=BALANCE-? WHERE ACC_ID=?"
                print(qry)

                stmt2 = ibm_db.prepare(con,qry2)
                ibm_db.bind_param(stmt2,1,amount)
                ibm_db.bind_param(stmt2,2,accid)

                resp2 = ibm_db.execute(stmt2)
                print(resp2)

                return redirect(url_for('feature.dashboard'))