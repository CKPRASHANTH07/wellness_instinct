from flask import *
import pymongo
from flask_session import Session
import random
import smtplib
from email.message import EmailMessage
import datetime
import re
import base64
from validate_email import validate_email
from dotenv import load_dotenv
import os
import bcrypt
import logics

from cryptography.fernet import Fernet

load_dotenv()

project_server = pymongo.MongoClient(os.getenv("pymongo_client"))
db_users = project_server['users']
users_column = db_users['users_list']
count_column = db_users['counts']
tweet_column = db_users['users_tweet']

doc_column = db_users['doc_column']

db_content = project_server['contents']
home_content_column = db_content['home_content']


app = Flask(__name__)
app.config['SESSION_TYPE'] = os.getenv("session_type")
app.config['SECRET_KEY'] = os.getenv("secret_key")
sess = Session()

key = b'My key'
urlsafe_key = base64.urlsafe_b64encode(key + b'\x00' * (32 - len(key)))
fernet = Fernet(urlsafe_key)

# @app.route('/')
# def home():
#     outsourcing_medical_service = home_content_column.find({'Block':'outsourcing medical service'}) 
#     exercise_at_home = home_content_column.find({'Block':'exercise'})
#     return render_template('home.html',oms = outsourcing_medical_service, ex = exercise_at_home)

@app.route('/')
def home():
    outsourcing_medical_service = home_content_column.find({'Block':'outsourcing medical service'}) 
    asmr_video = home_content_column.find_one({'Block':'asmr_link'})
    print(asmr_video)
    asmr_link = asmr_video['asmr_links']
    exercise_at_home = home_content_column.find({'Block':'exercise'})
    return render_template('home.html',oms = outsourcing_medical_service, ex = exercise_at_home, asmr_link = asmr_link)

@app.route('/login',methods=['GET','POST'])
def login():
    msg = ""
    if request.method == 'POST':
        details = request.form
        name = details['username']
        password = details['password']
        user = users_column.find_one({"$or":[{'Email':name},{'Phone':name}]})
        if user:
            if bcrypt.checkpw(password.encode('utf-8'), user['Password']):
                session['user_id'] = user['User_Id']
                session['name'] = user['Name']
                session['role'] = user['Role']
                session['email'] = user['Email']
                session['phone'] = user['Phone']
                if session['role'] == 'admin':
                    return redirect('/admin_dashboard')
                else:
                    return redirect('/user_dashboard')
            else:
                msg = "wrong Password"
        else:
            msg ="Wrong Username"
    return render_template('login.html',msg=msg)

@app.route('/admin_dashboard',methods=['GET','POST'])
def admin_dashboard():
    no_of_users = users_column.count_documents({'Role': 'user'})
    accounts = users_column.find_one({'Name': session['name']})
    number_colum = count_column.find_one({})
    number = number_colum['count']
    return render_template('admin_dashboard.html', account=accounts, counts=number, users_count=no_of_users)

@app.route('/user_dashboard',methods=['GET','POST'])
def user_dashboard():
    number_colum = count_column.find_one({})
    number = number_colum['count']
    accounts = users_column.find_one({'Name': session['name']})
    number = number + 1
    count_column.update_one({}, {'$set': {'count': number}})
    return render_template('user_dashboard.html', account=accounts)

@app.route('/signup', methods=['GET'])
def show_signup_form():
    return render_template('register.html', msg='')

@app.route('/signup',methods=['POST'])
def signup():
    msg = ""
    if request.method == 'POST':
        details = request.form
        email = details['email_address']
        name = details['username']
        phone = details['phone']
        password = details['password']
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        dob = details['dob']
        otp=  details['otp']
        if int(otp)==session['new_otp']  :
            latest_doc = users_column.find_one(sort=[('User_Id', -1)])
            id = int(latest_doc['User_Id']) + 1 if latest_doc else 1
            b= logics.add_user(id, name,  email, phone, password_hash, dob)
            session['new_otp'] = None
            return redirect('/login')
        else:
            msg = "Wrong Otp"
    return render_template('register.html',msg= msg)

@app.route('/generate_otp_email',methods=['GET','POST'])
def generate_otp_email():
    msg=""
    if request.method == 'POST':
        email=request.form.get('data')
        user = users_column.find_one({'Email':email})
        if user:
            msg = "User Email already Registered"
        else:
            msg = "OTP send to corresponding mail"
            email_otp = logics.generate_otp(email)
            session['new_otp'] = email_otp
            if email_otp == 0:
                otp_status = 1
            else :
                otp_status = email_otp
    return jsonify ({'success':True,'otp':otp_status,'msg':msg})


    
@app.route('/mail_to_subscribers',methods = ['GET','POST'])
def mail_to_subscribe():
    if request.method == 'POST':
        content=request.form.get('data')
        mail_subscribe = users_column.find({'Mail_Status':'Subscribe'})
        for users in mail_subscribe:
            a=logics.send_mail(users['Email'], content)
        return jsonify ({'success':True,})

@app.route('/bot',methods=['GET','POST'])
def bot():
    return render_template('chat_bot.html')

@app.route('/chat_response',methods=['GET','POST'])
def chat_bot_url():
    if request.method == 'POST':
        comment = request.form.get('comment')
        reply_comment = logics.chatbot(comment)
    return jsonify({'reply_status':reply_comment})

@app.route('/editing',methods=['GET','POST'])
def editing():
    return render_template('editing.html')

@app.route('/add_oms',methods=['GET','POST'])
def add_oms():
    if request.method == 'POST':
        image_link=request.form.get('image_link') 
        link_oms=request.form.get('link_oms') 
        outsourcing_type=request.form.get('outsourcing_type') 
        logics.add_to_oms(image_link , link_oms , outsourcing_type)
    return jsonify ({'success':True,})

@app.route('/add_asmr',methods=['GET','POST'])
def add_asmr():
    if request.method == 'POST':
        print("Done")
        asmr_links=request.form.get('asmr_links')
        logics.add_asmr_links(asmr_links)
    return jsonify ({'success':True,})

@app.route('/venting',methods=['GET','POST'])
def venting():
    return render_template('venting.html')

@app.route('/tweet',methods=['GET','POST'])
def tweet():
    if request.method == 'POST':
        message = request.form.get('tweet_msg')
        logics.add_tweet(message, session['name'] )
    return jsonify ({'success':True,})

@app.route('/forum',methods=['GET','POST'])
def forum():
    tweets = tweet_column.find()
    return render_template('TwitterCole.html',tweets = tweets)

@app.route('/logout')
def logout():
    return redirect('/')

@app.route('/chat_to')
def chat_to():
    return render_template('chat_to.html')

@app.route('/search_user', methods=['POST'])
def search():
    query = request.form['query']
    print(query)
    if query:
        results = users_column.find({'Name': {'$regex': '.*' + query + '.*'}})
        return jsonify({'results':results})
    else:
        return ''

@app.route('/chat_page')
def chat_page():
    chats = logics.get_chat_time_line(session['name'], 'naveen')
    decrypted_chats = []
    for chat in chats:
        chat['message'] = fernet.decrypt(chat['message']).decode()
        decrypted_chats.append(chat)
    return render_template('chats.html',chats = decrypted_chats)

@app.route('/chat_upload',methods=['GET','POST'])
def chat_upload():
    if request.method == 'POST':
        message = request.form.get('message')
        encMessage = fernet.encrypt(message.encode())
        logics.chat_time(session['name'], 'naveen', encMessage)
    return jsonify({'status':True})

#doc
@app.route('/doc_entry',methods=['GET','POST'])
def add_doc():
    if request.method=='POST':
        name=request.form['doc_name']
        clinic = request.form['doc_clinic']
        specialist=request.form['doc_specialist']
        year=request.form['doc_experience']
        city=request.form['doc_city']
        address = request.form['doc_address']
        phone = request.form['doc_phone']
        con_fee = request.form['doc_fee']
        #image_uploading
        file = request.files["img_file"]
        img_binary = file.read()
        #storing Id
        latest_id = doc_column.find_one(sort=[('User_Id', -1)])
        id = int(latest_id['Doc_Id']) + 1 if latest_id else 1
        b=logics.add__doc(id, name, specialist, year, city, address, phone, img_binary, clinic, con_fee)
    return render_template('add_doc.html')

@app.route('/get_city_doc',methods=['GET','POST'])
def get_city_doc():
    city = request.form.get('city')
    details = doc_column.find({'City':city},{'_id':0,'Image':0})
    lists = []
    for i in details:
        for j in i.values():
            lists.append(j)
    return jsonify(lists)

@app.route('/doc_city',methods=['GET','POST'])
def city():
    # tn_cities = ['Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem', 'Tirunelveli', 'Erode', 'Vellore', 'Thoothukudi', 'Thanjavur', 'Dindigul', 'Kanchipuram', 'Nagercoil', 'Hosur', 'Pudukkottai', 'Krishnagiri', 'Kumbakonam', 'Cuddalore', 'Nagapattinam', 'Tiruvannamalai']
    details = doc_column.find()
    return render_template('doc_city.html',doctor_details=details)


if __name__=="__main__":
    app.run(debug=True, host="192.168.35.244")