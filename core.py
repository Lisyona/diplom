from random import randrange
import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.exceptions import ApiError
from vk_api.utils import get_random_id
from config import community_token, access_token
import datetime
from datetime import datetime
from pprint import pprint

today = datetime.now()

vk = vk_api.VkApi(token=community_token)
longpoll = VkLongPoll(vk)
class VKTools:
    def __init__(self, access_token):
        self.vkapi = vk_api.VkApi(token=access_token)

    def _bdate_toyear(self, bdate: str):
        if bdate is not None:
            user_byear = int(bdate.split('.')[2])
            if user_byear > 0:
                today = datetime.now().year
                age = today - user_byear
            else:
                age = 25
        else:
            age =  25
        return age

    def get_profile_info(self, user_id):
        #info = {}
        try:
            info, = self.vkapi.method('users.get',
                                 {'users_id': user_id,
                                  'fields': 'city,sex,bdate,relation,books,interests,music,groups'})
        except ApiError as e:
            info = {}
            print(f'error = {e}')

        result = {'name': (info['first_name'] + ' ' + info['last_name']) if 'first_name' in info and 'last_name' in info else None,
                   'sex': info.get('sex'),
                   'city': info.get('city')['id'] if int(info.get('city')['id']) > 0 else 0,
                   'age': self._bdate_toyear(info.get('bdate')),
                   'relation': info.get('relation'),
                   'books': info.get('books'),
                   'interests': info.get('interests') if info.get('interests') is not None else None,
                   'music': info.get('music') if info.get('music') is not None else None,
                   'groups': info.get('groups') if info.get('groups') is not None else None,
                   }
        return result
    def search_worksheet(self, params, offset):
        try:
            #for i in range(len(named_interests)):
            users = self.vkapi.method('users.search',
                                        {'count': 50,
                                        'offset': offset,
                                        'has_photo': 1,
                                        'status': 1 or 6,
                                        'age_from': params['age'] - 3,
                                        'age_to': params['age'] + 3,
                                        'city_id': params['city'],
                                        'sex': 1 if params['sex'] == 2 else 2,
                                        'can_access_closed': False
                                         })

        except ApiError as e:
            users = []
            print(f'error = {e}')

        users_result = [{'name': item['first_name'] + ' ' + item['last_name'],
                        'id': item['id']
                         } for item in users['items'] if item['is_closed'] is False
                        ]

        return users_result

    def get_photos(self, id):
        global photos
        try:
            photos = self.vkapi.method('photos.get',
                                        {'owner_id': id,
                                        'album_id': 'profile',
                                        'extended': 1
                                        })


            result = [{'owner_id': item['owner_id'],
                       'id': item['id'],
                       'likes': item['likes']['count'],
                       'comments': item['comments']['count']} for item in photos['items']]
            popular_result = [sorted(result['id'], key=result['likes'], reverse=False)][:3]

        except ApiError as e:
            photos = {}
            print(f'error = {e}')

        return popular_result


# id phpto like-dislike  attribute
if __name__ == '__main__':
    user_id = 15206350
    tools = VKTools(access_token)
    params = tools.get_profile_info(user_id)
    pprint(params)
    named_interests = params['interests'] + params['books'] + params['music']
    worksheets = tools.search_worksheet(params, 50)
    worksheet = worksheets.pop()
    photos = tools.get_photos(worksheet['id'])
    pprint(photos)
    photo = photos.pop()
