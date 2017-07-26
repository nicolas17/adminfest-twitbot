from peewee import *
import datetime
import random

db = SqliteDatabase('adminfest.db')

def gen_hex_colour_code():
   return ''.join([random.choice('0123456789ABCDEF') for x in range(6)])

class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    """
    ORM model of the User table
    """
    #username = CharField(unique=True)
    user_id = BigIntegerField(primary_key=True)
    beers = IntegerField(default=0)


class BeerCode(BaseModel):
    """
    ORM model of the BeerCode table
    """
    beer_code = TextField(unique=True)
    user = ForeignKeyField(User, null=True, related_name='beer_codes')
    timestamp = DateTimeField(default="")
    used = BooleanField(default=False)


class Tweet(BaseModel):
    """
    ORM model of the Tweet table
    """
    user = ForeignKeyField(User, related_name='tweets')
    status_id = TextField(unique=True)
    text = TextField()
    created_date = DateTimeField(default=datetime.datetime.now)
    is_published = BooleanField(default=True)
    processed = BooleanField(default=False)
    process_try = IntegerField(default=0)
    beer_code = TextField(default="")


if __name__ == "__main__":
    try:
        User.create_table()
    except OperationalError:
        print("User table already exists!")

    try:
        BeerCode.create_table()
    except OperationalError:
        print("BeerCode table already exists!")

    try:
        Tweet.create_table()
    except OperationalError:
        print("Tweet table already exists!")

    #generate codes
    with db.atomic():
        for n in range(50):
            code = gen_hex_colour_code()
            beer_code = BeerCode.create(beer_code=code)
            beer_code.save()
