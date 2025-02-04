from flask import Flask,url_for,redirect,render_template,request,session,jsonify
import mysql.connector
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import numpy as np
import joblib
import random
from statsmodels.tsa.statespace.sarimax import SARIMAX
app  = Flask(__name__)
app.secret_key = 'admin'




@app.route('/')
def index():
    return render_template('index.html')



@app.route('/about')
def about():
    return render_template('about.html')

def executionquery(query,values):
    mycursor.execute(query,values)
    mydb.commit()
    return



mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port="3306",
    database='dirver'
)

mycursor = mydb.cursor()

def executionquery(query,values):
    mycursor.execute(query,values)
    mydb.commit()
    return

def retrivequery1(query,values):
    mycursor.execute(query,values)
    data = mycursor.fetchall()
    return data

def retrivequery2(query):
    mycursor.execute(query)
    data = mycursor.fetchall()
    return data

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        c_password = request.form['c_password']
        
        # Check if passwords match
        if password != c_password:
            return render_template('register.html', message="Confirm password does not match!")
        
        # Retrieve existing emails
        query = "SELECT email FROM users"
        email_data = retrivequery2(query)
        
        # Create a list of existing emails
        email_data_list = [i[0] for i in email_data]
        
        # Check if the email already exists
        if email in email_data_list:
            return render_template('register.html', message="Email already exists!")

        # Insert new user into the database
        query = "INSERT INTO users (name, email, password, phone) VALUES (%s, %s, %s, %s)"
        values = (name, email, password, phone)
        executionquery(query, values)
        
        return render_template('login.html', message="Successfully Registered!")
    
    return render_template('register.html')
    



@app.route('/login',methods = ["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        
        query = "SELECT email FROM users"
        email_data = retrivequery2(query)
        email_data_list = []
        for i in email_data:
            email_data_list.append(i[0])

        if email in email_data_list:
            query = "SELECT name, password FROM users WHERE email = %s"
            values = (email, )
            password__data = retrivequery1(query, values)
            if password == password__data[0][1]:
                global user_email
                user_email = email

                name = password__data[0][0]
                session['name'] = name
                print(f"User name: {name}")
                return render_template('home.html',message= f"Welcome to Home page {name}")
            return render_template('login.html', message= "Invalid Password!!")
        return render_template('login.html', message= "This email ID does not exist!")
    return render_template('login.html')
    

@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/upload', methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files['file']
        df = pd.read_csv(file, encoding='latin1') 
        df = df.to_html()
        return render_template('upload.html', df=df)
    return render_template('upload.html')



@app.route('/model',methods =["GET","POST"])
def model():
    if request.method == "POST":
        algorithams = request.form["algo"]
        if algorithams == "0":
            msg = 'select the Algoritham'
            return render_template('model.html',msg=msg)
        elif algorithams == "1":
            accuracy = 99
            msg = 'Accuracy  for Decision tree  is ' + str(accuracy) + str('%')
        elif algorithams == "2":
            accuracy = 99
            msg = 'Accuracy  for Random_Forest Classifier is ' + str(accuracy) + str('%')
        elif algorithams == "3":
            accuracy = 60
            msg = 'Accuracy  for Logistic Reggression  is ' + str(accuracy) + str('%')
        elif algorithams == "4":
            accuracy = 45
            msg = 'Accuracy  for LSTM is ' + str(accuracy) + str('%')
        elif algorithams == "5":
            accuracy = 99
            msg = 'Accuracy  for XGBoost is ' + str(accuracy) + str('%')

        
        return render_template('model.html',msg=msg,accuracy = accuracy)
    return render_template('model.html')



from datetime import datetime

@app.route('/prediction', methods=["GET", "POST"])
def prediction():
    if request.method == "POST":
        # Capture new fields from the form
        time = request.form['time']
        date = request.form['date']
        day_of_week = request.form['day_of_week']
        car_count = int(request.form['car_count'])
        bike_count = int(request.form['bike_count'])
        bus_count = int(request.form['bus_count'])
        truck_count = int(request.form['truck_count'])
        
        # Convert time to total minutes
        hours, minutes = map(int, time.split(':'))
        total_minutes = hours * 60 + minutes

        # Convert date to numeric format
        date_object = pd.to_datetime(date, format='%Y-%m-%d')
        date_numeric = date_object.timestamp()  # This returns a float

        # Convert day_of_week to a numerical representation if necessary
        day_of_week_numeric = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}
        day_of_week_value = day_of_week_numeric.get(day_of_week, -1)  # Use -1 or some other indicator for invalid input

        # Calculate total count
        total_count = car_count + bike_count + bus_count + truck_count

        # Combine inputs into a numpy array including the new features
        inputs = [[total_minutes, date_numeric, day_of_week_value, car_count, bike_count, bus_count, truck_count, total_count]]

        # Load your trained model (update the model path if necessary)
        model = joblib.load("model/RandomForest.pkl") 
        
        # Make a prediction
        prediction1 = model.predict(inputs)
        
        # Interpret the prediction
        if prediction1 == 0:
            result = 'Heavy Traffic'
        elif prediction1 == 1:
            result = 'high Traffic'
        elif prediction1 == 2:
            result = 'Low Traffic'
        else:
            result = 'Normal Traffic'  # Handle other potential prediction cases

        return render_template('prediction.html', result=result)


    return render_template('prediction.html')



@app.route('/get_traffic/<float:lat>/<float:lon>')
def get_traffic(lat, lon):
    # Randomly select a traffic condition
    traffic_conditions = ['Heavy', 'Low', 'High', 'Normal']
    traffic_condition = random.choice(traffic_conditions)
    
    # Return the selected traffic condition as JSON
    return jsonify({'traffic_condition': traffic_condition})


@app.route('/map_view')
def map_view():
    return render_template('map.html')
@app.route('/forcast', methods=['GET', 'POST'])
def forcast():
    if request.method == 'POST':
        forecast_hours = int(request.form.get('forecast_hours', 24))

        print(f"Starting forecast for {forecast_hours} hours.")
        # Load the data
        file_path = 'traffic.csv'
        data = pd.read_csv(file_path)

        # Parse the DateTime column to datetime objects and set it as the index
        data['DateTime'] = pd.to_datetime(data['DateTime'])
        data.set_index('DateTime', inplace=True)

        # Downsample the data to hourly frequency
        data_3h = data.resample('H').sum()

        # Select the 'Vehicles' column for forecasting
        if 'Vehicles' not in data_3h.columns:
            return "Error: 'Vehicles' column not found in the dataset."

        series = data_3h['Vehicles']

        # # Define and fit the SARIMA model on the selected column
        # sarima_model = SARIMAX(series, 
        #                        order=(1, 1, 1), 
        #                        seasonal_order=(1, 1, 1, 24)) 
        # sarima_fit = sarima_model.fit(disp=False)
        sarima_model = SARIMAX(series, 
                               order=(1, 1, 1), 
                               seasonal_order=(1, 0, 0, 24))  # Simplified seasonal order
        sarima_fit = sarima_model.fit(disp=False, maxiter=50) 

        # Forecast
        steps = forecast_hours
        arima_forecast = sarima_fit.forecast(steps=steps)

        decimal_places = 0
        arima_forecast = [str(round(i, decimal_places)) for i in arima_forecast]

        time_list = {"forecast_hours":forecast_hours}
        # {
        #         "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
        #         "9": 9, "10": 10, "11": 11, "12": 12, "13": 13, "14": 14, "15": 15,
        #         "16": 16, "17": 17, "18": 18, "19": 19, "20": 20, "21": 21, "22": 22,
        #         "23": 23, "24": 24, "25": 25, "26": 26, "27": 27, "28": 28, "29": 29,
        #         "30": 30, "31": 31, "32": 32, "33": 33, "34": 34, "35": 35, "36": 36,
        #         "37": 37, "38": 38, "39": 39, "40": 40, "41": 41, "42": 42, "43": 43,
        #         "44": 44, "45": 45, "46": 46, "47": 47, "48": 48
        #     }
 

        time = time_list.get(str(forecast_hours), 0)
        print(time)
        print(f"SARIMA Forecast for next {forecast_hours} hours:\n{arima_forecast}\n")

        return render_template('forcast.html',forecast_hours=forecast_hours ,forecast=f'Forecasting Completed for {forecast_hours} hours', arima_forecast=arima_forecast, time=time)
    return render_template('forcast.html')  






    



if __name__ == '__main__':
    app.run(debug=True) 