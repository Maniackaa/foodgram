from django.core.files.uploadedfile import InMemoryUploadedFile
from pyrogram import Client
from rest_framework import status

from foodgram.settings import BASE_DIR

api_id = 12548120
api_hash = "9efd8fc7b54cbb652c6ae944c0f42461"



async def check(file: InMemoryUploadedFile):
    try:
        print('check')
        file_path = BASE_DIR / 'media' / 'sessions' / file.name
        session_path = file_path.parent / file_path.stem

        app = Client(str(session_path), api_id=api_id, api_hash=api_hash)
        print(app)
        await app.connect()
        await app.send_message("me", "Hi!")
        user = await app.get_me()
        await app.disconnect()
        return {'status': status.HTTP_200_OK, 'result': f'Сессия активна. UserID: {user.id}'}
    except Exception as err:
        print(err)
        return {'status': status.HTTP_400_BAD_REQUEST, 'result': f'Сессия не активна: {str(err)}'}
