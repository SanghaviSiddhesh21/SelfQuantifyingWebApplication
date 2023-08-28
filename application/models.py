from .database import db
from flask_login import UserMixin

class User(db.Model,UserMixin):
  __tablename__='user'
  id=db.Column(db.Integer,primary_key=True,autoincrement=True)
  fname=db.Column(db.String,nullable=False)
  lname=db.Column(db.String,nullable=False)
  birthdate=db.Column(db.Date,nullable=False)
  username=db.Column(db.String(20),nullable=False,unique=True)
  password=db.Column(db.String(80),nullable=False)
  user_tracker_relationship=db.relationship("Tracker",secondary='user_tracker')
class Tracker(db.Model):
  __tablename__='tracker'
  tracker_id=db.Column(db.Integer,primary_key=True,autoincrement=True,nullable=False,unique=True)
  tracker_name=db.Column(db.String,nullable=False,unique=True)
class User_tracker(db.Model):
  __tablename__='user_tracker'
  user_id=db.Column(db.Integer,db.ForeignKey("user.id"),primary_key=True)
  tracker_id=db.Column(db.Integer,db.ForeignKey("tracker.tracker_id"),primary_key=True)
class Food_nutrients(db.Model):
  __tablename__='food_nutrients'
  food_id=db.Column(db.Integer,primary_key=True,autoincrement=True,nullable=False,unique=True)
  food_name=db.Column(db.String,nullable=False,unique=True)
  Kcal_per_gram=db.Column(db.Float,nullable=False)
class User_food_log(db.Model):
  __tablename__='user_food_log'
  user_food_log_id=db.Column(db.Integer,primary_key=True,autoincrement=True,nullable=False,unique=True)
  user_id=db.Column(db.Integer,db.ForeignKey("user.id"))
  food_id=db.Column(db.Integer,db.ForeignKey("food_nutrients.food_id"))
  quantity_taken=db.Column(db.Float,nullable=False)
  calorie_input=db.Column(db.Float,nullable=False)
  date=db.Column(db.Date)
class Excercise_calorie(db.Model):
  __tablename__='excercise_calorie'
  exercise_id=db.Column(db.Integer,autoincrement=True,primary_key=True,nullable=False,unique=True)
  exercise_name=db.Column(db.String,unique=True,nullable=False)
  avg_calorie_burnt_per_min=db.Column(db.Float,nullable=False)
class Run_log(db.Model):
  __tablename__='run_log'
  run_log_id=db.Column(db.Integer,autoincrement=True,primary_key=True,unique=True,nullable=False)
  user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
  date=db.Column(db.Date,nullable=False)
  start_time=db.Column(db.DateTime,nullable=False)
  end_time=db.Column(db.DateTime,nullable=False)
  duration=db.Column(db.Float,nullable=False)
  calorie_burnt=db.Column(db.Float,nullable=False)
class Walk_log(db.Model):
  __tablename__='walk_log'
  walk_log_id=db.Column(db.Integer,autoincrement=True,primary_key=True,unique=True,nullable=False)
  user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
  date=db.Column(db.Date,nullable=False)
  start_time=db.Column(db.DateTime,nullable=False)
  end_time=db.Column(db.DateTime,nullable=False)
  duration=db.Column(db.Float,nullable=False)
  calorie_burnt=db.Column(db.Float,nullable=False)
class Expense_criteria(db.Model):
  __tablename__='expense_criteria'
  criteria_id=db.Column(db.Integer,autoincrement=True,primary_key=True,unique=True,nullable=False)
  criteria_name=db.Column(db.String,nullable=False,unique=True)
class Expenses(db.Model):
  __tablename__='expenses'
  expense_id=db.Column(db.Integer,autoincrement=True,primary_key=True,nullable=False,unique=True)
  user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
  expense_criteria_id=db.Column(db.Integer,db.ForeignKey('expense_criteria.criteria_id'),nullable=False)
  amount=db.Column(db.Float,nullable=False)
  date=db.Column(db.Date,nullable=False)