from email import message
from flask import make_response
from werkzeug.exceptions import HTTPException
from flask import make_response
import json

class BusinessValidationError(HTTPException):
  def __init__(self, status_code,error_code,error_message):
    message={'error code':error_code,'error_message':error_message}
    self.response=make_response(json.dumps(message),status_code)#json.dumps() converts an object into a json string