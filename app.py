from audioop import add
from pyexpat import model
from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db
import json
import requests
app = Flask(__name__)

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=54a2f15b-5c0f-46df-8954-7e38e612c2bd.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32733;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=xzq90036;PWD=4XGL0Jn7t0mZyb4H",'','')

@app.route('/registration')
def home():
    return render_template('register.html',pred="As a customer of our sevice, you can raise a ticket to bring you issue forward with a detailed description of the problem.Your issues will be assigned to an agent who will take care of it")

@app.route('/register',methods=['POST'])
def register():
    x = [x for x in request.form.values()]
    print(x)
    name=x[0]
    email=x[1]
    phone=x[2]
    city=x[3]
    problem=x[4]
    model=x[5]
    password=x[6]
    desc=x[7]
    sql = "SELECT * FROM ticket WHERE email =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,email)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    print(account)
    if account:
        return render_template('register.html', pred="You are already a member, please login using your details")
    else:
        insert_sql = "INSERT INTO ticket VALUES (?, ?, ?, ?, ?, ?, ?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, name)
        ibm_db.bind_param(prep_stmt, 2, email)
        ibm_db.bind_param(prep_stmt, 3, phone)
        ibm_db.bind_param(prep_stmt, 4, city)
        ibm_db.bind_param(prep_stmt, 5, problem)
        ibm_db.bind_param(prep_stmt, 6, model)
        ibm_db.bind_param(prep_stmt, 7, password)
        ibm_db.bind_param(prep_stmt, 8, desc)
        ibm_db.execute(prep_stmt)
        return render_template('register.html', pred=" Account creation in customer care registry was successful.for raising tickets, login with your email id and password. Thank You")
       
           
@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/adminpage',methods=['POST'])
def adminpage():
    user = request.form['admin']
    passw = request.form['password']
    sql = "SELECT * FROM administration WHERE admin=? AND password=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,user)
    ibm_db.bind_param(stmt,2,passw)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    print (account)
    print(user,passw)
    if account:
            return redirect(url_for('adminstats'))
    else:
        return render_template('admin.html', pred="Login unsuccessful. Incorrect username / password !")
       
            

@app.route('/')    
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/loginpage',methods=['POST'])
def loginpage():
    user = request.form['user']
    passw = request.form['passw']
    sql = "SELECT * FROM ticket WHERE email=? AND password=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,user)
    ibm_db.bind_param(stmt,2,passw)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    print (account)
    print(user,passw)
    if account:
            return redirect(url_for('stats'))
    else:
        return render_template('login.html', pred="Login unsuccessful. Incorrect username / password !") 
      
@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/adminstats')
def adminstats():
    return render_template('adminstat.html',b=5,b1=2,b2=3,b3=4,b4=2,b5=1,b6=2,b7=1,b8=1)    

@app.route('/requester')
def requester():
    return render_template('request.html')


@app.route('/requested',methods=['POST'])
def requested():
    device = request.form['device']
    address = request.form['address']
    print(address)
    sql = "SELECT * FROM ticket WHERE model=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,device)
    ibm_db.execute(stmt)
    data = ibm_db.fetch_assoc(stmt)
    msg = "I am facing issue with my"+device+" phone.My address for communication:"+address
    while data != False:
        print ("The Phone is : ", data["PHONE"])
        url="https://www.fast2sms.com/dev/bulk?authorization=7rnOBao3JNwLfkmMQCItu6RYzgdbKeDsphZ8VGc2140FWHyiSEEDmlW7V6jqxkTzrJORa3HFvdticNnu&sender_id=FSTSMS&message="+msg+"&language=english&route=p&numbers="+str(data["PHONE"])
        result=requests.request("GET",url)
        print(result)
        data = ibm_db.fetch_assoc(stmt)
    return render_template('request.html', pred="Your Complaint is sent to the concerned people.")
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

