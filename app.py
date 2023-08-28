import os
from flask import Flask
from flask_restful import Resource,Api
from application.config import LocalDevelopmentConfig
from application.database import db

app=None
api=None
def create_app():
  app=Flask(__name__,template_folder='templates')
  if os.getenv('ENV','development')=='production':
    raise Exception("Currently bo production config is set-up")
  else:
    print("Starting Local Development")
    app.config.from_object(LocalDevelopmentConfig)
  db.init_app(app)
  api=Api(app)
  app.app_context().push()
  return app,api


app,api=create_app()

from application.controllers import *

from application.api import UserAPI,Food_log_API,Run_log_API,Walk_log_API,Add_Foodlog_API,Add_Runlog_API,Add_Walklog_API,Expense_Log_API,Add_Expense_Log_API,Get_Tracker_List_API,Get_All_Food_Nutrients_List_API
api.add_resource(UserAPI,'/api/userchecks/<string:username>','/api/userchecks')
api.add_resource(Food_log_API,'/api/user/food_tracker_logs')
api.add_resource(Run_log_API,'/api/user/run_tracker_logs')
api.add_resource(Walk_log_API,'/api/user/walk_tracker_logs')
api.add_resource(Add_Foodlog_API,'/api/user/add_food_log')
api.add_resource(Add_Runlog_API,'/api/user/add_run')
api.add_resource(Add_Walklog_API,'/api/user/add_walk')
api.add_resource(Expense_Log_API,'/api/user/expense_log')
api.add_resource(Add_Expense_Log_API,'/api/user/add_expense_log')
api.add_resource(Get_Tracker_List_API,'/api/get_all_trackers')
api.add_resource(Get_All_Food_Nutrients_List_API,'/api/get_all_food_nutrients')

if __name__=="__main__":
  app.run(host='0.0.0.0',port=8080)