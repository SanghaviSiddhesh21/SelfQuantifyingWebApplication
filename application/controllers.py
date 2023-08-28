from datetime import datetime,date
from flask import Flask, redirect,render_template, request, session,url_for
from flask import current_app as app
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user
from flask_bcrypt import Bcrypt
from sqlalchemy import func,desc
import pandas as pd
import matplotlib.pyplot as plt
from application.models import *
from application.functions import *

bcrypt=Bcrypt(app)
login_manager=LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
  return User.query.get(int(id))

@app.route('/',methods=['GET','POST'])
def home():
  return render_template('home.html')

@app.route('/login',methods=['GET','POST'])
def login():
  if request.method=='GET':
    return render_template('login.html')
  elif request.method=='POST':
    (username,password)=(request.form['username'],request.form['password'])
    userexist=User.query.filter_by(username=username).first()
    if userexist:
      if bcrypt.check_password_hash(userexist.password,password):
        login_user(userexist)
        return redirect(url_for('dashboard'))
      else:
        return redirect(url_for('login'))
    else:
      return redirect(url_for('login'))

@app.route('/register',methods=['GET','POST'])
def register():
  if request.method=='GET':
    return render_template('register.html')
  elif request.method=='POST':
    (fname,lname,dob,username,password,repass)=(request.form['fname'],request.form['lname'],request.form['dob'],request.form['username'],request.form['password'],request.form['repass'])
    if password!=repass:
      return redirect(url_for('register'))
    userexist=User.query.filter_by(username=username).first()
    if userexist:
      return redirect(url_for('register'))
    else:
      hashedpassword=bcrypt.generate_password_hash(password)
      dob=datetime.strptime(dob,'%Y-%m-%d')
      new_user=User(fname=fname,lname=lname,birthdate=dob,username=username,password=hashedpassword)
      try:
        db.session.add(new_user)
        db.session.flush()
      except Exception as error:
        db.session.rollback()
        return redirect(url_for('register'))
      db.session.commit()
      db.session.close()
    return redirect(url_for('login'))

@app.route('/dashboard',methods=['GET','POST'])
@login_required
def dashboard():
  if request.method=='GET':
    user_data=User.query.filter(User.id==current_user.id).first()
    tracker_list=User_tracker.query.with_entities(User_tracker.tracker_id).filter_by(user_id=current_user.id).all()
    if tracker_list:
      tracker_list_=[]
      for i in tracker_list:
        tracker_list_.append(i[0])
      all_tracker=Tracker.query.filter(Tracker.tracker_id.in_(tracker_list_)).all()
      return render_template('dashboard_with_tracker.html',data=all_tracker,username=user_data.username,fname=user_data.fname,lname=user_data.lname,dob=user_data.birthdate)
    else:
      return render_template('dashboard_without_tracker.html',username=user_data.username,fname=user_data.fname,lname=user_data.lname,dob=user_data.birthdate)


@app.route('/add_tracker',methods=['GET','POST'])
@login_required
def tracker_adder():
  if request.method=='GET':
    tracker_list=User_tracker.query.with_entities(User_tracker.tracker_id).filter_by(user_id=current_user.id).all()
    if tracker_list:
      tracker_list_=[]
      for i in tracker_list:
        tracker_list_.append(i[0])
      all_tracker=Tracker.query.filter(Tracker.tracker_id.not_in(tracker_list_)).all()
      return render_template("tracker_adder.html",data=all_tracker)
    else:
      all_tracker=Tracker.query.all()
      return render_template("tracker_adder.html",data=all_tracker)
  elif request.method=='POST':
    tracker_selected=request.form.getlist('tracker')
    tracker_to_add=[]
    for i in tracker_selected:
      tracker_to_add.append(int(i))
    try:
      for i in tracker_to_add:
        x=User_tracker(user_id=current_user.id,tracker_id=i)
        db.session.add(x)
        db.session.flush()
    except:
      db.session.rollback()
    db.session.commit()
    db.session.close()
    return redirect(url_for('dashboard'))

@app.route('/<int:tracker_id>/remove',methods=['GET','POST'])
@login_required
def remove_tracker(tracker_id):
  if request.method=='GET':
    try:
      User_tracker.query.filter_by(tracker_id=tracker_id,user_id=current_user.id).delete()
      db.session.flush()
    except:
      db.session.rollback()
    db.session.commit()
    db.session.close()
    return redirect(url_for('dashboard'))

@app.route('/open_dashboard_1',methods=['GET','POST'])
@login_required
def food_tracker_open_dashboard():
  if request.method=='GET':
    food_log=db.session.query(User_food_log.date,func.sum(User_food_log.calorie_input).label('total_Kcal')).filter(User_food_log.user_id==current_user.id).group_by(User_food_log.date).all()
    if food_log:
      time=[]
      energy=[]
      for i in food_log:
        time.append(i[0])
        energy.append(i[1])
      graph={}
      graph['time']=time
      graph['energy']=energy
      df=pd.DataFrame(graph)
      df.plot(x='time',y='energy',figsize=(15,5))
      plt.savefig(f"static/food_dashboard.jpg")
      food_log=db.session.query(User_food_log.user_food_log_id,User_food_log.food_id,User_food_log.quantity_taken,User_food_log.calorie_input,User_food_log.date,Food_nutrients.food_name).join(Food_nutrients,User_food_log.food_id==Food_nutrients.food_id).filter(User_food_log.user_id==current_user.id).all()
      return render_template('food_tracker_open_dashboard_with_logs.html',data=food_log)
    else:
      return render_template('food_tracker_open_dashboard_without_logs.html')
@app.route('/add_food_track_entry',methods=['GET','POST'])
@login_required
def add_food_track_entry():
  if request.method=='GET':
    all_food_items=Food_nutrients.query.all()
    return render_template('add_food_tracker_entry.html',data=all_food_items)
  elif request.method=='POST':
    (food_selected,quantity_consumed)=(request.form.get('food'),request.form['quantity'])
    quantity_consumed=float(quantity_consumed)
    f_id=Food_nutrients.query.with_entities(Food_nutrients.food_id,Food_nutrients.Kcal_per_gram).filter(Food_nutrients.food_name==food_selected).first()
    food_id=f_id['food_id']
    food_cal=f_id['Kcal_per_gram']
    date_=date.today()
    food_log=User_food_log(user_id=current_user.id,food_id=food_id,quantity_taken=(quantity_consumed),calorie_input=(quantity_consumed*food_cal),date=date_)
    try:
      db.session.add(food_log)
      db.session.flush()
    except:
      db.session.rollback()
    db.session.commit()
    db.session.close()
    return redirect(url_for('food_tracker_open_dashboard'))
@app.route('/<int:log_id>/delete_food_track_entry',methods=['GET','POST'])
@login_required
def delete_food_entry(log_id):
  if request.method=='GET':
    try:
      User_food_log.query.filter_by(user_food_log_id=log_id).delete()
      db.session.flush()
    except:
      db.session.rollback()
    db.session.commit()
    db.session.close()
    return redirect(url_for('food_tracker_open_dashboard'))

@app.route('/<int:log_id>/update_food_track_entry',methods=['GET','POST'])
@login_required
def update_food_entry(log_id):
  if request.method=='GET':
    all_food_items=Food_nutrients.query.all()
    return render_template('food_entry_update.html',data=all_food_items,log_id=log_id)
  elif request.method=='POST':
    (food_selected,quantity_consumed,date_)=(request.form.get('food'),request.form['quantity'],request.form['date_'])
    date_=datetime.strptime(date_,'%Y-%m-%d')
    quantity_consumed=float(quantity_consumed)
    f_id=Food_nutrients.query.with_entities(Food_nutrients.food_id,Food_nutrients.Kcal_per_gram).filter(Food_nutrients.food_name==food_selected).first()
    food_id=f_id['food_id']
    food_cal=f_id['Kcal_per_gram']
    update_entry=User_food_log.query.filter_by(user_food_log_id=log_id).first()
    try:
      update_entry.food_id=food_id
      db.session.flush()
      update_entry.quantiy_taken=quantity_consumed
      db.session.flush()
      update_entry.calorie_input=quantity_consumed*food_cal
      db.session.flush()
      update_entry.date=date_
      db.session.flush()
    except:
      db.session.rollback()
    db.session.commit()
    db.session.close()
    return redirect(url_for('food_tracker_open_dashboard'))

@app.route('/open_dashboard_2',methods=['GET','POST'])
@login_required
def run_tracker_open_dashboard():
  if request.method=='GET':
    run_log=db.session.query(Run_log.date,func.sum(Run_log.calorie_burnt)).filter(Run_log.user_id==current_user.id).group_by(Run_log.date).all()
    if run_log:
      time=[]
      energy=[]
      for i in run_log:
        time.append(i[0])
        energy.append(i[1])
      graph={}
      graph['time']=time
      graph['energy']=energy
      df=pd.DataFrame(graph)
      df.plot(x='time',y='energy',figsize=(15,5))
      plt.savefig(f"static/run_dashboard.jpg")
      run_log=db.session.query(Run_log.run_log_id,Run_log.user_id,Run_log.duration,Run_log.calorie_burnt,Run_log.date).filter(Run_log.user_id==current_user.id).all()
      return render_template('run_tracker_dashboard_with_logs.html',data=run_log)
    else:
      return render_template('run_tracker_dashboard_without_logs.html')

@app.route('/add_run_track_entry',methods=['GET','POST'])
@login_required
def add_run_track_entry():
  if  request.method=='GET':
    return render_template('run_start.html')
  elif request.method=='POST':
    entry=request.form['Run_entry']
    if (entry=='start_run'):
      run_log=Run_log(user_id=current_user.id,date=date.today(),start_time=datetime.now(),end_time=datetime.now(),duration=0,calorie_burnt=0)
      try:
        db.session.add(run_log)
        db.session.flush()
      except:
        db.session.rollback()
      log_id=run_log.run_log_id
      db.session.commit()
      db.session.close()
      return render_template('run_start.html',log_id=log_id)
    elif (entry=='end_run'):
      run_log_id=request.form['log_id']
      run_log=Run_log.query.filter_by(run_log_id=run_log_id).first()
      try:
        run_log.end_time=datetime.now()
        db.session.flush()
        difference=run_log.end_time-run_log.start_time
        difference_in_float=date_to_float(str(difference))
        run_log.duration=round(difference_in_float,2)
        db.session.flush()
        cal_per_min=Excercise_calorie.query.with_entities(Excercise_calorie.avg_calorie_burnt_per_min).filter(Excercise_calorie.exercise_id==1).first()
        cal=[]
        for i in cal_per_min:
          cal.append(float(i))
        cal_burned=round((cal[0]*difference_in_float),2)
        run_log.calorie_burnt=cal_burned
        db.session.flush()
      except:
        db.session.rollback()
      db.session.commit()
      db.session.close()
      return redirect(url_for('run_tracker_open_dashboard'))

@app.route('/<int:log_id>/delete_run_track_entry',methods=['GET','POST'])
@login_required
def delete_run_entry(log_id):
  try:
    Run_log.query.filter(Run_log.run_log_id==log_id).delete()
    db.session.flush()
  except:
    db.session.rollback()
  db.session.commit()
  db.session.close()
  return redirect(url_for('run_tracker_open_dashboard'))

@app.route('/open_dashboard_3',methods=['GET','POST'])
@login_required
def walk_tracker_open_dashboard():
  if request.method=='GET':
    walk_log=db.session.query(Walk_log.date,func.sum(Walk_log.calorie_burnt)).filter(Walk_log.user_id==current_user.id).group_by(Walk_log.date).all()
    if walk_log:
      time=[]
      energy=[]
      for i in walk_log:
        time.append(i[0])
        energy.append(i[1])
      graph={}
      graph['time']=time
      graph['energy']=energy
      df=pd.DataFrame(graph)
      df.plot(x='time',y='energy',figsize=(15,5))
      plt.savefig(f"static/walk_dashboard.jpg")
      walk_log=db.session.query(Walk_log.walk_log_id,Walk_log.user_id,Walk_log.duration,Walk_log.calorie_burnt,Walk_log.date).filter(Walk_log.user_id==current_user.id).all()
      return render_template('walk_tracker_dashboard_with_logs.html',data=walk_log)
    else:
      return render_template('walk_tracker_dashboard_without_logs.html')

@app.route('/add_walk_track_entry',methods=['GET','POST'])
@login_required
def add_walk_track_entry():
  if  request.method=='GET':
    return render_template('walk_start.html')
  elif request.method=='POST':
    entry=request.form['Walk_entry']
    if (entry=='start_walk'):
      walk_log=Walk_log(user_id=current_user.id,date=date.today(),start_time=datetime.now(),end_time=datetime.now(),duration=0,calorie_burnt=0)
      try:
        db.session.add(walk_log)
        db.session.flush()
      except:
        db.session.rollback()
      log_id=walk_log.walk_log_id
      db.session.commit()
      db.session.close()
      return render_template('walk_start.html',log_id=log_id)
    elif (entry=='end_walk'):
      walk_log_id=request.form['log_id']
      walk_log=Walk_log.query.filter_by(walk_log_id=walk_log_id).first()
      try:
        walk_log.end_time=datetime.now()
        db.session.flush()
        difference=walk_log.end_time-walk_log.start_time
        difference_in_float=round(date_to_float(str(difference)),2)
        walk_log.duration=difference_in_float
        db.session.flush()
        cal_per_min=Excercise_calorie.query.with_entities(Excercise_calorie.avg_calorie_burnt_per_min).filter(Excercise_calorie.exercise_id==2).first()
        cal=[]
        for i in cal_per_min:
          cal.append(float(i))
        cal_burned=round((cal[0]*difference_in_float),2)
        walk_log.calorie_burnt=cal_burned
        db.session.flush()
      except:
        db.session.rollback()
      db.session.commit()
      db.session.close()
      return redirect(url_for('walk_tracker_open_dashboard'))

@app.route('/<int:log_id>/delete_walk_track_entry',methods=['GET','POST'])
@login_required
def delete_walk_entry(log_id):
  try:
    Walk_log.query.filter(Walk_log.walk_log_id==log_id).delete()
    db.session.flush()
  except:
    db.session.rollback()
  db.session.commit()
  db.session.close()
  return redirect(url_for('walk_tracker_open_dashboard'))

@app.route('/open_dashboard_4',methods=['GET','POST'])
@login_required
def finance_tracker_open_dashboard():
  if request.method=='GET':
    all_expense=Expenses.query.with_entities(Expenses.expense_criteria_id,Expense_criteria.criteria_name,func.sum(Expenses.amount).label('total_amount')).join(Expense_criteria,Expense_criteria.criteria_id==Expenses.expense_criteria_id).filter(Expenses.user_id==current_user.id).group_by(Expenses.expense_criteria_id).all()
    if all_expense:
      criteria=[]
      total=[]
      for i in all_expense:
        criteria.append(i[1])
        total.append(i[2])
      graph={}
      graph['criteria']=criteria
      graph['total']=total
      df=pd.DataFrame(graph)
      df.plot(x='criteria',y='total',kind='bar',figsize=(8,4))
      plt.xticks(rotation=0, horizontalalignment="center")
      plt.savefig(f"static/finance_dashboard.jpg")
      return render_template('finance_tracker_dashboard_with_logs.html',data=all_expense)
    else:
      return render_template('finance_tracker_dashboard_without_logs.html')
  else:
    pass

@app.route('/expenditure_log',methods=['GET','POST'])
@login_required
def add_expenditure_entry():
  if request.method=='GET':
    all_criteria=Expense_criteria.query.all()
    return render_template('add_expense.html',data=all_criteria)
  elif request.method=='POST':
    (criteria_selected,amount_paid)=(request.form.get('criteria'),request.form['amount'])
    expense=Expenses(user_id=current_user.id,expense_criteria_id=criteria_selected,amount=amount_paid,date=date.today())
    try:
      db.session.add(expense)
      db.session.flush()
    except:
      db.session.rollback()
    db.session.commit()
    db.session.close()
    return redirect(url_for('finance_tracker_open_dashboard'))

@app.route('/<int:criteria_id>/List_of_particular_expenditure',methods=['GET','POST'])
@login_required
def List_of_particular_expenditure(criteria_id):
  if request.method=='GET':
    select_all_of_particular_criteria=Expenses.query.with_entities(Expenses.date,Expenses.amount,Expenses.expense_id).filter(Expenses.expense_criteria_id==criteria_id).order_by(desc(Expenses.date)).all()
    header=Expense_criteria.query.with_entities(Expense_criteria.criteria_name).filter(Expense_criteria.criteria_id==criteria_id).first()
    return render_template('finance_particular_criteria_expenditure.html',header=header[0],data=select_all_of_particular_criteria,criteria_id=criteria_id)

@app.route('/<int:entry_id>/<int:criteria_id>/delete_expense_entry',methods=['GET','POST'])
@login_required
def delete_expense_entry(entry_id,criteria_id):
  if request.method=='GET':
    try:
      Expenses.query.filter(Expenses.expense_id==entry_id).delete()
      db.session.flush()
    except:
      db.session.rollback()
    db.session.commit()
    db.session.close()
    return redirect(f'/{criteria_id}/List_of_particular_expenditure')

@app.route('/delete_account',methods=['GET','POST'])
@login_required
def delete_account():
  if request.method=='GET':
    try:
      User_tracker.query.filter(User_tracker.user_id==current_user.id).delete()
      db.session.flush()
      User_food_log.query.filter(User_food_log.user_id==current_user.id).delete()
      db.session.flush()
      Run_log.query.filter(Run_log.user_id==current_user.id).delete()
      db.session.flush()
      Walk_log.query.filter(Walk_log.user_id==current_user.id).delete()
      db.session.flush()
      Expenses.query.filter(Expenses.user_id==current_user.id).delete()
      db.session.flush()
      User.query.filter(User.id==current_user.id).delete()
      db.session.flush()
    except:
      db.session.rollback()      
    db.session.commit()
    db.session.close()
    return redirect(url_for('home'))
    
@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
  logout_user()
  return redirect(url_for('login'))