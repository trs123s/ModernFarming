# Importing essential libraries and modules
from flask import Flask, render_template, request, Markup,session, redirect, url_for, flash, Response 
import numpy as np
import pandas as pd
from utils.disease import disease_dic
from utils.fertilizer import fertilizer_dic
import requests
import config
import pickle
import io
import sqlite3
from PIL import Image
import random
from twilio.rest import Client
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from forms import LoginForm
import datetime as dt
import os
import bcrypt
# ==============================================================================================


# -------------------------LOADING THE TRAINED MODELS -----------------------------------------------


# Loading crop recommendation model

crop_recommendation_model_path = 'models/RandomForest.pkl'
crop_recommendation_model = pickle.load(
    open(crop_recommendation_model_path, 'rb'))


# =========================================================================================

# Custom functions for calculations


def weather_fetch(city_name):
    """
    Fetch and returns the temperature and humidity of a city
    :params: city_name
    :return: temperature, humidity
    """
    api_key = config.weather_api_key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()

    if x["cod"] != "404":
        y = x["main"]

        temperature = round((y["temp"] - 273.15), 2)
        humidity = y["humidity"]
        return temperature, humidity
    else:
        return None



# ===============================================================================================
# ------------------------------------ FLASK APP -------------------------------------------------


app = Flask(__name__)
app.secret_key = "otp"#secret
# render home page
# bcrypt = Bcrypt(app)


@ app.route('/')
def home():
    title = 'Harvestsolutions - Home'
    return render_template('index.html', title=title)
#=================================login signup==================
@ app.route('/login')
def login():
    title = 'Harvestsolutions - Home'
    return render_template('login.html', title=title)
@ app.route('/login', methods =['POST'])
def checklogin():
    UN = request.form['username']
    session['username'] = request.form['username']
    PW = request.form['password']
    
    sqlconnection = sqlite3.Connection("login.db")
    cursor = sqlconnection.cursor()
    query1 = "SELECT password From users WHERE username = '{un}'".format(un=UN)
    cursor.execute(query1)
    hashed= cursor.fetchone()
    rows = cursor.fetchall()
    print(rows)
    if hashed is None or not bcrypt.checkpw(PW.encode('utf-8'), hashed[0]):
        return redirect("/register")
    else:
        return redirect("/")
    
@app.route('/logout')
def logout():
    if 'username' in session:  
        session.pop('username',None)  
        return redirect('/');  
    else:  
        return '<p>user already logged out</p>'  

UPLOAD_FOLDER = './static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

@ app.route('/register', methods = ['GET', 'POST'])
def registerpage():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        email = request.form['email']
        file1 = request.files['file1']
        if 'file1' not in request.files:
            return 'there is no file1 in form!'
        path = os.path.join(app.config['UPLOAD_FOLDER'], str(username)+ ".jpg")
        file1.save(path)
        path = str(path)
        print(path)
        try:
            with sqlite3.connect("login.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO users (username,password,email,path) values (?,?,?,?)",(username,hashed,email,path))
                con.commit()
                flash("Successfully Registered")
                return redirect('/login')
        except:
            msg= "Again"
            return render_template("Register.html",msg=msg)
            
    return render_template("Register.html")


        # <img src="{{url_for('static', filename='Hermes.png')}}" align="middle" /> 

# x = cur.execute("SELECT * FROM users WHERE username = ?", (username))
            
            # if int(len(x)) > 0:
            #     return render_template('error.html')
            # else:
#=================================login signup==================

# render crop  form page
@ app.route('/crop')
def crop():
    title = 'Harvestsolutions - Crop'
    return render_template('fuser.html', title=title)

# render crop recommendation form page
@ app.route('/crop-recommend')
def crop_recommend():
    title = 'Harvestsolutions - Crop Recommendation'
    return render_template('crop.html', title=title)

@ app.route('/crop-register')
def crop_register():
    title = 'Harvestsolutions - Crop Register'
    return render_template('crop-register.html', title=title)

# render fertilizer recommendation form page


@ app.route('/fertilizer')
def fertilizer_recommendation():
    title = 'Harvestsolutions - Fertilizer Suggestion'

    return render_template('fertilizer.html', title=title)

@ app.route('/users')
def user_details():
    title = 'Harvestsolutions - User Suggestion'

    return render_template('user.html', title=title)

@ app.route('/profile')
def profile():
    title = 'Harvestsolutions - Register'
    return render_template('userprofile.html', title=title)

@app.route("/view-profile", methods=['POST'])  
def viewprofile():  
    title = 'Harvestsolutions - User Profile'
    if request.method == 'POST':
        username = request.form["username"]
        con = sqlite3.connect("login.db")  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        query = "SELECT  * FROM users WHERE"
        query = query + " " + "username" + " LIKE " + "'"
        query = query + str(username) + "'"
        print(query)
        cur.execute(query)  
        rows = cur.fetchall()  
        for row in rows:
            print(row[0])
        return render_template("view-profile.html",rows = rows, title=title)

# render disease prediction input page

# ===================================Login via OTP()============================================

# @app.route('/login')
# def login():
# 	return render_template('loginOTP.html')

# @app.route('/getOTP', methods=['POST'])
# def getOTP():
# 	number = request.form['number']
# 	val = getOTPApi(number)
# 	if val:
# 		return render_template('enterOTP.html')
# 	return render_template('enterOTP.html')
# @app.route('/validateOTP', methods = ['POST'])
# def validateOTP():
# 	otp = request.form['otp']
# 	if 'response' in session:
# 		s = session['response']
# 		session.pop('response',None)
# 		if s == otp:
# 			return render_template('crop-register.html')
# 		else:
# 			return 'You are not Authorized , Sorry'
# def generateOTP():
# 	return random.randrange(100000, 999999)

# def getOTPApi(number):
# 	account_sid = 'ACa46e556b138b226b0ed97bbf451589fa' 
# 	auth_token = '17595c2b0ed59bbe3b991685d4c05de8' 
# 	client = Client(account_sid, auth_token) 
# 	otp=generateOTP()
# 	session['response'] = str(otp)
# 	body = 'Your OTP is' + str(otp)
# 	message = client.messages.create(
# 		from_='+15597852530',
# 		body=body,
# 		to=number
# 		)
# 	if message.sid:
# 		return True
# 	else:
# 		False

# ===============================================================================================
#USer profile



# ===============================================================================================

# RENDER PREDICTION PAGES

# render crop recommendation result page

@ app.route('/crop-predict', methods=['POST'])
def crop_prediction():
    title = 'Harvestsolutions - Crop Recommendation'

    if request.method == 'POST':
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['pottasium'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])

        # state = request.form.get("stt")
        city = request.form.get("city")

        if weather_fetch(city) != None:
            temperature, humidity = weather_fetch(city)
            data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            my_prediction = crop_recommendation_model.predict(data)
            final_prediction = my_prediction[0]

            return render_template('crop-result.html', prediction=final_prediction, title=title)

        else:

            return render_template('try_again.html', title=title)

@ app.route('/crop-registered', methods=['POST'])
def crop_register_success():
    title = 'Harvestsolutions - Crop Registered'
    msg = "msg"  

    if request.method == 'POST':
        try:  
            name = request.form["name"]  
            phonenumber = request.form["phonenumber"]  
            adharnumber = request.form["adharnumber"]  
            area = request.form["area"]  
            cropg = request.form["cropg"]  
            cropr = request.form["cropr"]  
            nitrogen = request.form['nitrogen']
            phosphorous = request.form['phosphorous']
            pottasium = request.form['pottasium']
            ph = request.form['ph']
            rainfall = request.form['rainfall']
            state = request.form['state']
            city = request.form['city']
            username = request.form['username']
            Timestamp = dt.datetime.now()
            # city = request.form.get("city")
            # temperature, humidity = weather_fetch(city)
            with sqlite3.connect("fdetail.db") as con:  
                cur = con.cursor()  
                cur.execute("INSERT into FDetails (name, phonenumber, adharnumber, area, cropg, cropr, nitrogen, phosphorous, pottasium, ph, rainfall, state, city, username, Timestamp) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(name,phonenumber,adharnumber,area,cropg,cropr,nitrogen,phosphorous,pottasium,ph,rainfall,state,city,username,Timestamp))  
                con.commit()  
                msg = "Your farm is registered"  
        except:  
            con.rollback()  
            # msg = "We can not add the employee to the list"  
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['pottasium'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])

        # state = request.form.get("stt")
        city = request.form.get("city")

        if weather_fetch(city) != None:
            temperature, humidity = weather_fetch(city)
            data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            my_prediction = crop_recommendation_model.predict(data)
            final_prediction = my_prediction[0]

            return render_template('crop-result.html', prediction=final_prediction, title=title, msg=msg)

        else:

            return render_template('try_again.html', title=title)


# # render users details

@app.route("/view", methods=['POST'])  
def view():  
    title = 'Harvestsolutions - User Recommendation'
    if request.method == 'POST':
        area = request.form["area"]  
        cropr = request.form["cropr"]  
        state = request.form["state"]  
        city = request.form["city"]  
        con = sqlite3.connect("fdetail.db")  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        query = "SELECT rowid, * FROM FDetails WHERE"
        query = query + " " + "area" + ">=" + area + " AND"
        query = query + " " + "cropr" + " LIKE " + "'"
        query = query + str(cropr) + "'" + " AND"
        query = query + " " + "state" + " LIKE " + "'"
        query = query + str(state) + "'" + " AND"
        query = query + " " + "city" + " LIKE " + "'"
        query = query + str(city) + "'"
        print(query)
        cur.execute(query)  
        rows = cur.fetchall()  
        return render_template("view.html",rows = rows, title=title)  

# @ app.route('/user-predict', methods=['POST'])
# def user_prediction():
#     title = 'Harvestsolutions - User Recommendation'
#     msg = "msg"  

#     if request.method == 'POST':
#         try:  
#             name = request.form["name"]  
#             phonenumber = request.form["phonenumber"]  
#             adharnumber = request.form["adharnumber"]  
#             area = request.form["area"]  
#             cropg = request.form["cropg"]  
#             cropr = request.form["cropr"]  
#             nitrogen = request.form['nitrogen']
#             phosphorous = request.form['phosphorous']
#             pottasium = request.form['pottasium']
#             ph = request.form['ph']
#             rainfall = request.form['rainfall']
#             state = request.form['state']
#             city = request.form['city']
#             # city = request.form.get("city")
#             # temperature, humidity = weather_fetch(city)
#             with sqlite3.connect("fdetail.db") as con:  
#                 cur = con.cursor()  
#                 cur.execute("INSERT into FDetails (name, phonenumber, adharnumber, area, cropg, cropr, nitrogen, phosphorous, pottasium, ph, rainfall, state, city) values (?,?,?,?,?,?,?,?,?,?,?,?,?)",(name,phonenumber,adharnumber,area,cropg,cropr,nitrogen,phosphorous,pottasium,ph,rainfall,state,city))  
#                 con.commit()  
#                 # msg = "Data successfully Added"  
#         except:  
#             con.rollback()  
#             # msg = "We can not add the employee to the list"  
#         N = int(request.form['nitrogen'])
#         P = int(request.form['phosphorous'])
#         K = int(request.form['pottasium'])
#         ph = float(request.form['ph'])
#         rainfall = float(request.form['rainfall'])

#         # state = request.form.get("stt")
#         city = request.form.get("city")

#         if weather_fetch(city) != None:
#             temperature, humidity = weather_fetch(city)
#             data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
#             my_prediction = crop_recommendation_model.predict(data)
#             final_prediction = my_prediction[0]

#             return render_template('user-view.html', prediction=final_prediction, title=title)

#         else:

#             return render_template('try_again.html', title=title)

# render fertilizer recommendation result page


@ app.route('/fertilizer-predict', methods=['POST'])
def fert_recommend():
    title = 'Harvestsolutions - Fertilizer Suggestion'
    if request.method == 'POST':
        # cropname = request.form["cropname"]  
        phonenumber = request.form["phonenumber"]  
        adharnumber = request.form["adharnumber"]  
        con = sqlite3.connect("fdetail.db")  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        query = "SELECT rowid, * FROM FDetails WHERE"
        query = query + " " + "phonenumber" + " LIKE " + "'"
        query = query + str(phonenumber) + "'" + " AND"
        query = query + " " + "adharnumber" + " LIKE " + "'"
        query = query + str(adharnumber) + "'"
        print(query)
        cur.execute(query)  
        rows = cur.fetchall()
        print(rows[0])
        # nitrogen = ''
        # phosphorous = ''
        # pottasium = ''
        # cropname = 
        for row in rows:
            print(str(row[0]) + " " + str(row[8]))
            crop_name = row[7]
            nitrogen = row[8]
            phosphorous = row[9]
            pottasium = row[10]
        
        # nitrogen = request.form["nitrogen"]  
        # phosphorous = request.form["phosphorous"]  
        # pottasium = request.form["pottasium"]  
        # nitrogen = '50'
        # phosphorous = '50'
        # pottasium = '50'
        # cropname = 
        # crop_name = str(cropname)
        # crop_name = "rice"
        N = int(nitrogen)
        P = int(phosphorous)
        K = int(pottasium)
        # ph = float(request.form['ph'])

        df = pd.read_csv('Data/fertilizer.csv')

        nr = df[df['Crop'] == crop_name]['N'].iloc[0]
        pr = df[df['Crop'] == crop_name]['P'].iloc[0]
        kr = df[df['Crop'] == crop_name]['K'].iloc[0]

        n = nr - N
        p = pr - P
        k = kr - K
        temp = {abs(n): "N", abs(p): "P", abs(k): "K"}
        max_value = temp[max(temp.keys())]
        if max_value == "N":
            if n < 0:
                key = 'NHigh'
            else:
                key = "Nlow"
        elif max_value == "P":
            if p < 0:
                key = 'PHigh'
            else:
                key = "Plow"
        else:
            if k < 0:
                key = 'KHigh'
            else:
                key = "Klow"

        response = Markup(str(fertilizer_dic[key]))

        return render_template('fertilizer-result.html', recommendation=response, rows=rows, title=title)

    # crop_name = str(request.form['cropname'])
    # N = int(request.form['nitrogen'])
    # P = int(request.form['phosphorous'])
    # K = int(request.form['pottasium'])
    # # ph = float(request.form['ph'])

    # df = pd.read_csv('Data/fertilizer.csv')

    # nr = df[df['Crop'] == crop_name]['N'].iloc[0]
    # pr = df[df['Crop'] == crop_name]['P'].iloc[0]
    # kr = df[df['Crop'] == crop_name]['K'].iloc[0]

    # n = nr - N
    # p = pr - P
    # k = kr - K
    # temp = {abs(n): "N", abs(p): "P", abs(k): "K"}
    # max_value = temp[max(temp.keys())]
    # if max_value == "N":
    #     if n < 0:
    #         key = 'NHigh'
    #     else:
    #         key = "Nlow"
    # elif max_value == "P":
    #     if p < 0:
    #         key = 'PHigh'
    #     else:
    #         key = "Plow"
    # else:
    #     if k < 0:
    #         key = 'KHigh'
    #     else:
    #         key = "Klow"

    # response = Markup(str(fertilizer_dic[key]))

    # return render_template('fertilizer-result.html', recommendation=response, title=title)

# render disease prediction result page


@app.route('/disease-predict', methods=['GET', 'POST'])
def disease_prediction():
    title = 'Harvestsolutions - Disease Detection'

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files.get('file')
        if not file:
            return render_template('disease.html', title=title)
        try:
            img = file.read()

            prediction = predict_image(img)

            prediction = Markup(str(disease_dic[prediction]))
            return render_template('disease-result.html', prediction=prediction, title=title)
        except:
            pass
    return render_template('disease.html', title=title)


# ===============================================================================================
if __name__ == '__main__':
    app.run(debug=True, port='7000')




# # Importing essential libraries and modules

# from flask import Flask, render_template, request, Markup
# import numpy as np
# import pandas as pd
# from utils.disease import disease_dic
# from utils.fertilizer import fertilizer_dic
# import requests
# import config
# import pickle
# import io
# import sqlite3
# from PIL import Image
# # ==============================================================================================

# # -------------------------LOADING THE TRAINED MODELS -----------------------------------------------

# # Loading plant disease classification model

# # disease_classes = ['Apple___Apple_scab',
#                    # 'Apple___Black_rot',
#                    # 'Apple___Cedar_apple_rust',
#                    # 'Apple___healthy',
#                    # 'Blueberry___healthy',
#                    # 'Cherry_(including_sour)___Powdery_mildew',
#                    # 'Cherry_(including_sour)___healthy',
#                    # 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
#                    # 'Corn_(maize)___Common_rust_',
#                    # 'Corn_(maize)___Northern_Leaf_Blight',
#                    # 'Corn_(maize)___healthy',
#                    # 'Grape___Black_rot',
#                    # 'Grape___Esca_(Black_Measles)',
#                    # 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
#                    # 'Grape___healthy',
#                    # 'Orange___Haunglongbing_(Citrus_greening)',
#                    # 'Peach___Bacterial_spot',
#                    # 'Peach___healthy',
#                    # 'Pepper,_bell___Bacterial_spot',
#                    # 'Pepper,_bell___healthy',
#                    # 'Potato___Early_blight',
#                    # 'Potato___Late_blight',
#                    # 'Potato___healthy',
#                    # 'Raspberry___healthy',
#                    # 'Soybean___healthy',
#                    # 'Squash___Powdery_mildew',
#                    # 'Strawberry___Leaf_scorch',
#                    # 'Strawberry___healthy',
#                    # 'Tomato___Bacterial_spot',
#                    # 'Tomato___Early_blight',
#                    # 'Tomato___Late_blight',
#                    # 'Tomato___Leaf_Mold',
#                    # 'Tomato___Septoria_leaf_spot',
#                    # 'Tomato___Spider_mites Two-spotted_spider_mite',
#                    # 'Tomato___Target_Spot',
#                    # 'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
#                    # 'Tomato___Tomato_mosaic_virus',
#                    # 'Tomato___healthy']

# # disease_model_path = 'models/plant_disease_model.pth'
# # disease_model = ResNet9(3, len(disease_classes))
# # disease_model.load_state_dict(torch.load(
#     # disease_model_path, map_location=torch.device('cpu')))
# # disease_model.eval()


# # Loading crop recommendation model

# crop_recommendation_model_path = 'models/RandomForest.pkl'
# crop_recommendation_model = pickle.load(
#     open(crop_recommendation_model_path, 'rb'))


# # =========================================================================================

# # Custom functions for calculations


# def weather_fetch(city_name):
#     """
#     Fetch and returns the temperature and humidity of a city
#     :params: city_name
#     :return: temperature, humidity
#     """
#     api_key = config.weather_api_key
#     base_url = "http://api.openweathermap.org/data/2.5/weather?"

#     complete_url = base_url + "appid=" + api_key + "&q=" + city_name
#     response = requests.get(complete_url)
#     x = response.json()

#     if x["cod"] != "404":
#         y = x["main"]

#         temperature = round((y["temp"] - 273.15), 2)
#         humidity = y["humidity"]
#         return temperature, humidity
#     else:
#         return None


# # def predict_image(img, model=disease_model):
#     # """
#     # Transforms image to tensor and predicts disease label
#     # :params: image
#     # :return: prediction (string)
#     # """
#     # transform = transforms.Compose([
#         # transforms.Resize(256),
#         # transforms.ToTensor(),
#     # ])
#     # image = Image.open(io.BytesIO(img))
#     # img_t = transform(image)
#     # img_u = torch.unsqueeze(img_t, 0)

#     # # Get predictions from model
#     # yb = model(img_u)
#     # # Pick index with highest probability
#     # _, preds = torch.max(yb, dim=1)
#     # prediction = disease_classes[preds[0].item()]
#     # # Retrieve the class label
#     # return prediction

# # ===============================================================================================
# # ------------------------------------ FLASK APP -------------------------------------------------


# app = Flask(__name__)

# # render home page


# @ app.route('/')
# def home():
#     title = 'Harvestsolutions - Home'
#     return render_template('index.html', title=title)

# # render crop recommendation form page

# @ app.route('/crop')
# def crop():
#     title = 'Harvestsolutions - Crop'
#     return render_template('fuser.html', title=title)

# @ app.route('/crop-recommend')
# def crop_recommend():
#     title = 'Harvestsolutions - Crop Recommendation'
#     return render_template('crop.html', title=title)

# # render fertilizer recommendation form page


# @ app.route('/fertilizer')
# def fertilizer_recommendation():
#     title = 'Harvestsolutions - Fertilizer Suggestion'

#     return render_template('fertilizer.html', title=title)

# @ app.route('/users')
# def user_details():
#     title = 'Harvestsolutions - User Suggestion'

#     return render_template('user.html', title=title)

# # render disease prediction input page




# # ===============================================================================================

# # RENDER PREDICTION PAGES

# # render crop recommendation result page


# @ app.route('/crop-predict', methods=['POST'])
# def crop_prediction():
#     title = 'Harvestsolutions - Crop Recommendation'
#     msg = "msg"  

#     if request.method == 'POST':
#         try:  
#             name = request.form["name"]  
#             phonenumber = request.form["phonenumber"]  
#             adharnumber = request.form["adharnumber"]  
#             area = request.form["area"]  
#             cropg = request.form["cropg"]  
#             cropr = request.form["cropr"]  
#             nitrogen = request.form['nitrogen']
#             phosphorous = request.form['phosphorous']
#             pottasium = request.form['pottasium']
#             ph = request.form['ph']
#             rainfall = request.form['rainfall']
#             state = request.form['state']
#             city = request.form['city']
#             # city = request.form.get("city")
#             # temperature, humidity = weather_fetch(city)
#             with sqlite3.connect("fdetail.db") as con:  
#                 cur = con.cursor()  
#                 cur.execute("INSERT into FDetails (name, phonenumber, adharnumber, area, cropg, cropr, nitrogen, phosphorous, pottasium, ph, rainfall, state, city) values (?,?,?,?,?,?,?,?,?,?,?,?,?)",(name,phonenumber,adharnumber,area,cropg,cropr,nitrogen,phosphorous,pottasium,ph,rainfall,state,city))  
#                 con.commit()  
#                 # msg = "Data successfully Added"  
#         except:  
#             con.rollback()  
#             # msg = "We can not add the employee to the list"  
#         N = int(request.form['nitrogen'])
#         P = int(request.form['phosphorous'])
#         K = int(request.form['pottasium'])
#         ph = float(request.form['ph'])
#         rainfall = float(request.form['rainfall'])

#         # state = request.form.get("stt")
#         city = request.form.get("city")

#         if weather_fetch(city) != None:
#             temperature, humidity = weather_fetch(city)
#             data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
#             my_prediction = crop_recommendation_model.predict(data)
#             final_prediction = my_prediction[0]

#             return render_template('crop-result.html', prediction=final_prediction, title=title)

#         else:

#             return render_template('try_again.html', title=title)


# # # render users details

# @app.route("/view", methods=['POST'])  
# def view():  
#     title = 'Harvestsolutions - User Recommendation'
#     if request.method == 'POST':
#         area = request.form["area"]  
#         cropr = request.form["cropr"]  
#         state = request.form["state"]  
#         city = request.form["city"]  
#         con = sqlite3.connect("fdetail.db")  
#         con.row_factory = sqlite3.Row  
#         cur = con.cursor()  
#         query = "SELECT rowid, * FROM FDetails WHERE"
#         query = query + " " + "area" + ">=" + str(area) + " AND"
#         query = query + " " + "cropr" + " LIKE " + "'"
#         query = query + str(cropr) + "'" + " AND"
#         query = query + " " + "state" + " LIKE " + "'"
#         query = query + str(state) + "'" + " AND"
#         query = query + " " + "city" + " LIKE " + "'"
#         query = query + str(city) + "'"
#         print(query)
#         cur.execute(query)  
#         rows = cur.fetchall()  
#         return render_template("view.html",rows = rows, title=title)  

# # @ app.route('/user-predict', methods=['POST'])
# # def user_prediction():
# #     title = 'Harvestsolutions - User Recommendation'
# #     msg = "msg"  

# #     if request.method == 'POST':
# #         try:  
# #             name = request.form["name"]  
# #             phonenumber = request.form["phonenumber"]  
# #             adharnumber = request.form["adharnumber"]  
# #             area = request.form["area"]  
# #             cropg = request.form["cropg"]  
# #             cropr = request.form["cropr"]  
# #             nitrogen = request.form['nitrogen']
# #             phosphorous = request.form['phosphorous']
# #             pottasium = request.form['pottasium']
# #             ph = request.form['ph']
# #             rainfall = request.form['rainfall']
# #             state = request.form['state']
# #             city = request.form['city']
# #             # city = request.form.get("city")
# #             # temperature, humidity = weather_fetch(city)
# #             with sqlite3.connect("fdetail.db") as con:  
# #                 cur = con.cursor()  
# #                 cur.execute("INSERT into FDetails (name, phonenumber, adharnumber, area, cropg, cropr, nitrogen, phosphorous, pottasium, ph, rainfall, state, city) values (?,?,?,?,?,?,?,?,?,?,?,?,?)",(name,phonenumber,adharnumber,area,cropg,cropr,nitrogen,phosphorous,pottasium,ph,rainfall,state,city))  
# #                 con.commit()  
# #                 # msg = "Data successfully Added"  
# #         except:  
# #             con.rollback()  
# #             # msg = "We can not add the employee to the list"  
# #         N = int(request.form['nitrogen'])
# #         P = int(request.form['phosphorous'])
# #         K = int(request.form['pottasium'])
# #         ph = float(request.form['ph'])
# #         rainfall = float(request.form['rainfall'])

# #         # state = request.form.get("stt")
# #         city = request.form.get("city")

# #         if weather_fetch(city) != None:
# #             temperature, humidity = weather_fetch(city)
# #             data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
# #             my_prediction = crop_recommendation_model.predict(data)
# #             final_prediction = my_prediction[0]

# #             return render_template('user-view.html', prediction=final_prediction, title=title)

# #         else:

# #             return render_template('try_again.html', title=title)

# # render fertilizer recommendation result page


# @ app.route('/fertilizer-predict', methods=['POST'])
# def fert_recommend():
#     title = 'Harvestsolutions - Fertilizer Suggestion'

#     crop_name = str(request.form['cropname'])
#     N = int(request.form['nitrogen'])
#     P = int(request.form['phosphorous'])
#     K = int(request.form['pottasium'])
#     # ph = float(request.form['ph'])

#     df = pd.read_csv('Data/fertilizer.csv')

#     nr = df[df['Crop'] == crop_name]['N'].iloc[0]
#     pr = df[df['Crop'] == crop_name]['P'].iloc[0]
#     kr = df[df['Crop'] == crop_name]['K'].iloc[0]

#     n = nr - N
#     p = pr - P
#     k = kr - K
#     temp = {abs(n): "N", abs(p): "P", abs(k): "K"}
#     max_value = temp[max(temp.keys())]
#     if max_value == "N":
#         if n < 0:
#             key = 'NHigh'
#         else:
#             key = "Nlow"
#     elif max_value == "P":
#         if p < 0:
#             key = 'PHigh'
#         else:
#             key = "Plow"
#     else:
#         if k < 0:
#             key = 'KHigh'
#         else:
#             key = "Klow"

#     response = Markup(str(fertilizer_dic[key]))

#     return render_template('fertilizer-result.html', recommendation=response, title=title)

# # render disease prediction result page


# @app.route('/disease-predict', methods=['GET', 'POST'])
# def disease_prediction():
#     title = 'Harvestsolutions - Disease Detection'

#     if request.method == 'POST':
#         if 'file' not in request.files:
#             return redirect(request.url)
#         file = request.files.get('file')
#         if not file:
#             return render_template('disease.html', title=title)
#         try:
#             img = file.read()

#             prediction = predict_image(img)

#             prediction = Markup(str(disease_dic[prediction]))
#             return render_template('disease-result.html', prediction=prediction, title=title)
#         except:
#             pass
#     return render_template('disease.html', title=title)


# # ===============================================================================================
# if __name__ == '__main__':
#     app.run(debug=True)
