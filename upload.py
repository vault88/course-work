import requests, json
# from settings import YANDEX_TOKEN, VK_TOKEN, VK_USER_ID
from tqdm import trange, tqdm

VK_USER_ID = input('Введите id пользователя Вконтакте: ')
YANDEX_TOKEN = input('Введите токен Яндекс Диска: ')
VK_TOKEN = input('Введите токен VK: ')

URL = 'https://cloud-api.yandex.net/v1/disk/resources'
YANDEX_FOLDER = 'backups'

if YANDEX_FOLDER == '':
    folder_path = ''
else:
    folder_path = '/' + YANDEX_FOLDER + '/'


class VkParser:
    def __init__(self, token):
        self.params = {
            'access_token': token, 
            'v':'5.131'
            }

    def get_id(self):
        URL = 'https://api.vk.com/method/users.get'
        user_params = {
            'user_ids': VK_USER_ID,
            }
        response = requests.get(URL, params={**self.params, **user_params}).json()
        id = response['response'][0]['id']
        return id

    def get_photos(self, q=5, album='profile'): # wall — фотографии со стены, profile — фотографии профиля, saved — сохраненные фотографии. Возвращается только с ключом доступа пользователя.
        URL = 'https://api.vk.com/method/photos.get'
        user_params = {
            'owner_id': self.get_id(),
            'album_id': album, 
            'photo_sizes': 1,
            'extended': 1,
            'count': q
            }
        response = requests.get(URL, params={**self.params, **user_params}).json()
        name_list = []
        photos_list = []
        for item in response['response']['items']:
            photo = max(item['sizes'], key=lambda x: list(x.values()))
            size = photo['type']
            url = photo['url']
            date = item['date']
            likes = item['likes']['count']
            if any(x.startswith(str(likes) + '.jpg') for x in name_list):
            # if str(likes) + '.jpg' in name_list:
                file_name = str(likes) + '-' + str(date)
            else:
                file_name = str(likes)
            name_list.append(file_name + '.jpg' + '|' + url)
            photos_list.append(
                {
                    'file_name': file_name + '.jpg',
                    'size': size
                }
                )
        with open('info.json', 'wt') as dumped:
            json.dump(photos_list, dumped, ensure_ascii=False)
        return name_list


class YaUploader:
    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
            }

    def create_folder(self, folder_name):
        params = {'path': folder_name, 'overwrite': True}
        response = requests.put(URL, headers=self.get_headers(), params=params)

    def upload(self, link, path):
        params = {'path': path, 'url': link, 'overwrite': True}
        url = '/upload'
        response = requests.post(URL + url, headers=self.get_headers(), params=params)  


if __name__ == '__main__':
    user = VkParser(VK_TOKEN)
    uploader = YaUploader(YANDEX_TOKEN)
    uploader.create_folder(folder_path)
    name_list = user.get_photos(10)
    # for element in user.get_photos():
    #     uploader.upload(element.split('|')[1], folder_path + element.split('|')[0])
    for element in trange(len(name_list), desc=f"Загрузка файлов на Яндекс Диск: "):
        uploader.upload(name_list[element].split('|')[1], folder_path + name_list[element].split('|')[0])
    print('Фото успешно загружены на Яндекс Диск\nСписок загруженных файлов доступен в файле info.json')
