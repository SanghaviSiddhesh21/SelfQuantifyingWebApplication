from datetime import datetime,date
from numpy import outer
from sqlalchemy import desc

from flask_restful import Resource
from flask_restful import reqparse

from application.database import db
from application.models import *
from application.validation import BusinessValidationError
from application.controllers import add_food_track_entry, bcrypt
from application.functions import date_to_float

delete_user_parser=reqparse.RequestParser()
delete_user_parser.add_argument('password')

create_user_parser=reqparse.RequestParser()
create_user_parser.add_argument('first_name')
create_user_parser.add_argument('last_name')
create_user_parser.add_argument('date_of_birth')
create_user_parser.add_argument('username')
create_user_parser.add_argument('password')
create_user_parser.add_argument('re_enter_password')

class UserAPI(Resource):
  def get(self, username):
    user=db.session.query(User).filter(User.username==username).first()
    if user:
      return {'Existence':'True'}
    else:
      return {'Existence':'False'}
  def delete(self,username):
    args=delete_user_parser.parse_args()
    password=args.get('password',None)
    user=db.session.query(User).filter(User.username==username).first()
    if user:
      if password!=None:
        if (bcrypt.check_password_hash(user.password,password)):
          try:
            User_tracker.query.filter(User_tracker.user_id==user.id).delete()
            db.session.flush()
            User_food_log.query.filter(User_food_log.user_id==user.id).delete()
            db.session.flush()
            Run_log.query.filter(Run_log.user_id==user.id).delete()
            db.session.flush()
            Walk_log.query.filter(Walk_log.user_id==user.id).delete()
            db.session.flush()
            Expenses.query.filter(Expenses.user_id==user.id).delete()
            db.session.flush()
            User.query.filter(User.username==user.username).delete()
            db.session.flush()
          except:
            db.session.rollback()
          db.session.commit()
          db.session.close()
          return 'User deleted successfully',200
        else:
          raise BusinessValidationError(status_code=404,error_code='U1003',error_message='Incorrect password')
      else:
        raise BusinessValidationError(status_code=404,error_code='U1002',error_message='Password necessary for deleting user')
    else:
      raise BusinessValidationError(status_code=404,error_code='U1001',error_message="Username doesn't exists")
  def post(self):
    args=create_user_parser.parse_args()
    fname=args.get('first_name',None)
    lname=args.get('last_name',None)
    dob=args.get('date_of_birth',None)
    username=args.get('username',None)
    password=args.get('password',None)
    re_password=args.get('re_enter_password',None)
    if fname!=None:
      fname=fname.strip()
      if fname:
        dob=dob.split('/')
        dob[0]=dob[0].strip()
        dob[1]=dob[1].strip()
        dob[2]=dob[2].strip()
        if(dob[0].isnumeric() and dob[1].isnumeric() and dob[2].isnumeric() and len(dob)==3 and len(dob[0])==4 and len(dob[1])==2 and (int(dob[1])<=12) and (int(dob[2])<=31)):
          dob_=dob[0]+'-'+dob[1]+'-'+dob[2]   
          dob_obj = datetime.strptime(dob_,'%Y-%m-%d')
          dob_obj=dob_obj.date()
          user=User.query.filter(User.username==username).first()
          if user:
            raise BusinessValidationError(status_code=404,error_code='U1008',error_message="Username already exists")
          else:
            if password==re_password:
              hashedpassword=bcrypt.generate_password_hash(password)
              user=User(fname=fname,lname=lname,birthdate=dob_obj,username=username,password=hashedpassword)
              try:
                db.session.add(user)
                db.session.flush()
              except:
                db.session.rollback()
              db.session.commit()
              db.session.close()
              return 'Registration Successful',200
            else:
              raise BusinessValidationError(status_code=404,error_code='U1007',error_message="Same password should be typed in the re-enter password section")
        else:
          raise BusinessValidationError(status_code=404,error_code='U1006',error_message='Date not in correct format')
      else:
        raise BusinessValidationError(status_code=404,error_code='U1005',error_message='Incorrect First Name')
    else:
      raise BusinessValidationError(status_code=404,error_code='U1004',error_message='First Name missing')

add_food_log_parser=reqparse.RequestParser()
add_food_log_parser.add_argument('username')
add_food_log_parser.add_argument('password')
add_food_log_parser.add_argument('food_name')
add_food_log_parser.add_argument('quantity')

class Add_Foodlog_API(Resource):
  def post(self):
    args=add_food_log_parser.parse_args()
    username=args.get('username',None)
    password=args.get('password',None)
    food_name=args.get('food_name',None)
    quantity=args.get('quantity',None)
    if username!=None:
      if password!=None:
        user=User.query.filter(User.username==username).first()
        if user:
          if (bcrypt.check_password_hash(user.password,password)):
            quantity=float(quantity)
            if type(quantity)==type(21.1):
              food=Food_nutrients.query.filter(Food_nutrients.food_name==food_name).first()
              if food:
                add_log=User_food_log(user_id=user.id,food_id=food.food_id,quantity_taken=quantity,calorie_input=(quantity*food.Kcal_per_gram),date=date.today())
                try:
                  db.session.add(add_log)
                  db.session.flush()
                except:
                  db.session.rollback()
                db.session.commit()
                db.session.close()
                return 'Food entry added',200
              else:
                raise BusinessValidationError(status_code=404,error_code='F1013',error_message="Food_name doesn't exists")
            else:
              raise BusinessValidationError(status_code=404,error_code='F1012',error_message="Quantity Should be in form of float")
          else:
            raise BusinessValidationError(status_code=404,error_code='F1004',error_message='Incorrect password')
        else:
          raise BusinessValidationError(status_code=404,error_code='F1003',error_message='Username not present')
      else:
        raise BusinessValidationError(status_code=404,error_code='F1002',error_message='Password Required')
    else:
      raise BusinessValidationError(status_code=404,error_code='F1001',error_message='Username required')



get_food_log_parser=reqparse.RequestParser()
get_food_log_parser.add_argument('username')
get_food_log_parser.add_argument('password')

update_food_log_parser=reqparse.RequestParser()
update_food_log_parser.add_argument('username')
update_food_log_parser.add_argument('password')
update_food_log_parser.add_argument('food_name_old')
update_food_log_parser.add_argument('food_name_new')
update_food_log_parser.add_argument('quantity_old')
update_food_log_parser.add_argument('quantity_new')
update_food_log_parser.add_argument('date_old')
update_food_log_parser.add_argument('date_new')

delete_food_log_parser=reqparse.RequestParser()
delete_food_log_parser.add_argument('username')
delete_food_log_parser.add_argument('password')
delete_food_log_parser.add_argument('food_name')
delete_food_log_parser.add_argument('quantity')
delete_food_log_parser.add_argument('date')
class Food_log_API(Resource):
  def post(self):
    args=get_food_log_parser.parse_args()
    username=args.get('username',None)
    password=args.get('password',None)
    if username!=None:
      if password!=None:
        user=User.query.filter(User.username==username).first()
        if user:
          if (bcrypt.check_password_hash(user.password,password)):
            food_logs=User_food_log.query.with_entities(Food_nutrients.food_name,User_food_log.quantity_taken,User_food_log.calorie_input,User_food_log.date).join(Food_nutrients,Food_nutrients.food_id==User_food_log.food_id).filter(User_food_log.user_id==user.id).order_by(desc(User_food_log.date)).all()
            output=''
            for i in food_logs:
              output=output+"{ "+f'Food name :{i["food_name"]} , ' + f'Quantity Consumed:{i["quantity_taken"]} , ' + f'Calorie Input:{i["calorie_input"]} ' + f'Date : {i["date"]} ' + '} ,'
            output='{ '+ output[:len(output)-1]+' }'
            return output
          else:
            raise BusinessValidationError(status_code=404,error_code='F1004',error_message='Incorrect password')
        else:
          raise BusinessValidationError(status_code=404,error_code='F1003',error_message='Username not present')
      else:
        raise BusinessValidationError(status_code=404,error_code='F1002',error_message='Password Required')
    else:
      raise BusinessValidationError(status_code=404,error_code='F1001',error_message='Username required')
  def put(self):
    args=update_food_log_parser.parse_args()
    username=args.get('username',None)
    password=args.get('password',None)
    food_name_old=args.get('food_name_old',None)
    food_name_new=args.get('food_name_new',None)
    quantity_old=args.get('quantity_old',None)
    quantity_new=args.get('quantity_new',None)
    date_old=args.get('date_old',None)
    date_new=args.get('date_new',None)
    if username!=None:
      if password!=None:
        user=User.query.filter(User.username==username).first()
        if user:
          if (bcrypt.check_password_hash(user.password,password)):
            fo_name_old=Food_nutrients.query.filter(Food_nutrients.food_name==food_name_old).first()
            if fo_name_old:
              fo_name_new=Food_nutrients.query.filter(Food_nutrients.food_name==food_name_new).first()
              if fo_name_new:
                quantity_old=(float(quantity_old))
                if type(quantity_old)==type(21.1):
                  quantity_new=float(quantity_new)
                  if type(quantity_new)==type(21.1):
                    date_old_alpha=[]
                    date_new_alpha=[]
                    if(len(date_old)==10):
                      if(len(date_new)==10):
                        for i in date_old:
                          if(i.isnumeric()):
                            pass
                          else:
                            date_old_alpha.append(i)
                        date_old_alpha=set(date_old_alpha)
                        date_old_alpha=list(date_old_alpha)
                        if (len(date_old_alpha)==1):
                          for i in date_new:
                            if(i.isnumeric()):
                              pass
                            else:
                              date_new_alpha.append(i)
                          date_new_alpha=set(date_new_alpha)
                          date_new_alpha=list(date_new_alpha)
                          if (len(date_new_alpha)==1):
                            dob_o=date_old.split(f'{date_old_alpha[0]}')
                            if(dob_o[0].isnumeric() and dob_o[1].isnumeric() and dob_o[2].isnumeric() and len(dob_o)==3 and len(dob_o[0])==4 and len(dob_o[1])==2 and (int(dob_o[1])<=12) and (int(dob_o[2])<=31)):
                              dob_o_=dob_o[0]+'-'+dob_o[1]+'-'+dob_o[2]   
                              dob_o_obj = datetime.strptime(dob_o_,'%Y-%m-%d')
                              dob_o_obj=dob_o_obj.date()
                              dob_n=date_new.split(f'{date_new_alpha[0]}')
                              if(dob_n[0].isnumeric() and dob_n[1].isnumeric() and dob_n[2].isnumeric() and len(dob_n)==3 and len(dob_n[0])==4 and len(dob_n[1])==2 and (int(dob_n[1])<=12) and (int(dob_n[2])<=31)):
                                dob_n_=dob_n[0]+'-'+dob_n[1]+'-'+dob_n[2]   
                                dob_n_obj = datetime.strptime(dob_n_,'%Y-%m-%d')
                                dob_n_obj=dob_n_obj.date()
                                ifexists=User_food_log.query.filter(User_food_log.user_id==user.id,User_food_log.date==dob_o_obj,User_food_log.quantity_taken==quantity_old,User_food_log.food_id==fo_name_old.food_id).first()
                                if ifexists:
                                  try:
                                    ifexists.quantity_taken=quantity_new
                                    db.session.flush()
                                    ifexists.date=dob_n_obj
                                    db.session.flush()
                                    ifexists.food_id=fo_name_new.food_id
                                    db.session.flush()
                                    ifexists.calorie_input=(quantity_new*fo_name_new.Kcal_per_gram)
                                    db.session.flush()
                                  except:
                                    db.session.rolback()
                                  db.session.commit()
                                  db.session.close
                                  return "Successfully updated",200
                                else:
                                  raise BusinessValidationError(status_code=404,error_code='F1011',error_message="log for the given values doesn't exists, hence cannot be updated")
                              else:
                                raise BusinessValidationError(status_code=404,error_code='None',error_message="Enter the new date in proper format")
                            else:
                              raise BusinessValidationError(status_code=404,error_code='None',error_message="Enter the old date in proper format")
                          else:
                            raise BusinessValidationError(status_code=404,error_code='None',error_message="Enter the new date in proper format")
                        else:
                          raise BusinessValidationError(status_code=404,error_code='None',error_message="Enter the old date in proper format")
                      else:
                        raise BusinessValidationError(status_code=404,error_code='None',error_message="Enter the new date in proper format")
                    else:
                      raise BusinessValidationError(status_code=404,error_code='None',error_message="Enter the old date in proper format")
                  else:
                    raise BusinessValidationError(status_code=404,error_code='None',error_message="New Quantity should be in form of float")
                else:
                  raise BusinessValidationError(status_code=404,error_code='None',error_message="Old Quantity Should be in form of float")
              else:
                raise BusinessValidationError(status_code=404,error_code='None',error_message="food_name_new_doesn't exists")
            else:
              raise BusinessValidationError(status_code=404,error_code='None',error_message="food_name_old_doesn't exists")
          else:
            raise BusinessValidationError(status_code=404,error_code='F1004',error_message='Incorrect password')
        else:
          raise BusinessValidationError(status_code=404,error_code='F1003',error_message='Username not present')
      else:
        raise BusinessValidationError(status_code=404,error_code='F1002',error_message='Password Required')
    else:
      raise BusinessValidationError(status_code=404,error_code='F1001',error_message='Username required')
  def delete(self):
    args=delete_food_log_parser.parse_args()
    username=args.get('username',None)
    password=args.get('password',None)
    food_name=args.get('food_name',None)
    quantity=args.get('quantity',None)
    date=args.get('date',None)
    if username!=None:
      if password!=None:
        user=User.query.filter(User.username==username).first()
        if user:
          if (bcrypt.check_password_hash(user.password,password)):
            fo_name=Food_nutrients.query.filter(Food_nutrients.food_name==food_name).first()
            if fo_name:
                quantity=(float(quantity))
                if type(quantity)==type(21.1):                 
                  if(len(date)==10):
                    date_alpha=[]
                    for i in date:
                      if(i.isnumeric()):
                        pass
                      else:
                        date_alpha.append(i)
                    date_alpha=set(date_alpha)
                    date_alpha=list(date_alpha)
                    if (len(date_alpha)==1):
                      dob=date.split(f'{date_alpha[0]}')
                      if(dob[0].isnumeric() and dob[1].isnumeric() and dob[2].isnumeric() and len(dob)==3 and len(dob[0])==4 and len(dob[1])==2 and (int(dob[1])<=12) and (int(dob[2])<=31)):
                        dob_=dob[0]+'-'+dob[1]+'-'+dob[2]   
                        dob_obj = datetime.strptime(dob_,'%Y-%m-%d')
                        dob_obj=dob_obj.date()
                        ifexists=User_food_log.query.filter(User_food_log.user_id==user.id,User_food_log.date==dob_obj,User_food_log.quantity_taken==quantity,User_food_log.food_id==fo_name.food_id).first()
                        if ifexists:
                          try:
                            User_food_log.query.filter(User_food_log.user_food_log_id==ifexists.user_food_log_id).delete()
                            db.session.flush()
                          except:
                            db.session.rollback()
                          db.session.commit()
                          db.session.close
                          return "Successfully Deleted",200
                        else:
                          raise BusinessValidationError(status_code=404,error_code='F1011',error_message="log for the given values doesn't exists, hence cannot be updated")
                    else:
                      raise BusinessValidationError(status_code=404,error_code='F1014',error_message="Enter the date in proper format") 
                  else:
                    raise BusinessValidationError(status_code=404,error_code='F1014',error_message="Enter the date in proper format")
                else:
                  raise BusinessValidationError(status_code=404,error_code='F1012',error_message="Quantity Should be in form of float")
            else:
              raise BusinessValidationError(status_code=404,error_code='F1013',error_message="food_name doesn't exists")
          else:
            raise BusinessValidationError(status_code=404,error_code='F1004',error_message='Incorrect password')
        else:
          raise BusinessValidationError(status_code=404,error_code='F1003',error_message='Username not present')
      else:
        raise BusinessValidationError(status_code=404,error_code='F1002',error_message='Password Required')
    else:
      raise BusinessValidationError(status_code=404,error_code='F1001',error_message='Username required')    

get_run_log_parser=reqparse.RequestParser()
get_run_log_parser.add_argument('username')
get_run_log_parser.add_argument('password')

delete_run_log_parser=reqparse.RequestParser()
delete_run_log_parser.add_argument('username')
delete_run_log_parser.add_argument('password')
delete_run_log_parser.add_argument('cal_burned')
delete_run_log_parser.add_argument('date')

class Add_Runlog_API(Resource):
  def post(self):
    args=get_run_log_parser.parse_args()
    username=args.get('username',None)
    password=args.get('password',None)
    if username!=None:
      if password!=None:
        user=User.query.filter(User.username==username).first()
        if user:
          if (bcrypt.check_password_hash(user.password,password)):
            run_log=Run_log(user_id=user.id,date=date.today(),start_time=datetime.now(),end_time=datetime.now(),duration= 0.1,calorie_burnt=0.1)
            try:
              db.session.add(run_log)
              db.session.flush()
            except:
              db.session.rollback()
            db.session.commit()
            db.session.close()
            return 'Run Started',200
          else:
            raise BusinessValidationError(status_code=404,error_code='R1004',error_message='Incorrect password')
        else:
          raise BusinessValidationError(status_code=404,error_code='R1003',error_message='Username not present')
      else:
        raise BusinessValidationError(status_code=404,error_code='R1002',error_message='Password Required')
    else:
      raise BusinessValidationError(status_code=404,error_code='R1001',error_message='Username required')
  def put(self):
    args=get_run_log_parser.parse_args()
    username=args.get('username',None)
    password=args.get('password',None)
    if username!=None:
      if password!=None:
        user=User.query.filter(User.username==username).first()
        if user:
          if (bcrypt.check_password_hash(user.password,password)):
            run_log=Run_log.query.filter(Run_log.user_id==user.id).order_by(desc(Run_log.date)).first()
            if(run_log.start_time==run_log.end_time):
              cal_per_min=Excercise_calorie.query.with_entities(Excercise_calorie.avg_calorie_burnt_per_min).filter(Excercise_calorie.exercise_id==1).first()
              end_time=datetime.now()
              duration=end_time-run_log.start_time
              duration=date_to_float(str(duration))
              duration=round(duration,2)
              try:
                run_log.end_time=end_time
                db.session.flush()
                run_log.duration=duration
                db.session.flush()
                run_log.calorie_burnt=(duration*cal_per_min[0])
                db.session.flush()
              except:
                db.session.rollback()
              db.session.commit()
              db.session.close()
              return 'Run Ended',200
            else:
              raise BusinessValidationError(status_code=404,error_code='R1005',error_message='Start Run first')
          else:
            raise BusinessValidationError(status_code=404,error_code='R1004',error_message='Incorrect password')
        else:
          raise BusinessValidationError(status_code=404,error_code='R1003',error_message='Username not present')
      else:
        raise BusinessValidationError(status_code=404,error_code='R1002',error_message='Password Required')
    else:
      raise BusinessValidationError(status_code=404,error_code='R1001',error_message='Username required')
class Run_log_API(Resource):
  def post(self):
    args=get_run_log_parser.parse_args()
    username=args.get('username',None)
    password=args.get('password',None)
    if username!=None:
      if password!=None:
        user=User.query.filter(User.username==username).first()
        if user:
          if (bcrypt.check_password_hash(user.password,password)):
            run_logs=Run_log.query.with_entities(Run_log.duration,Run_log.calorie_burnt,Run_log.date,Run_log.start_time).filter(Run_log.user_id==user.id).order_by(desc(Run_log.date)).all()
            output=''
            for i in run_logs:
              output=output+'{ '+f'Run Started at : {i["start_time"]} ,'+f' Run duration : {i["duration"]} ,'+f' Calories Burnt : {i["calorie_burnt"]} ,'+'} , '
            output='{ '+output[:len(output)-2]+' }'
            return output
          else:
            raise BusinessValidationError(status_code=404,error_code='R1004',error_message='Incorrect password')
        else:
          raise BusinessValidationError(status_code=404,error_code='R1003',error_message='Username not present')
      else:
        raise BusinessValidationError(status_code=404,error_code='R1002',error_message='Password Required')
    else:
      raise BusinessValidationError(status_code=404,error_code='R1001',error_message='Username required')
  def delete(self):
    args=delete_run_log_parser.parse_args()
    username=args.get('username',None)
    password=args.get('password',None)
    cal_burned=args.get('cal_burned',None)
    date=args.get('date',None)
    if username!=None:
      if password!=None:
        user=User.query.filter(User.username==username).first()
        if user:
          if (bcrypt.check_password_hash(user.password,password)):
            if(len(date)==10):
              date_alpha=[]
              for i in date:
                if(i.isnumeric()):
                  pass
                else:
                  date_alpha.append(i)
              date_alpha=set(date_alpha)
              date_alpha=list(date_alpha)
              if (len(date_alpha)==1):
                dob=date.split(f'{date_alpha[0]}')
                if(dob[0].isnumeric() and dob[1].isnumeric() and dob[2].isnumeric() and len(dob)==3 and len(dob[0])==4 and len(dob[1])==2 and (int(dob[1])<=12) and (int(dob[2])<=31)):
                  dob_=dob[0]+'-'+dob[1]+'-'+dob[2]   
                  dob_obj = datetime.strptime(dob_,'%Y-%m-%d')
                  dob_obj=dob_obj.date()
                  try:
                    Run_log.query.filter(Run_log.user_id==user.id,Run_log.calorie_burnt==cal_burned,Run_log.date==dob_obj).delete()
                    db.session.flush()
                  except:
                    db.session.rollback()
                  db.session.commit()
                  db.session.close()
                  return 'Run log successfully deleted',200
                else:
                  raise BusinessValidationError(status_code=404,error_code='R1006',error_message='Invalid date format')
              else:
                raise BusinessValidationError(status_code=404,error_code='R1006',error_message='Invalid date format') 
            else:
              raise BusinessValidationError(status_code=404,error_code='R1006',error_message='Invalid date format')
          else:
            raise BusinessValidationError(status_code=404,error_code='R1004',error_message='Incorrect password')
        else:
          raise BusinessValidationError(status_code=404,error_code='R1003',error_message='Username not present')
      else:
        raise BusinessValidationError(status_code=404,error_code='R1002',error_message='Password Required')
    else:
      raise BusinessValidationError(status_code=404,error_code='R1001',error_message='Username required')

get_walk_log_parser=reqparse.RequestParser()
get_walk_log_parser.add_argument('username')
get_walk_log_parser.add_argument('password')

delete_walk_log_parser=reqparse.RequestParser()
delete_walk_log_parser.add_argument('username')
delete_walk_log_parser.add_argument('password')
delete_walk_log_parser.add_argument('cal_burned')
delete_walk_log_parser.add_argument('date')

class Add_Walklog_API(Resource):
  def post(self):
    args=get_walk_log_parser.parse_args()
    username=args.get('username',None)
    password=args.get('password',None)
    if username!=None:
      if password!=None:
        user=User.query.filter(User.username==username).first()
        if user:
          if (bcrypt.check_password_hash(user.password,password)):
            walk_log=Walk_log(user_id=user.id,date=date.today(),start_time=datetime.now(),end_time=datetime.now(),duration= 0.1,calorie_burnt=0.1)
            try:
              db.session.add(walk_log)
              db.session.flush()
            except:
              db.session.rollback()
            db.session.commit()
            db.session.close()
            return 'Walk Started',200
          else:
            raise BusinessValidationError(status_code=404,error_code='W1004',error_message='Incorrect password')
        else:
          raise BusinessValidationError(status_code=404,error_code='W1003',error_message='Username not present')
      else:
        raise BusinessValidationError(status_code=404,error_code='W1002',error_message='Password Required')
    else:
      raise BusinessValidationError(status_code=404,error_code='W1001',error_message='Username required')
  def put(self):
    args=get_walk_log_parser.parse_args()
    username=args.get('username',None)
    password=args.get('password',None)
    if username!=None:
      if password!=None:
        user=User.query.filter(User.username==username).first()
        if user:
          if (bcrypt.check_password_hash(user.password,password)):
            walk_log=Walk_log.query.filter(Walk_log.user_id==user.id).order_by(desc(Walk_log.date)).first()
            if(walk_log.start_time==walk_log.end_time):
              cal_per_min=Excercise_calorie.query.with_entities(Excercise_calorie.avg_calorie_burnt_per_min).filter(Excercise_calorie.exercise_id==2).first()
              end_time=datetime.now()
              duration=end_time-walk_log.start_time
              duration=date_to_float(str(duration))
              duration=round(duration,2)
              try:
                walk_log.end_time=end_time
                db.session.flush()
                walk_log.duration=duration
                db.session.flush()
                walk_log.calorie_burnt=(duration*cal_per_min[0])
                db.session.flush()
              except:
                db.session.rollback()
              db.session.commit()
              db.session.close()
              return 'Walk Ended',200
            else:
              raise BusinessValidationError(status_code=404,error_code='W1006',error_message='Start Walk first')
          else:
            raise BusinessValidationError(status_code=404,error_code='W1004',error_message='Incorrect password')
        else:
          raise BusinessValidationError(status_code=404,error_code='W1003',error_message='Username not present')
      else:
        raise BusinessValidationError(status_code=404,error_code='W1002',error_message='Password Required')
    else:
      raise BusinessValidationError(status_code=404,error_code='W1001',error_message='Username required')
class Walk_log_API(Resource):
  def post(self):
    args=get_walk_log_parser.parse_args()
    username=args.get('username',None)
    password=args.get('password',None)
    if username!=None:
      if password!=None:
        user=User.query.filter(User.username==username).first()
        if user:
          if (bcrypt.check_password_hash(user.password,password)):
            walk_logs=Walk_log.query.with_entities(Walk_log.duration,Walk_log.calorie_burnt,Walk_log.date,Walk_log.start_time).filter(Walk_log.user_id==user.id).order_by(desc(Walk_log.date)).all()
            output=''
            for i in walk_logs:
              output=output+'{ '+f'Walk Started at : {i["start_time"]} ,'+f' Walk duration : {i["duration"]} ,'+f' Calories Burnt : {i["calorie_burnt"]} ,'+'} , '
            output='{ '+output[:len(output)-2]+' }'
            return output
          else:
            raise BusinessValidationError(status_code=404,error_code='W1004',error_message='Incorrect password')
        else:
          raise BusinessValidationError(status_code=404,error_code='W1003',error_message='Username not present')
      else:
        raise BusinessValidationError(status_code=404,error_code='W1002',error_message='Password Required')
    else:
      raise BusinessValidationError(status_code=404,error_code='W1001',error_message='Username required')
  def delete(self):
    args=delete_walk_log_parser.parse_args()
    username=args.get('username',None)
    password=args.get('password',None)
    cal_burned=args.get('cal_burned',None)
    date=args.get('date',None)
    if username!=None:
      if password!=None:
        user=User.query.filter(User.username==username).first()
        if user:
          if (bcrypt.check_password_hash(user.password,password)):
            if(len(date)==10):
              date_alpha=[]
              for i in date:
                if(i.isnumeric()):
                  pass
                else:
                  date_alpha.append(i)
              date_alpha=set(date_alpha)
              date_alpha=list(date_alpha)
              if (len(date_alpha)==1):
                dob=date.split(f'{date_alpha[0]}')
                if(dob[0].isnumeric() and dob[1].isnumeric() and dob[2].isnumeric() and len(dob)==3 and len(dob[0])==4 and len(dob[1])==2 and (int(dob[1])<=12) and (int(dob[2])<=31)):
                  dob_=dob[0]+'-'+dob[1]+'-'+dob[2]   
                  dob_obj = datetime.strptime(dob_,'%Y-%m-%d')
                  dob_obj=dob_obj.date()
                  try:
                    Walk_log.query.filter(Walk_log.user_id==user.id,Walk_log.calorie_burnt==cal_burned,Walk_log.date==dob_obj).delete()
                    db.session.flush()
                  except:
                    db.session.rollback()
                  db.session.commit()
                  db.session.close()
                  return 'Walk log successfully deleted',200
                else:
                  raise BusinessValidationError(status_code=404,error_code='W1006',error_message='Invalid date format')
              else:
                raise BusinessValidationError(status_code=404,error_code='W1006',error_message='Invalid date format') 
            else:
              raise BusinessValidationError(status_code=404,error_code='W1006',error_message='Invalid date format')
          else:
            raise BusinessValidationError(status_code=404,error_code='W1004',error_message='Incorrect password')
        else:
          raise BusinessValidationError(status_code=404,error_code='W1003',error_message='Username not present')
      else:
        raise BusinessValidationError(status_code=404,error_code='W1002',error_message='Password Required')
    else:
      raise BusinessValidationError(status_code=404,error_code='W1001',error_message='Username required')

get_expense_log_parser=reqparse.RequestParser()
get_expense_log_parser.add_argument('username')
get_expense_log_parser.add_argument('password')

delete_expense_log_parser=reqparse.RequestParser()
delete_expense_log_parser.add_argument('username')
delete_expense_log_parser.add_argument('password')
delete_expense_log_parser.add_argument('amount')
delete_expense_log_parser.add_argument('expense_criteria')
delete_expense_log_parser.add_argument('date')

add_expense_log_parser=reqparse.RequestParser()
add_expense_log_parser.add_argument('username')
add_expense_log_parser.add_argument('password')
add_expense_log_parser.add_argument('amount')
add_expense_log_parser.add_argument('expense_criteria')

class Expense_Log_API(Resource):
  def post(self):
    args=get_expense_log_parser.parse_args()
    username=args.get('username',None)
    password=args.get('password',None)
    if username!=None:
      if password!=None:
        user=User.query.filter(User.username==username).first()
        if user:
          if (bcrypt.check_password_hash(user.password,password)):    
            expenses=Expenses.query.with_entities(Expense_criteria.criteria_name,Expenses.amount,Expenses.date).join(Expense_criteria,Expense_criteria.criteria_id==Expenses.expense_criteria_id).filter(Expenses.user_id==user.id).order_by(desc(Expenses.date)).all()
            if expenses:
              output=''
              for i in expenses:
                output='{ ' + f'Expense_Criteria : {i["criteria_name"]} ' + ',' + f' Expense_amount : {i["amount"]} ' + f' Date_of_expense : {i["date"]} ' + '} ,'
              output='{ ' + output[:(len(output)-1)] + ' }'
              return output,200
            else:
              return 'No Expense Logged until now',200
          else:
            raise BusinessValidationError(status_code=404,error_code='E1004',error_message='Incorrect password')
        else:
          raise BusinessValidationError(status_code=404,error_code='E1003',error_message='Username not present')
      else:
        raise BusinessValidationError(status_code=404,error_code='E1002',error_message='Password Required')
    else:
      raise BusinessValidationError(status_code=404,error_code='E1001',error_message='Username required')
  def delete(self):
    args=delete_expense_log_parser.parse_args()
    username=args.get('username')
    password=args.get('password')
    amount=args.get('amount')
    criteria_name=args.get('expense_criteria')
    date=args.get('date')
    if username!=None:
      if password!=None:
        user=User.query.filter(User.username==username).first()
        if user:
          if (bcrypt.check_password_hash(user.password,password)):   
            ifcriteria=Expense_criteria.query.filter(Expense_criteria.criteria_name==criteria_name).first()
            if ifcriteria:
              if(len(date)==10):
                date_alpha=[]
                for i in date:
                  if(i.isnumeric()):
                    pass
                  else:
                    date_alpha.append(i)
                date_alpha=set(date_alpha)
                date_alpha=list(date_alpha)
                if (len(date_alpha)==1):
                  dob=date.split(f'{date_alpha[0]}')
                  if(dob[0].isnumeric() and dob[1].isnumeric() and dob[2].isnumeric() and len(dob)==3 and len(dob[0])==4 and len(dob[1])==2 and (int(dob[1])<=12) and (int(dob[2])<=31)):
                    dob_=dob[0]+'-'+dob[1]+'-'+dob[2]   
                    dob_obj = datetime.strptime(dob_,'%Y-%m-%d')
                    dob_obj=dob_obj.date()
                    amount_list=[]
                    for i in amount:
                      if i.isnumeric():
                        pass
                      else:
                        amount_list.append(i)
                    amount_list=list(set(amount_list))
                    if (len(amount_list)<=1):
                      amount=float(amount)
                      ifexpenseexists=Expenses.query.filter(Expenses.user_id==user.id,Expenses.expense_criteria_id==ifcriteria.criteria_id,Expenses.date==dob_obj,Expenses.amount==amount).first()
                      if ifexpenseexists:
                        try:
                          db.session.delete(ifexpenseexists)
                          db.session.flush()
                        except:
                          db.session.rollback()
                        db.session.commit()
                        db.session.close()
                        return 'Entry deleted successfully',200
                      else:
                        raise BusinessValidationError(status_code=404,error_code='E1008', error_message="The specified entry doesn't exists hence cannot be deleted")
                    else:
                      raise BusinessValidationError(status_code=404,error_code='E1007',error_message='expense amount in correct format')
                  else:
                    raise BusinessValidationError(status_code=404,error_code='E1006',error_message='Invalid date format')
                else:
                  raise BusinessValidationError(status_code=404,error_code='E1006',error_message='Invalid date format') 
              else:
                raise BusinessValidationError(status_code=404,error_code='E1006',error_message='Invalid date format')
            else:
              raise BusinessValidationError(status_code=404,error_code='E1005',error_message='Expense Criteria not available in list of criteria')
          else:
            raise BusinessValidationError(status_code=404,error_code='E1004',error_message='Incorrect password')
        else:
          raise BusinessValidationError(status_code=404,error_code='E1003',error_message='Username not present')
      else:
        raise BusinessValidationError(status_code=404,error_code='E1002',error_message='Password Required')
    else:
      raise BusinessValidationError(status_code=404,error_code='E1001',error_message='Username required') 

class Add_Expense_Log_API(Resource):
  def post(self):
    args=add_expense_log_parser.parse_args()
    username=args.get('username')
    password=args.get('password')
    amount=args.get('amount')
    criteria_name=args.get('expense_criteria')
    if username!=None:
      if password!=None:
        user=User.query.filter(User.username==username).first()
        if user:
          if (bcrypt.check_password_hash(user.password,password)):   
            ifcriteria=Expense_criteria.query.filter(Expense_criteria.criteria_name==criteria_name).first()
            if ifcriteria:
              amount_list=[]
              for i in amount:
                if i.isnumeric():
                  pass
                else:
                  amount_list.append(i)
              amount_list=list(set(amount_list))
              if (len(amount_list)<=1):
                amount=float(amount)
                add_expense_log=Expenses(user_id=user.id,expense_criteria_id=ifcriteria.criteria_id,amount=amount,date=date.today())
                try:
                  db.session.add(add_expense_log)
                  db.session.flush()
                except:
                  db.session.rollback()
                db.session.commit()
                db.session.close()
                return 'Expense Logged successfully',200
              else:
                raise BusinessValidationError(status_code=404,error_code='E1007',error_message='expense amount in correct format')
            else:
              raise BusinessValidationError(status_code=404,error_code='E1005',error_message='Expense Criteria not available in list of criteria')
          else:
            raise BusinessValidationError(status_code=404,error_code='E1004',error_message='Incorrect password')
        else:
          raise BusinessValidationError(status_code=404,error_code='E1003',error_message='Username not present')
      else:
        raise BusinessValidationError(status_code=404,error_code='E1002',error_message='Password Required')
    else:
      raise BusinessValidationError(status_code=404,error_code='E1001',error_message='Username required')

class Get_Tracker_List_API(Resource):
  def get(self):
    all_trackers=Tracker.query.with_entities(Tracker.tracker_name).all()
    if all_trackers:
      output=''
      for i in all_trackers:
        output=output + f' {i[0]} ,'
      output='{ ' + output[:(len(output)-1)] + ' }'
      return output,200
    else:
      raise BusinessValidationError(status_code=404,error_code='G1001',error_message='No tracker exists') 
class Get_All_Food_Nutrients_List_API(Resource):
  def get(self):
    all_foods=Food_nutrients.query.with_entities(Food_nutrients.food_name).all()
    if all_foods:
      output=''
      for i in all_foods:
        output=output + f' {i[0]} ,'
      output='{ ' + output[:(len(output)-1)] + ' }'
      return output,200 
    else:
      raise BusinessValidationError(status_code=404,error_code='G1001',error_message='No tracker exists')