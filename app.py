from flask import Flask
from flask import jsonify, render_template, abort, request
from flask_mysqldb import MySQL

app = Flask(__name__)
# MySQL Configurations
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'c$411Pr0J'
app.config['MYSQL_DB'] = 'RateMyClassroomData'
app.config['MYSQL_HOST'] = 'localhost'
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
    return render_template('index.html', title="Home", buildings=buildings_data, classrooms=classrooms_data)

@app.route('/room/<building>/<classname>')
def view_classroom(building, classname):
    cursor = mysql.connection.cursor()
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
    for classroom in classrooms:
        classroom_data['tags'].append(classroom[4])

    return render_template('classroom.html', title="Classroom", classroom=classroom_data)


if __name__ == "__main__":
    app.run(debug=True)
