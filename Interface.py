from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.exceptions import ApiError
from vk_api.utils import get_random_id
from config import community_token, access_token
import datetime
from core import VKTools
import sqlalchemy
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from main import create_tables, VKchat, add_user, check_user
now = datetime.datetime.now()

vk = vk_api.VkApi(token=community_token)
longpoll = VkLongPoll(vk)

class BotInterface():
    def __init__(self, access_token, community_token):
        self.vk = vk_api.VkApi(token=community_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = VKTools(access_token)
        self.params = {}
        self.worksheets = []
        self.offset = 0
    def message_send(self, user_id, message, attachment=None):
        self.vk.method('messages.send',
                  {'user_id': user_id,
                   'random_id': get_random_id(),
                   'message': message,
                   'attachment': attachment})

    def write_msg(self, user_id, message):
        vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })

    def event_handler(self) -> object:
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:

                if event.text.lower() == 'привет':
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Привет, {self.params["name"]}')

                    if self.params['age']==None:
                        self.message_send(event.user_id, 'Назовите свой возраст')
                        if event.text.isdigit():
                            self.vk_tools.info['id']['age'].get(event.text())
                        else:
                            self.message_send(event.user_id, 'Поиск партнера от 22 до 28 лет')

                elif event.text.lower() == 'поиск':
                    self.params = self.vk_tools.get_profile_info(event.user_id)
                    named_interests = []
                    self.message_send(event.user_id, 'Выберете, что важнее: книги, музыка или интерес')
                    if event.text.lower() == 'книги':
                        named_interests = self.params['books']
                        if self.params['books'] == None:
                            self.message_send(event.user_id, 'Назовите любимую книгу')
                            self.vk_tools.info['id']['books'].get(event.text())
                    elif event.text.lower() == 'музыка':
                        named_interests = self.params['music']
                        if self.params['music'] == None:
                            self.message_send(event.user_id, 'Назовите любимую музыку')
                            self.vk_tools.info['id']['music'].get(event.text())
                    elif event.text.lower() == 'интерес':
                        named_interests = self.params['interests']
                        if self.params['interests'] == None:
                            self.message_send(event.user_id, 'Назовите свой интерес')
                            self.vk_tools.info['id']['interests'].get(event.text())
                            
                    self.message_send(event.user_id, 'Начинаем поиск')
                    self.worksheets = self.vk_tools.search_worksheet(self.params, self.offset)
                    worksheet = self.worksheets.pop()
                    viewed_worksheet = session.add_user(engine, event.user_id, worksheet['id'])
                    session.commit(viewed_worksheet)
                    photos = self.vk_tools.get_photos(worksheet['id'])
                    photo_string = ''
                    for photo in photos:
                        photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                        photo_like = self.vk_tools.likes.add(photo["id"])
                        photo_dislike = self.vk_tools.likes.delete(photo["id"])
                    self.message_send(event.user_id, f'имя: {worksheet["name"]} ссылка: vk.com/{worksheet["id"]}', attachment=photo_string)
                    self.offset += 50
                elif event.text.lower() == "пока":
                    self.message_send(event.user_id, "До новых встреч!")
                else:
                    self.message_send(event.user_id, "Неизвестная команда")

if __name__=='__main__':
    bot_interface = BotInterface(access_token, community_token)
    bot_interface.event_handler()

session.close()
