from flask import Flask, render_template, request, redirect, url_for, flash,session
from flask_mysqldb import MySQL 
import MySQLdb.cursors
from logging import FileHandler,WARNING
import os
from datetime import date
import speech_recognition as sr
from gtts import gTTS
from time import sleep
import os
import pyglet

app = Flask(__name__)
app.secret_key = 'many random bytes'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Sujangb1@'
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


@app.route('/success', methods = ['POST'])
def success():  
    if request.method == 'POST':
        pname = request.form['productname']
        pprice = request.form['productprice']
        cate = request.form['catogery']
        pweight = request.form['productweight']
        des = request.form['description']
        print(pname,pprice,cate,pweight,des)
        f = request.files['file']  
        f.save("static/uploads/" + f.filename)
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("INSERT INTO product (pname ,pprice,cate,pweight,des, pimage ) VALUES (%s, %s,%s,%s,%s,%s)",
                    [pname,pprice,cate,pweight,des,f.filename])
        mysql.connection.commit() 
        cur.close()   
        flash('File(s) successfully uploaded')
        return redirect(url_for('adminindex'))
        
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

@app.route('/addproduct')
def addproduct():
    return render_template('Addproduct.html')


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

            return redirect(url_for('adminindex'))
        else:
            cur = mysql.connection.cursor() 
   
            cur.execute("SELECT  userid,username,password FROM register WHERE username = '%s' AND password = '%s'  "% (username, password))
            data = cur.fetchone()
            uid,uname,password= data
            if utype == 'User':
                session["username"]=uname
                session["userid"]=uid                
                return redirect(url_for('viewproduct'))
            elif data== None:
                return render_template('Login.html')
               
    return render_template('Login.html')


@app.route('/viewcustomer')
def viewcustomer():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM register ")
    data = cur.fetchall()
    cur.close()
    return render_template('ViewCustomer.html', registerlist=data)

@app.route('/proddetailsedit' , methods = ['POST'])
def proddetailsedit():
    result = request.form['result']
    print(result)
    cur = mysql.connection.cursor()
    cur.execute("SELECT  pid, pname,cate,pprice,pweight,des,pimage FROM product where pid = '%s'" % (result))
    data = cur.fetchone()
    pid, pname, cate, pprice, pweight, des ,pimage = data

    return render_template('editProduct.html', pid=pid, pname=pname,cate=cate,pprice=pprice,pweight=pweight,des=des,pimage=pimage)

@app.route('/updateprod' , methods = ['POST'])
def updateprod():
    if request.method == "POST":
        pid = request.form['pid']
        pname = request.form['productname']
        pprice = request.form['productprice']
        cate = request.form['catogery']
        pweight = request.form['productweight']
        des = request.form['description']
        # pimage = request.form['file']

        print(pname, pprice, cate, pweight, des)
        f = request.files['file']
        f.save("static/uploads/" + f.filename)
        cur = mysql.connection.cursor()
        cur.execute("update product set pname=%s , pprice=%s, cate=%s, pweight=%s, des=%s, pimage=%s  where pid=%s",(pname, pprice, cate, pweight, des, f.filename,pid))

        mysql.connection.commit()
        cur.close()
        return redirect(url_for('adminindex'))

@app.route('/proddelete' , methods = ['POST'])
def proddelete():
    result = request.form['result']
    print(result)
    cur = mysql.connection.cursor()
    cur.execute("Delete from product where pid = '%s'" % (result))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('adminindex'))

@app.route('/viewpayment')
def viewpayment():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM payment" )
    data = cur.fetchall() 
    cur.close()
    return render_template('Viewpayment.html', Paymentlist=data)




        
@app.route('/viewfeedback')
def viewfeedback():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM feedback" )
    data = cur.fetchall() 
    cur.close()
    return render_template('Viewfeedback.html',Feedbacklist=data)

@app.route('/adminindex')
def adminindex():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM product ")
    data = cur.fetchall()
    cur.close()

    return render_template('AdminIndex.html', productdata=data)

@app.route('/cancel')
def cancel():
    return render_template('AdminIndex.html' )
if __name__ == "__main__":
    app.run()

#pip install Flask-Session
    
