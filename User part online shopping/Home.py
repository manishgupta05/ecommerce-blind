from flask import Flask, render_template, request, redirect, url_for, flash,session
from flask_mysqldb import MySQL 
import MySQLdb.cursors
from logging import FileHandler,WARNING
import os
from datetime import date
import speech_recognition as sr
from flask import *

from gtts import gTTS
from time import sleep
import os
import pyglet


app = Flask(__name__)
app.secret_key = 'many random bytes'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'P@ssW0rd'
app.config['MYSQL_DB'] = 'Shopping'
#app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
  
def allowed_file(filename):
 return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
fh=FileHandler('errorlog.txt')
fh.setLevel(WARNING)

app.logger.addHandler(fh)


mysql = MySQL(app)
app.secret_key = os.urandom(24)


@app.route('/signup')
def signup():     
    today = date.today()
    cur = mysql.connection.cursor()
    cur.execute("select MAX(userid) from Register")
    data = cur.fetchone()
    uid=data[0]
    print(uid)
    if uid==None:
            uid="1" 
    else:         
         uid=uid+1      
    return render_template('Signup.html',uid=uid,today=today )


@app.route('/insert', methods = ['POST'])
def insert():
    if request.method == "POST":        
        try:
            name = request.form['name']
            mail = request.form['mail']
            mobile = request.form['mobile']
            currentdate = date.today()
            username = request.form['username']
            password = request.form['password']
            address = request.form['address']
            
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO register (name, mail, mobile,currentdate,username,password,address) VALUES (%s, %s, %s,%s,%s,%s,%s)", (name, mail, mobile,currentdate,username,password,address))

            mysql.connection.commit()
            flash("Data Inserted Successfully")      
            return redirect(url_for('login'))
        except (Exception) as e:
            return render_template('signup.html')

        
@app.route('/')
def index():  
    return render_template('index.html' ) 
 
@app.route('/login')
def login():
    txt='New technology and techniques are implemented . Login to Shopping '
    tts = gTTS(text=txt, lang='en')
    filename = 'temp.mp3'
    tts.save(filename)  
    music = pyglet.media.load(filename, streaming=False)
    music.play()

    sleep(music.duration) #prevent from killing
    os.remove(filename) #remove temperory file
    return render_template('login.html' )

@app.route('/logout')
def logout():
     txt='New technology and techniques are implemented . Thank You for coming'
     tts = gTTS(text=txt, lang='en')
     filename = 'temp.mp3'
     tts.save(filename)
     music = pyglet.media.load(filename, streaming=False)
     music.play()

     sleep(music.duration) #prevent from killing
     os.remove(filename) #remove temperory file
     return render_template('login.html' )


@app.route('/checklogin', methods = ['POST'])
def checklogin():
    if request.method == 'POST':
        
        username = request.form['username']
        password = request.form['password']
        utype=request.form['utype']
        
        if username=='Admin' and password=='Admin' and utype=="Admin":
            session["username"]="Admin"
            return render_template('addproduct.html')
        else:
            cur = mysql.connection.cursor() 
   
            cur.execute("SELECT  userid,name,username,password FROM register WHERE username = '%s' AND password = '%s'  "% (username, password))
            data = cur.fetchone()
            uid,name,uname,password= data
            if utype == 'User':
                session["username"]=uname
                session["name"]=name
                session["userid"]=uid                
                return redirect(url_for('viewproduct'))
            elif data== None:
                return render_template('Login.html')
               
    return render_template('Login.html')


@app.route('/viewproduct')
def viewproduct():
    name=session["name"]
    txt=name + 'Welcome. Here ia all Product are showing, select your Product'
    tts = gTTS(text=txt, lang='en')
    filename = 'temp.mp3'
    tts.save(filename)  
    music = pyglet.media.load(filename, streaming=False)
    music.play()

    sleep(music.duration) #prevent from killing
    os.remove(filename) #remove temperory file

    # r = sr.Recognizer()
    # mic = sr.Microphone()
    #
    # print('Which Category you want  ? ')
    # with mic as source:
    #     audio = r.listen(source)
    #
    # print(r.recognize_google(audio))
    # if r:
    #     tts = gTTS(text=r.recognize_google(audio) , lang='en')
    #     filename = 'temp.mp3'
    #     tts.save(filename)
    #     cat=r.recognize_google(audio)
    #     print(cat)
    #     music = pyglet.media.load(filename, streaming=False)
    #     music.play()
    #
    #     sleep(music.duration) #prevent from killing
    #     os.remove(filename) #remove temperory file
    #     print('Ok')
        
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM product")
    data = cur.fetchall()
    cur.close()
                      
    return render_template('viewproduct.html' , productlist=data,u=name)

@app.route('/viewcart')
def viewcart():
    name = session["name"]
    uname = session["username"]
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT cpid, cpname, ccate,cpprice,cpweight,cdes,cpimage from addcart where cuname = '%s'" %(uname))
    data = cur.fetchall()
    cur.close()
    if data != ():
        print(data)
        return render_template('viewcartitem.html', productlist=data,u=name)
    else:
        return render_template('cartempty.html',u=name)

@app.route('/filterprod', methods = ['POST'])
def filterprod():
    name = session["name"]
    from1 = request.form['from']
    to1 = request.form['to']
    cur = mysql.connection.cursor()
    if from1 != "" and to1 != "":
        cur.execute("SELECT  * FROM product where pprice>='%s' and pprice<='%s' "% (from1,to1))
    else:
        cur.execute("SELECT  * FROM product ")
    data = cur.fetchall() 
    cur.close()
    if data!=():
        return render_template('viewproduct.html' , productlist=data,u=name)
    else:
        return render_template('filterempty.html',u=name)


@app.route('/viewcatagoryby',methods = ["POST","GET"])
def viewcatagoryby():
    name = session["name"]
    if request.method == "POST":
        check = request.form['hdnbt']
        print(check)
        uname = session["username"]
        txt = 'You chooses  Category please select your Product'
        tts = gTTS(text=txt, lang='en')
        filename = 'temp.mp3'
        tts.save(filename)
        music = pyglet.media.load(filename, streaming=False)
        music.play()

        sleep(music.duration)  # prevent from killing
        os.remove(filename)  # remove temperory file

        cur = mysql.connection.cursor()
        cur.execute("SELECT  * FROM product where cate = '%s' "%(check))
        data = cur.fetchall()
        cur.close()

        return render_template('viewproduct.html', productlist=data,u=name)



@app.route('/proddetails' , methods = ['POST'])
def proddetails():
    result = request.form['result']
    print(result)
    if result != "":
        cur = mysql.connection.cursor()
        cur.execute("SELECT  pid, pname,cate,	pprice,	pweight,des FROM product where pid = '%s'" % (result))
        data = cur.fetchone()
        pid, pname, cate, pprice, pweight, des = data
        det = "You have selected " + pname + " Price is " + str(pprice) + "  Weight is : " + pweight + " and " + des
        print(data)
        tts = gTTS(text=det, lang='en')
        filename = 'temp.mp3'
        tts.save(filename)

        music = pyglet.media.load(filename, streaming=False)
        music.play()
        sleep(music.duration)  # prevent from killing
        os.remove(filename)  # remove temperory file
        print("start")
        session["pid"] = pid
        print(pid)
        return redirect(url_for('addpayment'))

@app.route('/prodadd' , methods = ['POST'])
def prodadd():
    uname = session["username"]
    result = request.form['result']
    print(result)
    cur = mysql.connection.cursor()
    cur.execute("SELECT  pid, pname,cate,pprice,pweight,des,pimage FROM product where pid = '%s'" % (result))
    data = cur.fetchone()
    pid, pname, cate, pprice, pweight, des ,pimage = data

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO addcart (cpid, cpname, ccate,cpprice,cpweight,cdes,cpimage,cuname) VALUES (%s, %s, %s,%s,%s,%s,%s,%s)",
        (pid, pname, cate, pprice, pweight, des ,pimage, uname))
    mysql.connection.commit()
    flash("Product Added Successfully")
    det = "Your Product Added to cart successfully"
    tts = gTTS(text=det, lang='en')
    filename = 'temp.mp3'
    tts.save(filename)
    music = pyglet.media.load(filename, streaming=False)
    music.play()

    sleep(music.duration)  # prevent from killing
    os.remove(filename)  # remove temperory file
    print(det)
    return redirect(url_for('viewproduct'))

@app.route('/addpayment')
def addpayment():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  pid, pname,cate,pprice,pweight,des FROM product where pid = '%s'" % (session["pid"]))
    data = cur.fetchone()
    pid, pname,cate,pprice,	pweight,des =data
    
    today = date.today()
    tax=pprice*12/100
    
    return render_template('AddPayment.html', today=today, username=session["username"], pid=pid, pname=pname,pprice=pprice,tax=tax,total=tax+pprice)

@app.route('/insertpayment', methods = ['POST'])
def insertpayment():
    if request.method == "POST":        
        try:
            uname = session["username"]
            Paymentdate = request.form['Paymentdate']
            userid=request.form['userid']
            prodid = request.form['prodid']
            prodname = request.form['prodname']
            
            amount  = request.form['amount']
            tax = request.form['tax']
            total = request.form['total']
            paytype = request.form['paytype']
            bankname = request.form['bankname']
            
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO payment (Paymentdate, prodid, prodname,userid,amount,tax,total,paytype,bankname) VALUES (%s, %s, %s,%s,%s,%s,%s,%s,%s)",
                        (Paymentdate, prodid, prodname,userid,amount,tax,total,paytype,bankname))


            flash("Data Inserted Successfully")
            det="Thank you for shopping"
            tts = gTTS(text=det, lang='en')
            filename = 'temp.mp3'
            tts.save(filename)  
            music = pyglet.media.load(filename, streaming=False)
            music.play()
            sleep(music.duration) #prevent from killing
            os.remove(filename) #remove temperory file
            # adding in order list
            cur = mysql.connection.cursor()
            cur.execute("SELECT  pid, pname,cate,pprice,pweight,des,pimage FROM product where pid = '%s'" % (prodid))
            data = cur.fetchone()
            pid, pname, cate, pprice, pweight, des, pimage = data

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO orderlist (opid, opname, ocate,opprice,opweight,odes,opimage,ouname) VALUES (%s, %s, %s,%s,%s,%s,%s,%s)",
                (pid, pname, cate, pprice, pweight, des, pimage, uname))
            mysql.connection.commit()
            print(det)
            return redirect(url_for('feedback'))
        except (Exception) as e:
            return redirect(url_for('addpayment'))

@app.route('/orderlist')
def orderlist():
    name = session["name"]
    uname = session["username"]
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from orderlist where ouname = '%s'" % (uname))
    data = cur.fetchall()
    cur.close()
    if data!=():
        return render_template('vieworderitem.html', productlist=data,u=name)
    else:
        return render_template('orderempty.html',u=name)

# this process from cart item..

@app.route('/proddetailscart' , methods = ['POST'])
def proddetailscart():
    result = request.form['result']
    print(result)
    if result != "":
        cur = mysql.connection.cursor()
        cur.execute("SELECT  pid, pname,cate,	pprice,	pweight,des FROM product where pid = '%s'" % (result))
        data = cur.fetchone()
        pid, pname, cate, pprice, pweight, des = data
        det = "You have selected " + pname + " Price is " + str(pprice) + "  Weight is : " + pweight + " and " + des
        print(data)
        tts = gTTS(text=det, lang='en')
        filename = 'temp.mp3'
        tts.save(filename)

        music = pyglet.media.load(filename, streaming=False)
        music.play()
        sleep(music.duration)  # prevent from killing
        os.remove(filename)  # remove temperory file
        print("start")
        session["pid"] = pid
        print(pid)
        return redirect(url_for('addpaymentcart'))


@app.route('/addpaymentcart')
def addpaymentcart():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  pid, pname,cate,pprice,pweight,des FROM product where pid = '%s'" % (session["pid"]))
    data = cur.fetchone()
    pid, pname, cate, pprice, pweight, des = data

    today = date.today()
    tax = pprice * 12 / 100

    return render_template('AddPaymentcart.html', today=today, username=session["username"], pid=pid, pname=pname,
                           pprice=pprice, tax=tax, total=tax + pprice)


@app.route('/insertpaymentcart', methods=['POST'])
def insertpaymentcart():
    name = session["name"]
    name = session["username"]
    if request.method == "POST":
        try:
            Paymentdate = request.form['Paymentdate']
            userid = request.form['userid']
            prodid = request.form['prodid']
            prodname = request.form['prodname']

            amount = request.form['amount']
            tax = request.form['tax']
            total = request.form['total']
            paytype = request.form['paytype']
            bankname = request.form['bankname']

            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO payment (Paymentdate, prodid, prodname,userid,amount,tax,total,paytype,bankname) VALUES (%s, %s, %s,%s,%s,%s,%s,%s,%s)",
                (Paymentdate, prodid, prodname, userid, amount, tax, total, paytype, bankname))

            mysql.connection.commit()

            # adding in order list
            cur = mysql.connection.cursor()
            cur.execute("SELECT  pid, pname,cate,pprice,pweight,des,pimage FROM product where pid = '%s'" % (prodid))
            data = cur.fetchone()
            pid, pname, cate, pprice, pweight, des, pimage = data

            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO orderlist (opid, opname, ocate,opprice,opweight,odes,opimage,ouname) VALUES (%s, %s, %s,%s,%s,%s,%s,%s)",
                (pid, pname, cate, pprice, pweight, des, pimage, name))
            mysql.connection.commit()

            # flash("Data Inserted Successfully")
            det = "Thank you for shopping"
            tts = gTTS(text=det, lang='en')
            filename = 'temp.mp3'
            tts.save(filename)
            music = pyglet.media.load(filename, streaming=False)
            music.play()

            sleep(music.duration)  # prevent from killing
            os.remove(filename)  # remove temperory file
            print(det)

            cur = mysql.connection.cursor()
            cur.execute("Delete from addcart where cpid = '%s' and cuname = '%s'" % (prodid,name))
            mysql.connection.commit()
            cur.close()

            return redirect(url_for('viewproduct'))
        except (Exception) as e:
            return redirect(url_for('addpayment'))

@app.route('/deletecartitem' , methods = ['POST'])
def deletecartitem():
    name = session["username"]
    result = request.form['result']
    print(result)
    cur = mysql.connection.cursor()
    cur.execute("Delete from addcart where cpid = '%s' and cuname = '%s'" % (result, name))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('viewproduct'))
#*************************************************************


@app.route('/feedback')
def feedback():     
    today = date.today()    
    return render_template('Addfeedback.html',uid=session["userid"],today=today )

@app.route('/insertfeedback', methods = ['POST'])
def insertfeedback():
    if request.method == "POST":        
        try:
            today = request.form['today']
            userid=request.form['userid']
            rating = request.form['rating']
            review = request.form['review']
            
            print(today, userid,  rating,review)
            
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO feedback(fdate, userid, rating,review) VALUES (%s, %s, %s,%s)",
                        (today, userid, rating,review))

            mysql.connection.commit()
            flash("Data Inserted Successfully")
            det="Thank you for feedback"
            tts = gTTS(text=det, lang='en')
            filename = 'temp.mp3'
            tts.save(filename)  
            music = pyglet.media.load(filename, streaming=False)
            music.play()

            sleep(music.duration) #prevent from killing
            os.remove(filename) #remove temperory file    
            print(det)
            return redirect(url_for('viewproduct'))
        except (Exception) as e:
            return redirect(url_for('feedback'))


if __name__ == "__main__":
    app.run()

#pip install Flask-Session
    
