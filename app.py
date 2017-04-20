from flask import Flask
from flask import jsonify, render_template, abort, request, redirect, url_for
from flask_mysqldb import MySQL
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import time
import datetime

app = Flask(__name__)
# MySQL Configurations
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'c$411Pr0J'
app.config['MYSQL_DB'] = 'RateMyClassroomData'
app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'testuser'
# app.config['MYSQL_PASSWORD'] = 'test123'
# app.config['MYSQL_DB'] = 'TESTDB'
# app.config['MYSQL_HOST'] = 'localhost'
mysql = MySQL(app)

@app.route('/')
def index():
    cursor = mysql.connection.cursor()
    
    cursor.execute("SELECT * FROM Building")
    buildings  = list(cursor.fetchall())
    buildings_data = []
    for building in buildings:
        buildings_data.append({
            'name': building[0],
            'address': building[1],
            'className': building[0].replace(' ', '')        
        })
    
    cursor.execute("SELECT * FROM Classroom")
    classrooms = list(cursor.fetchall())
    classrooms_data = []
    for classroom in classrooms:
        classrooms_data.append({
            'buildingName': classroom[0],
            'buildingClassName' : classroom[0].replace(' ', ''),
            'roomNumber' : classroom[2]
        })
    return render_template('index-bulma.html', title="Home", buildings=buildings_data, classrooms=classrooms_data)

@app.route('/search', methods=['POST'])
def search():
    building_name = request.form['buildingNameInput']
    classroom_name = request.form['classroomNameInput']
    return redirect(url_for('room', building=building_name, classname=classroom_name))

@app.route('/add_review', methods=['POST'])
def add_review():
    building_name = request.form['buildingNameInput']
    room_number = request.form['roomNumberInput']
    user_name = request.form['userNameText']
    rating = request.form['ratingSelectInput']
    review_text = request.form['reviewText']

    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    
    cursor = mysql.connection.cursor()  
    cursor.execute("INSERT INTO Review (Rating, DateTime, Text, UserName, ClassroomNumber, BldgName) VALUES (%s, %s, %s, %s, %s, %s)", (rating, timestamp, review_text, user_name, room_number, building_name))  
    mysql.connection.commit()
    return redirect(url_for('room', building=building_name, classname=room_number))

@app.route('/handle_review', methods=['POST'])
def handle_review():
    cursor = mysql.connection.cursor()
    if request.form['submit'] == 'edit':
        user_name = request.form['reviewUserName']
        building = request.form['reviewBuilding']
        classroom = request.form['reviewClassroom']
        
        rating = request.form['reviewRating']
        review_text = request.form['reviewText']                
        cursor.execute("UPDATE Review SET Rating = %s WHERE UserName = %s AND BldgName = %s AND ClassroomNumber = %s", (rating, user_name, building, classroom))
        cursor.execute("UPDATE Review SET Text = %s WHERE UserName = %s AND BldgName = %s AND ClassroomNumber = %s", (review_text, user_name, building, classroom))
        mysql.connection.commit()

        return redirect(url_for("room", building=building, classname=classroom))
        
    elif request.form['submit'] == 'delete':
        user_name = request.form['reviewUserName']
        building = request.form['reviewBuilding']
        classroom = request.form['reviewClassroom']
        cursor.execute("DELETE FROM Review WHERE UserName = %s AND BldgName = %s AND ClassroomNumber = %s", (user_name, building, classroom))
        mysql.connection.commit()
        return redirect(url_for("room", building=building, classname=classroom))
    else:
        return 'Do nothing'

@app.route('/room/<building>/<classname>')
def room(building, classname):
    cursor = mysql.connection.cursor()
    # Load classroom data
    cursor.execute("SELECT * FROM Classroom WHERE BldgName = %s AND RoomNumber = %s", (building, classname)) 
    classrooms = cursor.fetchall()
    classroom = classrooms[0]
    classroom_data = {
        'buildingName': classroom[0],
        'buildingAddress': classroom[1],
        'roomNumber': classroom[2],
        'averageRating': classroom[3],
        'tags' : []
    }
    # for classroom in classrooms:
    #     if(classroom[4])
    #         classroom_data['tags'].append(classroom[4])
    # Load reviews
    cursor.execute("SELECT * FROM Review WHERE BldgName = %s AND ClassroomNumber = %s", (building, classname)) 
    reviews_list = cursor.fetchall()
    reviews = []
    for review in reviews_list:
        tags = []
        cursor.execute("SELECT * FROM TagsInReview WHERE UserName = %s AND DateTime = %s", (review[3], review[1])) 
        tags_list = cursor.fetchall()
        reviews.append({
            'userName': review[3],
            'text': review[2],
            'rating': review[0],
            'ratingStars': "{}{}".format(review[0]*"★", (5-review[0])*"☆"),
            'tags': tags_list,
            'time': review[1]
        })

    words = {}
    sid = SentimentIntensityAnalyzer()
    for review in reviews:
        tokens = review['text'].split(" ")
        for word in tokens:
            try:
                words[word]['count'] += 1
            except KeyError:
                sentiment = sid.polarity_scores(word)['compound']
                sentiment_type = "positive"
                if sentiment < 0:
                    sentiment_type = "negative"
                words[word] = {'count': 1, 'sentiment': sentiment_type }

    return render_template('classroom-bulma.html', title="{} {}".format(classroom_data['roomNumber'], classroom_data['buildingName']), classroom=classroom_data, reviews=reviews, sentiments=words)

if __name__ == "__main__":
    app.run(debug=True)
