from flask import Blueprint, redirect, render_template, url_for, session, request, send_file
import ibm_db
from io import BytesIO
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from datetime import datetime
from .connect import connection
from .email import sendMail
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
                q = "SELECT * from EXPENSE WHERE user_id=? ORDER BY EXP_ID DESC"
                s = ibm_db.prepare(con,q)
                ibm_db.bind_param(s,1,uid)
                ibm_db.execute(s)

                r = ibm_db.fetch_assoc(s)
                expList = []
                while r!=False:
                    li=[r['TITLE'],r['AMOUNT'], r['DATE_TIME'],r['PAYMENT_MODE']]
                    expList.append(li)
                    r = ibm_db.fetch_assoc(s)
                
                # print(expList)

                result = []
                paymentmethods = []
                pay = {}
                total_balance = 0
                while resp2 != False:
                    t = [resp2['NAME'],resp2['BALANCE'],resp2['ACC_NO']]
                    name=resp2['NAME']
                    acno = str(resp2['ACC_NO'])
                    accid = str(resp2['ACC_ID'])
                    session[accid]=resp2['BALANCE']
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
                # print(result)
                # print(pay)
                # print(paymentmethods)
                session['accounts'] = result
                session['balance'] = total_balance
                session['payment'] = paymentmethods
                session['pay'] = pay
                session['expense'] = expList
                return render_template('dashboard.html')
            else:
                return redirect(url_for('auth.login')) 
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

                
                # print(resp2)
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
                category = request.form['category']
                categoryList = ['Food and Drinks','Transportation','Entertainment','Mobile','Investment']
                if category not in categoryList:
                    category = 'Entertainment'

                accdet = paymenttype.split('--')
                accid = accdet[-1]
                paymode = accdet[0]
                uid = session['uid']
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

                currentMonth = datetime.now().month
                currentYear = datetime.now().year

                if float(session[accid])<float(amount):
                    return render_template("dashboard.html", message="Insufficient Funds..Choose different account")

                qry = "INSERT INTO EXPENSE(title,description,amount,payment_mode,date_time,acc_id,user_id,category,month,year) VALUES(?,?,?,?,?,?,?,?,?,?)"

                stmt = ibm_db.prepare(con,qry)
                f = request.files.get('img','')
                
                ibm_db.bind_param(stmt,1,str(title))
                ibm_db.bind_param(stmt,2,description)
                ibm_db.bind_param(stmt,3,amount)
                ibm_db.bind_param(stmt,4,paymode)
                ibm_db.bind_param(stmt,5,dt_string)
                ibm_db.bind_param(stmt,6,accid)
                ibm_db.bind_param(stmt,7,uid)
                ibm_db.bind_param(stmt,8,category)
                ibm_db.bind_param(stmt,9,currentMonth)
                ibm_db.bind_param(stmt,10,currentYear)

                resp = ibm_db.execute(stmt)
                # print(resp)

                qry2 = "UPDATE ACCOUNT SET BALANCE=BALANCE-? WHERE ACC_ID=?"
                # print(qry)

                
                budget = float(session['budget'])
                amt = float(amount)

                if(budget-amt)<=0:
                    message = '''
Hey {0},

Warning!!.. your Expenses have exceeded the planned budget.
Please Plan your future expenses accordingly!
                    
Regards
MyMoney Team

                    '''.format(session['name'])
                    sc = sendMail("Alert Budget Exceeded !!",message,session['email'])
                    # print("Mail STatus : "+str(sc))
                budget-=amt
                session['budget'] = str(budget)

                stmt2 = ibm_db.prepare(con,qry2)
                ibm_db.bind_param(stmt2,1,amount)
                ibm_db.bind_param(stmt2,2,accid)

                resp2 = ibm_db.execute(stmt2)
                # print(resp2)

                return redirect(url_for('feature.dashboard'))
            return redirect(url_for('auth.login'))
        return redirect(url_for('auth.login'))
    return redirect(url_for('auth.login'))


@feature.route('/charts')
def charts():
    if(request.method == 'GET'):
        if 'auth' in session:
            if session['auth']:

                uid = session['uid']

                categoryData=[0,0,0,0,0]
                # categoryData=['0','0','0','0','0']

                qry="SELECT category,SUM(amount) as AMOUNT FROM EXPENSE WHERE USER_ID=? GROUP BY category"

                stmt = ibm_db.prepare(con,qry)

                ibm_db.bind_param(stmt,1,uid)

                resp = ibm_db.execute(stmt)

                var = ibm_db.fetch_assoc(stmt)

                while var!=False:
                    # print(var)

                    if(var['CATEGORY']=='Investment'):
                        categoryData[4]=int(var['AMOUNT'])
                    elif(var['CATEGORY']=='Transportation'):
                        categoryData[1]=int(var['AMOUNT'])
                    elif(var['CATEGORY']=='Entertainment'):
                        categoryData[2]=int(var['AMOUNT'])
                    elif(var['CATEGORY']=='Mobile'):
                        categoryData[3]=int(var['AMOUNT'])
                    elif(var['CATEGORY']=='Food and Drinks'):
                        categoryData[0]=int(var['AMOUNT'])
                    var = ibm_db.fetch_assoc(stmt)

                paymentType = [0,0,0,0,0]
                # paymentType = ['0','0','0','0','0']

                qry1 = "SELECT payment_mode, SUM(AMOUNT) as AMOUNT from EXPENSE WHERE user_id=? GROUP BY payment_mode"

                stmt2 = ibm_db.prepare(con,qry1)

                ibm_db.bind_param(stmt2,1,uid)

                resp2 = ibm_db.execute(stmt2)

                data = ibm_db.fetch_assoc(stmt2)

                while data:

                    # print(data)

                    if(data['PAYMENT_MODE']=='UPI'):
                        paymentType[1] = int(data['AMOUNT'])
                    elif(data['PAYMENT_MODE']=='Cash'):
                        paymentType[0] =int(data['AMOUNT'])
                    elif(data['PAYMENT_MODE']=='Debit Card'):
                        paymentType[2] = int(data['AMOUNT'])
                    elif(data['PAYMENT_MODE']=='Credit Card'):
                        paymentType[3] = int(data['AMOUNT'])
                    elif(data['PAYMENT_MODE']=='Cheque'):
                        paymentType[4] = int(data['AMOUNT'])

                    data= ibm_db.fetch_assoc(stmt2)

                # print(categoryData)
                # print(paymentType)

                qry2 = "SELECT * from EXPENSE WHERE user_id=? ORDER BY EXP_ID DESC"
                # qry2 = "SELECT * FROM EXPENSE WHERE USER_ID=? ORDER BY EXP_ID DESC"

                stmt3 = ibm_db.prepare(con,qry2)

                ibm_db.bind_param(stmt3,1,uid)

                resp3 = ibm_db.execute(stmt3)
                dt = ibm_db.fetch_assoc(stmt3)
                expHistory = []

                while dt:
                    t = []
                    t.append(dt['TITLE'])
                    t.append(dt['AMOUNT'])
                    t.append(dt['CATEGORY'])
                    t.append(dt['PAYMENT_MODE'])
                    t.append(str(dt['DATE_TIME']))

                    expHistory.append(t)

                    dt = ibm_db.fetch_assoc(stmt3)

                # print(expHistory)
                
                return render_template("chart.html",categoryData=categoryData,paymentType=paymentType,expenseHistory=expHistory)
            return redirect(url_for('auth.login'))


@feature.route('/profile', methods=['GET', 'POST'])
def profile():
    if(request.method == 'POST'):
        if 'auth' in session:
            if session['auth']:

                name = request.form['name']
                password = request.form['password']
                budget = request.form['budget']
                uid = session['uid']
                qry = "UPDATE USER SET NAME=?,PASSWORD=?,BUDGET=? WHERE USER_ID=?"

                stmt = ibm_db.prepare(con,qry)

                ibm_db.bind_param(stmt,1,name)
                ibm_db.bind_param(stmt,2,password)
                ibm_db.bind_param(stmt,3,budget)
                ibm_db.bind_param(stmt,4,uid)


                resp = ibm_db.execute(stmt)

                # print(resp)

                session['name'] = name
                session['budget'] = budget
                session['actualBudget']=budget

                return redirect(url_for('feature.dashboard'))
            return redirect(url_for('auth.login'))
        return redirect(url_for('auth.login'))

    elif request.method=='GET':
        return render_template('profile.html')


@feature.route("/pdf")
def pdfGenerator():
    if(request.method == 'GET'):
        if 'auth' in session:
            if session['auth']:    

                qry = "SELECT * FROM EXPENSE WHERE USER_ID=? ORDER BY EXP_ID;"

                stmt = ibm_db.prepare(con,qry)
                uid = session['uid']
                ibm_db.bind_param(stmt,1,uid)

                resp = ibm_db.execute(stmt)

                data = ibm_db.fetch_assoc(stmt)

                result = []

                while data:
                    t = []

                    t.append(data['TITLE'])
                    t.append(data['AMOUNT'])
                    t.append(data['CATEGORY'])
                    t.append(data['PAYMENT_MODE'])
                    t.append(str(data['DATE_TIME'])[:10])

                    result.append(t)

                    data = ibm_db.fetch_assoc(stmt)

                # print(result)

                buffer = create_pdf(result)

                buffer.seek(0)

                return send_file(buffer, as_attachment=True, mimetype='application/pdf',download_name="{name}-report.pdf".format(name=str(session['name'])))

            return redirect(url_for('auth.login'))
        return redirect(url_for('auth.login'))



def create_pdf(expenseList):
    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4)
    WIDTH, HEIGHT = A4
    MARIGIN = 0.5 * cm
    canvas.translate(MARIGIN, HEIGHT-MARIGIN)

    canvas.setFont("Helvetica-Bold", 15)
    canvas.drawString(WIDTH//3+10, 0, "Expense Report")

    canvas.setFont("Helvetica", 12)
    canvas.drawString(430, -0.9*cm, "MyMoney Pvt Ltd")
    canvas.setStrokeGray(0)
    canvas.line(0, -1*cm, WIDTH - 2*MARIGIN, -1*cm)


    canvas.line(0, -26.6*cm, WIDTH - 2*MARIGIN, -26.6*cm)
    canvas.drawString(430, -26.5*cm, "MyMoney Pvt Ltd")

    txt_obj = canvas.beginText(14, -2* cm)
    txt_obj.setFont("Helvetica-Bold", 18)
    txt_obj.setWordSpace(3)
    txt_obj.textOut("Expense information")
    txt_obj.moveCursor(0, 16)
    txt_obj.setFont("Helvetica", 15)
    txt_lst = [ 
                "Name : " + str(session['name']),
                "Email : " + str(session['email']),
                "User ID : " + str(session['uid']),
                "Budget : Rs. " + str(session['actualBudget']),
                "Current Balance : Rs. " + str(session['balance']),
                ]
    for line in txt_lst:
        txt_obj.textOut(line)
        txt_obj.moveCursor(0, 16)
    canvas.drawText(txt_obj)

    canvas.setFont("Helvetica", 15)
    canvas.setFont("Helvetica-Bold", 15)
    canvas.drawString(0, -6.5*cm, "Expense List : ")
    canvas.setFont("Helvetica", 15)
    table_data = [['Paid For', 'Amount( in Rs )', 'Category', 'Payment Mode', 'Date']]

    for e in expenseList:
        table_data.append(e)

    t = Table(table_data, colWidths=[180, 100, 90, 120, 60], rowHeights=30)
    style = [('BACKGROUND',(0,1),(4,(len(table_data))),colors.lightblue),
            ('ALIGN',(0,-1),(-1,-1),'CENTER'),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]
    t.setStyle(tblstyle=style)
    t.wrapOn(canvas, 10, 10)
    t.drawOn(canvas=canvas, x=20, y=-15.5*cm)

    canvas.showPage()
    canvas.save()
    return buffer   