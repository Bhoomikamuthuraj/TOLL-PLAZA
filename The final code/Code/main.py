from flask import Flask, render_template, Response, redirect, url_for, request, flash, session
import cv2
import pytesseract
import mysql.connector
import razorpay
from flask_mail import Mail, Message
import datetime

#variables
min_area = 600
count=1

#importing harcascade files
harcascade = "model\haarcascade_russian_plate_number.xml"
pytesseract.pytesseract.tesseract_cmd ='C:/Program Files/Tesseract-OCR/tesseract.exe'

#configure mysql connection
mydb=mysql.connector.connect(
host="localhost",
user="root",
password="Bhoomika@2002",
database="final_project"
)

app=Flask(__name__, static_folder='static')     #WSGI 
app.secret_key = 'dont tell anyone'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "plazaplus.ltd@gmail.com"
app.config['MAIL_PASSWORD'] = "lcbojetmfdmgdoiq"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True 
mail=Mail(app)          #mail instance


@app.route("/")            #decorator
def index():
    return render_template('index.html')

############################################# ADMIN ########################################

@app.route("/admin",methods=['POST','GET'])
def admin():
    if request.method=='POST':
        admin_id = str(request.form['admin_login_email'])
        admin_pw = str(request.form['admin_login_password'])

        cursor=mydb.cursor()
        cursor.execute("SELECT * FROM final_project.admin_table WHERE admin_id=%s and admin_pw=%s",(admin_id,admin_pw))
        data=cursor.fetchone()

        if data == None:
            flash("Wrong login credentials please try again !!!")
            return redirect(url_for("index"))
        else:
            flash("Login successful!!!")
            return render_template('admin.html')
        
    else:
        return render_template('admin.html')
        
@app.route("/acc_rej_user")
def acc_rej_user():
    cursor=mydb.cursor()
    cursor.execute("SELECT user_name,vehicle_no,user_id,vehicle_type FROM final_project.user_table where status='pending'")
    data=cursor.fetchall()

    return render_template('acc_rej_user.html',DATA=data)

@app.route("/update_accept/<string:number>")
def update_accept(number):
    params=(number,)
    cursor=mydb.cursor()
    cursor.execute("UPDATE final_project.user_table SET status = 'accepted' WHERE (vehicle_no = %s)",params)
    mydb.commit()
    return redirect(url_for("acc_rej_user"))

@app.route("/update_reject/<string:number>")
def update_reject(number):
    params=(number,)
    cursor=mydb.cursor()
    cursor.execute("UPDATE final_project.user_table SET status = 'rejected' WHERE (vehicle_no = %s)",params)
    mydb.commit()
    flash("USER REJECTED")
    return redirect(url_for("acc_rej_user"))


@app.route("/registered_user")
def registered_user():
    cursor=mydb.cursor()
    cursor.execute("SELECT user_name,user_id,vehicle_no,city,state,phone_no FROM final_project.user_table where status='accepted'")
    data=cursor.fetchall()

    return render_template('registered_user.html',DATA=data)

@app.route("/rejected_user")
def rejected_user():
    cursor=mydb.cursor()
    cursor.execute("SELECT user_name,user_id,vehicle_no,city,state,phone_no FROM final_project.user_table where status='rejected'")
    data=cursor.fetchall()

    return render_template('rejected_user.html',DATA=data)

@app.route("/add_del_toll")
def add_del_toll():
    cursor = mydb.cursor()
    cursor.execute("SELECT toll_name,location,toll_id FROM final_project.toll_table")
    data=cursor.fetchall()

    return render_template('add_del_toll.html',DATA=data)

@app.route("/add_toll",methods=['GET','POST'])
def add_toll():
    if request.method=='POST':
        toll_name = str(request.form['add_tollbooth_name'])
        toll_id = str(request.form['add_tollbooth_mailid'])
        toll_ps = str(request.form['add_tollbooth_password'])
        toll_loc = str(request.form['add_tollbooth_location'])

        cursor = mydb.cursor()
        cursor.execute("INSERT INTO final_project.toll_table (toll_name,toll_id,toll_pw,location) VALUES (%s,%s,%s,%s)",(toll_name,toll_id,toll_ps,toll_loc))
        mydb.commit()

        flash('TOLL BOOTH DETAILS ADDED.')
    
    return redirect(url_for("add_del_toll"))
            
###################################### TOLL PLAZA #######################################    

@app.route("/tollplaza",methods=['POST','GET'])
def toll():
    if request.method == 'POST':
        toll_email = str(request.form['tollplaza_login_email'])
        toll_pw = str(request.form['tollplaza_login_password'])

        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM final_project.toll_table WHERE toll_id=%s and toll_pw=%s",(toll_email,toll_pw))
        data = cursor.fetchone()
         
        if data == None:
            flash("Wrong login credentials!! Try again")
            return redirect(url_for("index"))
        else:
            flash("Logged in successfully !!!")
            return render_template('tollplaza.html')
        
    else :
        return render_template('tollplaza.html')

@app.route("/result")
def result():
    number = detect()
    return render_template('result.html',NUMBER=number)

@app.route("/result1",methods=['GET','POST'])
def result1():
    if request.method == 'POST':
        number = request.form['tollplaza_vehicleno']
        params=(number,)

        cursor=mydb.cursor()
        cursor.execute("SELECT user_name, user_id, vehicle_type, city, phone_no, vehicle_no FROM final_project.user_table where vehicle_no=%s",(params))
        info=cursor.fetchall()

        cursor.execute("SELECT toll_name, amount_paid, status, book_id FROM final_project.pre_book_table where vehicle_no=%s and book_id = (SELECT max_bookid FROM (SELECT MAX(book_id) AS max_bookid FROM final_project.pre_book_table) AS subquery)",params)
        info2=cursor.fetchall()

        print(info)
        print(info2)

        return render_template("result1.html",DATA=info,DATA2=info2)

@app.route("/update_done/<string:id>")
def update_done(id):
    cursor=mydb.cursor()
    cursor.execute("UPDATE final_project.pre_book_table SET status = 'done' WHERE book_id = %s",(id,))
    mydb.commit()

    cursor.execute("SELECT vehicle_no,toll_name,amount_paid FROM final_project.pre_book_table WHERE book_id = %s",(id,))
    data=cursor.fetchall()

    for item in data: 
        msg = "Your Vehicle with vehicle number = "+item[0]+" has passed - "+item[1]+" with the payment of RS."+item[2]+" at "+str(datetime.datetime.now())


    cursor.execute("SELECT user_id FROM final_project.user_table where vehicle_no=%s",(data[0][0],))
    email=cursor.fetchall()
    user_mail=email[0][0]

    subject = 'Pre-booked Payment Details'
    message = Message(subject,sender="plazaplus.ltd@gmail.com",recipients=[user_mail])
    message.body = msg

    mail.send(message)

    return render_template("tollplaza.html")
    

################################################### USER #####################################################

@app.route("/user",methods=['GET','POST'])
def user():
    if request.method=="POST":
        user_id = str(request.form['user_login_email'])
        user_pw = str(request.form['user_login_password'])

        cursor=mydb.cursor()
        cursor.execute("SELECT * FROM final_project.user_table WHERE user_id=%s and user_pw=%s",(user_id,user_pw))
        data=cursor.fetchone()

        if data == None:
            flash("Wrong credentials!! Try again.")
            return redirect(url_for("index"))
        else:
            session['loggedin']=True
            session['user_id']=data[1]

            cursor.execute("SELECT status FROM final_project.user_table WHERE user_id=%s",(user_id,))
            status=cursor.fetchone()
            print(status[0])
            if status[0]=='pending':
                flash('Your Request is still pending, Do check after some time!!!')
                return redirect(url_for("index"))
            elif status[0] == 'rejected':
                flash('Your Request has been Rejected !!! Do verify your details!!!')
                return redirect(url_for("index"))
            else:
                flash('Logged in successfully.')
                return render_template('user.html')

    else:
        return render_template("user.html")
    
@app.route("/signin")
def signin(): 
    return render_template('/signin.html')
    
@app.route("/add_user",methods=['POST','GET'])
def add_user():
    status = 'pending' 
    if request.method=="POST":
        user_name=str(request.form['signin_name'])
        vehicle_no=str(request.form['signin_vehicle_no'])
        vehicle_type=str(request.form['signin_vehicletype'])
        user_city=str(request.form['signin_city'])
        user_state=str(request.form['signin_state'])
        phone_no=str(request.form['signin_ph_no'])
        user_email=str(request.form['signin_email'])
        user_pw=str(request.form['signin_password'])

        cursor=mydb.cursor()
        cursor.execute("INSERT INTO user_table(user_name,user_id,user_pw,vehicle_no,vehicle_type,status,city,state,phone_no) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);",(user_name,user_email,user_pw,vehicle_no,vehicle_type,status,user_city,user_state,phone_no))
        mydb.commit()

        return redirect(url_for("index"))

@app.route("/prebook/")
def prebook():
    cursor=mydb.cursor()
    cursor.execute("SELECT vehicle_no from final_project.user_table where user_id=%s",(session['user_id'],))
    number=cursor.fetchone()

    return render_template("prebook.html",NUMBER=number[0])

@app.route("/prebook/add_prebook",methods=['GET','POST'])
def add_prebook():
    if request.method=="POST":
        number=request.form['vehicle_no']
        select_toll=str(request.form['selected_toll'])
        select_route=str(request.form['mySelect'])
        toll_amount=str(request.form['toll_amount'])
        status='pending'
        date=datetime.date.today()
        formatted_date = str(date.strftime('%d-%m-%Y'))

        cursor=mydb.cursor()
        cursor.execute("INSERT INTO final_project.pre_book_table(date,vehicle_no,toll_name,amount_paid,status) VALUES (%s,%s,%s,%s,%s)",(formatted_date,number,select_toll,toll_amount,status))
        mydb.commit()

        cursor.execute("SELECT user_name,user_id,phone_no FROM final_project.user_table where vehicle_no=%s",(number,))
        info=cursor.fetchall()
        INFO=(info[0])

        toll_amount=(int(toll_amount)*100)
        # toll_amount=1000
        client = razorpay.Client(auth=('rzp_test_cXFVB8FzMYf1gW', 'cGYO1EEFdZDVXzn7P22Ur3jc'))
        DATA = {
        "amount": toll_amount,
        "currency": "INR",
        "receipt": str(id),
        }
        payment=client.order.create(data=DATA)

        username=INFO[0]
        userid=INFO[1]
        user_number=INFO[2]
        selected_toll=select_toll
        t_amount=toll_amount

        return render_template('/payment.html',payment=payment,INFO=info,TOLL=selected_toll,AMOUNT=t_amount,NUMBER=number,USER=username ,ID=userid, PH_NO=user_number)

@app.route("/success",methods=['GET','POST'])
def success():
    cursor=mydb.cursor()
    cursor.execute("UPDATE final_project.pre_book_table SET status = 'booked' WHERE (book_id = (SELECT max_bookid FROM (SELECT MAX(book_id) AS max_bookid FROM final_project.pre_book_table) AS subquery))")
    mydb.commit()

    return render_template("/success.html")

@app.route("/booking")
def booking():
    cursor=mydb.cursor()

    cursor.execute("SELECT vehicle_no from final_project.user_table where user_id=%s",(session['user_id'],))
    number=cursor.fetchone()

    cursor.execute("SELECT date, toll_name, amount_paid, status FROM final_project.pre_book_table WHERE vehicle_no=%s",(number[0],))
    data=cursor.fetchall()
    
    return render_template('/booking.html',DATA=data)

@app.route("/profile")
def profile():
    cursor=mydb.cursor()
    cursor.execute("SELECT * from final_project.user_table where user_id=%s",(session['user_id'],))
    data=cursor.fetchone()
    list_data=[data]
    print(list_data)

    return render_template('/profile.html',DATA=list_data)

@app.route("/forgot_password", methods=['GET','POST'])
def forgot_password():
    if request.method=='POST':
        email = str(request.form['user_email'])
        password = str(request.form['password'])

        cursor = mydb.cursor()
        cursor.execute("SELECT * from final_project.user_table where user_id=%s",(email,))
        data = cursor.fetchall()

        if data == None:
            return redirect(url_for('forgot_password'))
        else:
            cursor.execute("UPDATE final_project.user_table SET user_pw=%s where user_id=%s",(password,email))
            mydb.commit()

            flash('PASSWORD CHANGED SUCCESSFULLY.')

            return render_template('/index.html')
    else:
        return render_template('/forgot_password.html')


@app.route('/video')
def video():
    return Response(detect_number(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/logout")
def logout():
    flash("You have successfully logged out !!!")
    return redirect(url_for("index"))


##############   FUNCTIONS    #################
cap=cv2.VideoCapture(0)
def detect_number():
    while True:
        success ,img = cap.read()

        if not success:
            break
        else: 
            plate_cascade = cv2.CascadeClassifier(harcascade)      #loading harcascade xml file
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)       #converting to gray scale image 

            plates = plate_cascade.detectMultiScale(img_gray, 1.1, 4)

            for (x,y,w,h) in plates:
                area = w * h
                ##
                if area > min_area:
                    cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)

                    img_roi = img[y: y+h, x:x+w]
                    #cv2.imshow("roi", img_roi)

                    grayscale_img = cv2.cvtColor(img_roi,cv2.COLOR_BGR2GRAY)    #converting image to gray scales

                    cv2.imwrite("..\plate_images\plates\scanned_img"+str(count)+".jpg", img_roi)
                    cv2.imwrite("..\static\scanned_img"+str(count)+".jpg", img_roi)

                    result = pytesseract.image_to_string(img_roi)
                    #cv2.imshow('result',img)
                    
            ret,buffer=cv2.imencode('.jpg',img)
            img =buffer.tobytes()
        yield(b'--frame\r\n'+b'content-Type: image/jpeg\r\n\r\n'+img+b'\r\n')
        
            
def detect():
    img = "..\static\scanned_img1.jpg"
    result = pytesseract.image_to_string(img)
    print(str(result))
    return str(result)
 
   
if __name__=='__main__':
    app.run(host='0.0.0.0',debug=True)