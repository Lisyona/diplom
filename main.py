#import random
#import vk_api
#from vk_api.longpoll import VkLongPoll, VkEventType
#from vk_api.utils import get_random_id
#from config import community_token

#vk = vk_api.VkApi(token=community_token)
#longpoll = VkLongPoll(vk)
import sqlalchemy
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import select
from sqlalchemy import create_engine, MetaData
import ast
from config import DSN

engine = sqlalchemy.create_engine(DSN)
Session = sessionmaker(bind = engine)
session = Session()
Base = declarative_base()
Base.metadata.create_all(engine)

class VKchat(Base):
    __tablename__ = 'viewed'

    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, unique=True)
    liked = sq.Column(sq.Text)
    disliked = sq.Column(sq.Text)

def add_user(engine, profile_id, worksheet_id):
    with Session(engine) as session:
        to_bd = VKchat(profile_id=profile_id, worksheet_id=worksheet_id)
        session.add(to_bd)
        session.commit()

def check_user(engine, profile_id, worksheet_id):
    with Session(engine) as session:
        from_bd = session.query(VKchat).filter(VKchat.profile_id == profile_id, VKchat.worksheet_id == worksheet_id).first()
    return True if from_bd else False



if __name__=='__main__':
    engine = create_engine(db_url_object)
    Base.metadata.create_all(engine)
    add_user(engine, 2113, 124512)
    res = check_user(engine, 2113, 124512)
    print(res)

session.close()
