from flask import Blueprint

from com.tgu.controller.SysUserController import sys_user
from com.tgu.controller.FlightInfoController import flight_info
from com.tgu.controller.BaggageController import baggage
from com.tgu.controller.TravellerController import traveller
from com.tgu.controller.DifyController import dify

# 创建主蓝图
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api')

# 注册子蓝图
api_v1.register_blueprint(sys_user, url_prefix='/users')
api_v1.register_blueprint(traveller, url_prefix='/travellers')
api_v1.register_blueprint(baggage, url_prefix='/baggage')
api_v1.register_blueprint(flight_info, url_prefix='/flights')
api_v1.register_blueprint(dify, url_prefix='/dify')