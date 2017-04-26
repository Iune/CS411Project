from flask import Flask
from flask import jsonify, render_template, abort, request, redirect, url_for, jsonify
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, \
                                login_required, login_user, logout_user 
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from colour import Color
import time
import datetime
import nltk

# App Configuration
app = Flask(__name__)
app.secret_key = '&~\xcb\xa1 \xc35d\x00m7\xacc\xe9A\xb5N\xdb\x0b\n8\x9b"\xa4'

# MySQL Configurations
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'c$411Pr0J'
app.config['MYSQL_DB'] = 'RateMyClassroomData'
app.config['MYSQL_HOST'] = 'localhost'
mysql = MySQL(app)

# Login Configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class Database:
    @staticmethod
    def update_classroom_rating(building, room):
        cursor = mysql.connection.cursor()  
        cursor.execute("SELECT AVG(Rating) FROM Review WHERE BldgName = %s AND ClassroomNumber = %s", (building, room))
        average_rating = cursor.fetchall()[0][0]
        cursor.execute("UPDATE Classroom SET AverageRating = %s WHERE BldgName = %s AND RoomNumber = %s", (average_rating, building, room))
        mysql.connection.commit()

class User(UserMixin):
    def __init__ (self, name, password):
        self.name = name
        self.password = password

    def get_id(self):
        return self.name

    @staticmethod
    def save_user(user):
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO User (Name, PasswordHash) VALUES (%s, %s)", (user.name, user.password))  
            mysql.connection.commit()   
        except mysql_exceptions.IntegrityError:
            return None     

    @staticmethod
    def get_user(user_name):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM User WHERE Name = %s", (user_name,))
        user_info = list(cursor.fetchall())
        if len(user_info) == 0:
            return None
        else:
            return User(user_info[0][0], user_info[0][1])

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

@app.route('/search_keys', methods=['POST'])
def search_keys():
    building_name = request.form['buildingNameInput']
    travel_method = request.form['travelMethod']
    travel_time = request.form['travelTime']
    search_tags = request.form.getlist('tags')

    cursor = mysql.connection.cursor()  
    if travel_method == "walking":
        cursor.execute("SELECT DISTINCT SecondBuildingName FROM Travel WHERE FirstBuildingName = %s AND WalkTime <= %s", (building_name, travel_time))  
    else:
        cursor.execute("SELECT DISTINCT SecondBuildingName FROM Travel WHERE FirstBuildingName = %s AND BikeTime <= %s", (building_name, travel_time))  

    close_buildings = [building[0] for building in cursor.fetchall()]

    cursor.execute("SELECT * FROM Tags")
    tags_list = cursor.fetchall()

    classes = {}
    for tag in tags_list:
        building = tag[3]
        room = tag[4]

        try:
            classes["{} {}".format(room, building)]['tags'].add(tag[2])
        except KeyError:
            classes["{} {}".format(room, building)] = {
                'building': building,
                'room': room,
                'tags': set([tag[2]])
            }

    for classroom in classes.values():
        classroom['tags'] = list(classroom['tags'])

    for tag in search_tags:
        new_classes = {}
        for room in classes.keys():
            if tag in classes[room]['tags']:
                new_classes[room] = classes[room]
            else:
                continue
        classes = new_classes

    

    classrooms = []
    for building in close_buildings:
        cursor.execute("SELECT DISTINCT RoomNumber FROM Classroom WHERE BldgName = %s", (building,))  
        building_rooms = cursor.fetchall() 
        classrooms += [{'building': building, 'room': room[0]} for room in building_rooms]  


    return jsonify(name=building_name, method=travel_method, time=travel_time, tags=classes, distances=close_buildings, classrooms=classrooms)

@app.route('/sign_up', methods=['GET'])
def sign_up():
    return render_template('register-bulma.html', title="Sign Up")

@app.route('/register', methods=['POST'])
def register():
    user_name = request.form['userNameText']
    password = request.form['passwordText']
    user = User(user_name, password)
    User.save_user(user)
    return redirect(url_for('index'))

@login_manager.user_loader
def load_user(user_name):
    return User.get_user(user_name)

# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['userNameText']
        password = request.form['passwordText']        

        user = User.get_user(username)
        login_user(user)
        return redirect(url_for('index'))
    else:
        return render_template('login-bulma.html', title="Login")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/add_review', methods=['POST'])
def add_review():
    building_name = request.form['buildingNameInput']
    room_number = request.form['roomNumberInput']
    user_name = request.form['userNameText']
    rating = request.form['ratingSelectInput']
    review_text = request.form['reviewText']
    tags = request.form.getlist('tags')

    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    
    cursor = mysql.connection.cursor()  
    cursor.execute("INSERT INTO Review (Rating, DateTime, Text, UserName, ClassroomNumber, BldgName) VALUES (%s, %s, %s, %s, %s, %s)", (rating, timestamp, review_text, user_name, room_number, building_name))  
    mysql.connection.commit()

    for tag in tags:
        cursor.execute("INSERT INTO Tags (DateTime, Username, TagName, BldgName, RoomNumber) VALUES (%s, %s, %s, %s, %s)", (timestamp, user_name, tag, building_name, room_number))
        mysql.connection.commit()

    # Update Average Classroom Rating
    Database.update_classroom_rating(building_name, room_number)

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

        Database.update_classroom_rating(building_name, room_number)
        return redirect(url_for("room", building=building, classname=classroom))
        
    elif request.form['submit'] == 'delete':
        user_name = request.form['reviewUserName']
        building = request.form['reviewBuilding']
        classroom = request.form['reviewClassroom']
        cursor.execute("DELETE FROM Review WHERE UserName = %s AND BldgName = %s AND ClassroomNumber = %s", (user_name, building, classroom))
        mysql.connection.commit()
        
        Database.update_classroom_rating(building_name, room_number)
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

    # Get the Classroom Tags
    classroom_tags = []

    # Load reviews
    cursor.execute("SELECT * FROM Review WHERE BldgName = %s AND ClassroomNumber = %s", (building, classname)) 
    reviews_list = cursor.fetchall()
    reviews = []
    for review in reviews_list:
        tags = []
        cursor.execute("SELECT TagName FROM Tags WHERE UserName = %s AND DateTime = %s", (review[3], review[1])) 
        tags_list = cursor.fetchall()
        tags_list = [tag[0] for tag in tags_list]
        reviews.append({
            'userName': review[3],
            'text': review[2],
            'rating': review[0],
            'ratingStars': "{}{}".format(review[0]*"★", (5-review[0])*"☆"),
            'tags': tags_list,
            'time': review[1]
        })
        for tag in tags_list:
            classroom_tags.append(tag)
    classroom_tags = list(set(classroom_tags))
    classroom_data['tags'] = classroom_tags

    # Get Word Sentiments for Word Cloud
    words = {}
    sid = SentimentIntensityAnalyzer()
    sentiments = []
    num_words = 0
    for review in reviews:
        tokens = word_tokenize(review['text'])
        tokens = [word for word in tokens if word not in ['.', ',', ';', '!', '?', '--', '...', ":", '\'s', '(', ')']]
        tokens = [word for word in tokens if not word.isnumeric()]
        tokens = [word for word in tokens if word not in nltk.corpus.stopwords.words()]

        # review['text'].replace(",", "").replace(".", "").replace("!", "").split(" ")
        num_words += len(tokens)
        for word in tokens:
            word = word.lower()
            sentiment = sid.polarity_scores(word)['compound']
            sentiments.append(sentiment)
            try:
                words[word]['freq'] += 10
            except KeyError:
                words[word] = {'freq': 10, "word": word}

    if num_words == 0:
        avg_rating = 0
    else:
        avg_rating = 0.5 + (float(sum(sentiments)/num_words)/1.0)
    color = Color(hue=avg_rating*0.4, saturation=0.9, luminance=0.9).hex
    words = [[word['word'], word['freq']] for word in words.values()]

    return render_template('classroom-bulma.html', title="{} {}".format(classroom_data['roomNumber'], classroom_data['buildingName']), classroom=classroom_data, reviews=reviews, sentiments=words, color=color)

if __name__ == "__main__":
    app.run(debug=True)
