from flask import Flask, request, g, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_cors import CORS
import sqlite3 as sql
import json
import random

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///confusing_answer.db'

db = SQLAlchemy(app)

CORS(app)
api = Api(app)

### ------- All the tables as per the DB design from the link : https://prnt.sc/12fcv8v  ------- ###

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))


class Answers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(200), db.ForeignKey(User.id), nullable=False)
    question_id = db.Column(db.String(200), primary_key=True)
    time_taken = db.Column(db.Integer)


class TextAnswers(db.Model):
    answer_id = db.Column(
        db.Integer, db.ForeignKey(Answers.id), nullable=False)
    text = db.Column(db.String(200), primary_key=True)


class MarkedWords(db.Model):
    answer_id = db.Column(
        db.Integer, db.ForeignKey(Answers.id), nullable=False)
    question_id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(200), primary_key=True)

### ------- end of the table models  ------- ###


### ------- Creating user Api  ------- ###
@app.route('/user', methods=['POST'])
def createUser():
    msg = "error"
    try:
        req_data = request.get_json()
        name = req_data['name']
        user = User(name =name)
        db.session.add(user)
        db.session.commit()
        print(user.id)
        msg = "Record added successfully"
    except:
        msg = "error in insert operation"
    finally:
        return msg


### ------- retreiving user by id  ------- ###
@app.route('/user/<id>')
def getUser(id):
    try:
        response = []
        user = User.query.filter_by(id=id).first()
        response.append({"id":user.id, "name" : user.name})
        return jsonify(response)
    except:
        return "There are no users with the given id"
    

### ------- retrieving all users  ------- ###
@app.route('/user/*')
def getAllUser():
    try:
        response = []
        users = User.query.all()
        for user in users:
            response.append({"id":user.id, "name" : user.name})
        return jsonify(response)
    except:
        return "There are no users"


### ------- Adding the user inputs to database tables  ------- ###
@app.route('/answered', methods=['POST'])
def answered():
    msg = "error"
    try:
        req_data = request.get_json()
        question_id = req_data['id']
        marked_word = req_data['markedWords']
        text = req_data['inputText']
        time_spent = req_data['timeSpent']
        user_id = req_data['userId']

        answerId = Answers.query.count() + 1
        print(answerId)

        answers = Answers(id = answerId,user_id= user_id, question_id = question_id, time_taken = time_spent)
        db.session.add(answers)
        db.session.commit()

        textAnswers = TextAnswers(answer_id= answerId, text = text )
        db.session.add(textAnswers)
        db.session.commit()

        for word in marked_word:
           markedWords = MarkedWords(answer_id = answerId, question_id = question_id, word= word)
           db.session.add(markedWords)
           db.session.commit()
        
        msg = "Record added successfully"

    except:
        msg = "error in insert operation"

    finally:
        return msg


### ------- Opening JSON file  ------- ###
message_file = open('messages.json',)


### ------- returns JSON object as a dictionary  ------- ###
messages = json.load(message_file)


### ------- Generates random question from the JSON file   ------- ###
@app.route('/question')
def question():
    n = random.randint(0, len(messages)-1)
    message = messages[n]
    return message

if __name__ == "__main__":
    app.run(debug=True)
