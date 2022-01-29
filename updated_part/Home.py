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
app.config['MYSQL_PASSWORD'] = ''
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

@app.route('/adminsignin')
def adminsignin():

    return render_template('adminsignin.html')

@app.route('/insert', methods=['POST'])
def insert():
    if request.method == "POST":
        try:
            fname = request.form['fname']
            lname = request.form['lname']
            email = request.form['email']
            currentdate = date.today()
            mobile = request.form['mobile']

            password = request.form['password']
            address = request.form['address']

            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO register (fname,lname, email, currentdate,mobile,password,address) VALUES (%s,%s, %s, %s,%s,%s,%s)",
                (fname, lname, email, currentdate, mobile, password, address))

            mysql.connection.commit()
            flash("Data Inserted Successfully")
            return redirect(url_for('login'))
        except (Exception) as e:
            return render_template('login.html')

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
    return render_template('newindex.html' )
 
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

        email = request.form['email']
        password = request.form['password']


        if email=='admin@dshop.com' and password=='Admin1@' :
            session["email"]="Admin"
            return redirect(url_for('adminindex'))
        else:
            cur = mysql.connection.cursor()

            cur.execute("SELECT  userid,fname,email,password FROM register WHERE email = '%s' AND password = '%s'  "% (email, password))
            data = cur.fetchone()
            uid,fname,email,password = data

            session["fname"]=fname
            session["email"]=email
            session["userid"] = uid
            return redirect(url_for('viewproduct'))

    return render_template('login.html')


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


@app.route('/contact', methods=['POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        print(name, email, message)
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("INSERT INTO contact (name ,email,message) VALUES (%s, %s,%s)",( name, email, message))
        mysql.connection.commit()
        cur.close()
        flash("Data Inserted Successfully")
        return render_template('newindex.html' )

@app.route('/viewapplication')
def viewapplication():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM Applicationfeedback" )
    data = cur.fetchall()
    cur.close()
    return render_template('viewapplication.html',Applicationlist=data)

@app.route('/appfeedback')
def appfeedback():
    return render_template('Addappfeedback.html')

@app.route('/insertApplicationfeedback', methods=['POST'])
def insertApplicationfeedback():
    if request.method == "POST":
        try:
            ser_rating = request.form['ser_rating']
            offer_satisfied= request.form['offer_satisfied']
            rating_price = request.form['rating_price']
            order_delivery = request.form['order_delivery']
            customer_support = request.form['customer_support']
            Recommend_product = request.form['Recommend_product']
            review= request.form['review']
            Email = request.form['Email']

            print(ser_rating,offer_satisfied,rating_price,order_delivery,customer_support,Recommend_product,review,Email)
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO Applicationfeedback(ser_rating,offer_satisfied,rating_price,order_delivery,customer_support,Recommend_product,review,Email) VALUES (%s, %s, %s,%s,%s,%s,%s,%s)",
                        (ser_rating,offer_satisfied,rating_price,order_delivery,customer_support,Recommend_product,review,Email))
            mysql.connection.commit()
            flash("Data Inserted Successfully")
            det = "Thank you for feedback"
            tts = gTTS(text=det, lang='en')
            filename = 'temp.mp3'
            tts.save(filename)
            music = pyglet.media.load(filename, streaming=False)
            music.play()
            sleep(music.duration)  # prevent from killing
            os.remove(filename)  # remove temperory file
            print(det)
            return render_template('newindex.html')
        except (Exception) as e:
            return redirect(url_for('appfeedback'))


@app.route('/userappfeedback')
def userappfeedback():
    fname = session["fname"]

    return render_template('userAddappfeedback.html',u=fname)

@app.route('/userinsertfeedback', methods=['POST'])
def userinsertfeedback():
    if request.method == "POST":
         try:
            ser_rating = request.form['ser_rating']
            offer_satisfied = request.form['offer_satisfied']
            rating_price = request.form['rating_price']
            order_delivery = request.form['order_delivery']
            customer_support = request.form['customer_support']
            Recommend_product = request.form['Recommend_product']
            review = request.form['review']
            Email = request.form['Email']

            print(ser_rating, offer_satisfied, rating_price, order_delivery, customer_support, Recommend_product,
                      review, Email)
            cur = mysql.connection.cursor()
            cur.execute(
                    "INSERT INTO Applicationfeedback(ser_rating,offer_satisfied,rating_price,order_delivery,customer_support,Recommend_product,review,Email) VALUES (%s, %s, %s,%s,%s,%s,%s,%s)",
                    (ser_rating, offer_satisfied, rating_price, order_delivery, customer_support, Recommend_product,
                     review, Email))
            mysql.connection.commit()
            flash("Data Inserted Successfully")
            det = "Thank you for feedback"
            tts = gTTS(text=det, lang='en')
            filename = 'temp.mp3'
            tts.save(filename)
            music = pyglet.media.load(filename, streaming=False)
            music.play()
            sleep(music.duration)  # prevent from killing
            os.remove(filename)  # remove temperory file
            print(det)
            return redirect(url_for('viewproduct'))
         except (Exception) as e:
            return redirect(url_for('userappfeedback'))


        # ***********************
#user part
@app.route('/contactus')
def contactus():
    fname = session["fname"]

    return render_template('help.html',u=fname)

@app.route('/contacthelp', methods=['POST'])
def contacthelp():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        print(name, email, message)
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("INSERT INTO contact (name ,email,message) VALUES (%s, %s,%s)",( name, email, message))
        mysql.connection.commit()
        cur.close()
        flash("Data Inserted Successfully")
        return redirect(url_for('viewproduct'))


@app.route('/viewproduct')
def viewproduct():
    fname = session["fname"]
    txt = fname + 'Welcome. Here ia all Product are showing, select your Product'
    tts = gTTS(text=txt, lang='en')
    filename = 'temp.mp3'
    tts.save(filename)
    music = pyglet.media.load(filename, streaming=False)
    music.play()

    sleep(music.duration)  # prevent from killing
    os.remove(filename)  # remove temperory file

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

    return render_template('viewproduct.html', productlist=data, u=fname)


@app.route('/viewcart')
def viewcart():
    fname = session["fname"]
    uname = session["email"]
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT DISTINCT cpid, cpname, ccate,cpprice,cpweight,cdes,cpimage from addcart where cuname = '%s'" % (uname))
    data = cur.fetchall()
    cur.close()
    if data != ():
        print(data)
        return render_template('viewcartitem.html', productlist=data, u=fname)
    else:
        return render_template('cartempty.html', u=fname)


@app.route('/filterprod', methods=['POST'])
def filterprod():
    fname = session["fname"]
    from1 = request.form['from']
    to1 = request.form['to']
    cur = mysql.connection.cursor()
    if from1 != "" and to1 != "":
        cur.execute("SELECT  * FROM product where pprice>='%s' and pprice<='%s' " % (from1, to1))
    else:
        cur.execute("SELECT  * FROM product ")
    data = cur.fetchall()
    cur.close()
    if data != ():
        return render_template('viewproduct.html', productlist=data, u=fname)
    else:
        return render_template('filterempty.html', u=fname)


@app.route('/viewcatagoryby', methods=["POST", "GET"])
def viewcatagoryby():
    fname = session["fname"]
    if request.method == "POST":
        check = request.form['hdnbt']
        print(check)
        # uname = session["email"]
        txt = 'You chooses  Category please select your Product'
        tts = gTTS(text=txt, lang='en')
        filename = 'temp.mp3'
        tts.save(filename)
        music = pyglet.media.load(filename, streaming=False)
        music.play()

        sleep(music.duration)  # prevent from killing
        os.remove(filename)  # remove temperory file

        cur = mysql.connection.cursor()
        cur.execute("SELECT  * FROM product where cate = '%s' " % (check))
        data = cur.fetchall()
        cur.close()

        return render_template('viewproduct.html', productlist=data, u=fname)


@app.route('/proddetails', methods=['POST'])
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


@app.route('/prodadd', methods=['POST'])
def prodadd():
    uname = session["email"]
    result = request.form['result']
    print(result)
    cur = mysql.connection.cursor()
    cur.execute("SELECT  pid, pname,cate,pprice,pweight,des,pimage FROM product where pid = '%s'" % (result))
    data = cur.fetchone()
    pid, pname, cate, pprice, pweight, des, pimage = data

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO addcart (cpid, cpname, ccate,cpprice,cpweight,cdes,cpimage,cuname) VALUES (%s, %s, %s,%s,%s,%s,%s,%s)",
        (pid, pname, cate, pprice, pweight, des, pimage, uname))
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
    pid, pname, cate, pprice, pweight, des = data

    today = date.today()
    tax = pprice * 12 / 100

    return render_template('AddPayment.html', today=today, username=session["username"], pid=pid, pname=pname,
                           pprice=pprice, tax=tax, total=tax + pprice)


@app.route('/insertpayment', methods=['POST'])
def insertpayment():
    if request.method == "POST":
        try:
            uname = session["email"]
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

            flash("Data Inserted Successfully")
            det = "Thank you for shopping"
            tts = gTTS(text=det, lang='en')
            filename = 'temp.mp3'
            tts.save(filename)
            music = pyglet.media.load(filename, streaming=False)
            music.play()
            sleep(music.duration)  # prevent from killing
            os.remove(filename)  # remove temperory file
            # adding in order list
            cur = mysql.connection.cursor()
            cur.execute("SELECT  pid, pname,cate,pprice,pweight,des,pimage FROM product where pid = '%s'" % (prodid))
            data = cur.fetchone()
            pid, pname, cate, pprice, pweight, des, pimage = data

            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO orderlist (opid, opname, ocate,opprice,opweight,odes,opimage,ouname) VALUES (%s, %s, %s,%s,%s,%s,%s,%s)",
                (pid, pname, cate, pprice, pweight, des, pimage, uname))
            mysql.connection.commit()
            print(det)
            return redirect(url_for('feedback'))
        except (Exception) as e:
            return redirect(url_for('addpayment'))


@app.route('/orderlist')
def orderlist():
    fname = session["fname"]
    uname = session["email"]
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from orderlist where ouname = '%s'" % (uname))
    data = cur.fetchall()
    cur.close()
    if data != ():
        return render_template('vieworderitem.html', productlist=data, u=fname)
    else:
        return render_template('orderempty.html', u=fname)


# this process from cart item..

@app.route('/proddetailscart', methods=['POST'])
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

    return render_template('AddPaymentcart.html', today=today, username=session["email"], pid=pid, pname=pname,
                           pprice=pprice, tax=tax, total=tax + pprice)


@app.route('/insertpaymentcart', methods=['POST'])
def insertpaymentcart():
    fname = session["fname"]
    name = session["email"]
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
            cur.execute("Delete from addcart where cpid = '%s' and cuname = '%s'" % (prodid, name))
            mysql.connection.commit()
            cur.close()

            return redirect(url_for('feedback'))
        except (Exception) as e:
            return redirect(url_for('addpayment'))


@app.route('/deletecartitem', methods=['POST'])
def deletecartitem():
    name = session["email"]
    result = request.form['result']
    print(result)
    cur = mysql.connection.cursor()
    cur.execute("Delete from addcart where cpid = '%s' and cuname = '%s'" % (result, name))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('viewproduct'))


# *************************************************************


@app.route('/feedback')
def feedback():
    today = date.today()
    return render_template('Addfeedback.html', uid=session["userid"], today=today)


@app.route('/insertfeedback', methods=['POST'])
def insertfeedback():
    if request.method == "POST":
        try:
            today = request.form['today']
            userid = request.form['userid']
            rating = request.form['rating']
            review = request.form['review']

            print(today, userid, rating, review)

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO feedback(fdate, userid, rating,review) VALUES (%s, %s, %s,%s)",
                        (today, userid, rating, review))

            mysql.connection.commit()
            flash("Data Inserted Successfully")
            det = "Thank you for feedback"
            tts = gTTS(text=det, lang='en')
            filename = 'temp.mp3'
            tts.save(filename)
            music = pyglet.media.load(filename, streaming=False)
            music.play()

            sleep(music.duration)  # prevent from killing
            os.remove(filename)  # remove temperory file
            print(det)
            return redirect(url_for('viewproduct'))
        except (Exception) as e:
            return redirect(url_for('feedback'))




@app.route('/cancel')
def cancel():
    return render_template('AdminIndex.html' )
if __name__ == "__main__":
    app.run()

#pip install Flask-Session
    
