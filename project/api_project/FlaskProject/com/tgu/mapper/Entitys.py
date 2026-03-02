from peewee import Model, CharField, TextField, PostgresqlDatabase, AutoField, IntegerField, BooleanField, DateTimeField

import logging

logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

db = PostgresqlDatabase('tjpu22ai10', user='tjpu22ai10', password='tjpu22ai10', host='106.3.99.64', port=20024)


class BaseModel(Model):
    class Meta:
        database = db


class SysUser(BaseModel):
    id = AutoField(primary_key=True)
    uid = CharField(max_length=255)
    pwd = CharField(max_length=255)
    nickName = CharField(max_length=255, column_name='nick_name')
    createTime = DateTimeField(column_name='create_time')
    isDeleted = BooleanField(column_name='is_deleted', default=False)

    class Meta:
        table_name = 'sys_user'


class Traveller(BaseModel):
    id = AutoField(primary_key=True)
    travellerName = CharField(max_length=255, column_name='traveller_name')
    travellerId = CharField(max_length=255, column_name='traveller_id')
    travellerTel = CharField(max_length=255, column_name='traveller_tel')
    uid = CharField(max_length=255)
    flightNo = CharField(max_length=255, column_name='flight_no')
    createTime = DateTimeField(column_name='create_time')
    isDeleted = BooleanField(column_name='is_deleted', default=False)

    class Meta:
        table_name = 'traveller'


class Baggage(BaseModel):
    id = AutoField(primary_key=True)
    type = IntegerField()
    travellerId = CharField(max_length=255, column_name='traveller_id')
    flightNo = CharField(max_length=255, column_name='flight_no')
    status = IntegerField()
    travelBeginTime = DateTimeField(column_name='travel_begin_time')
    createTime = DateTimeField(column_name='create_time')
    isDeleted = BooleanField(column_name='is_deleted', default=False)

    class Meta:
        table_name = 'baggage'


class FlightInfo(BaseModel):
    id = AutoField(primary_key=True)
    flightNo = CharField(max_length=255, column_name='flight_no')
    departure = CharField(max_length=255)
    destination = CharField(max_length=255)
    period = TextField()
    airline = CharField(max_length=255)
    createTime = DateTimeField(column_name='create_time')
    isDeleted = BooleanField(column_name='is_deleted', default=False)

    class Meta:
        table_name = 'flight_info'

