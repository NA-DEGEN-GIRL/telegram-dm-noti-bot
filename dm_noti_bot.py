import json
import ctypes
import asyncio
from telegram import Bot
from key_tg import TG_KEY
import os
import uuid
import logging

# 로깅 설정: 콘솔과 파일 모두에 출력
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')
file_handler = logging.FileHandler('dm_noti_bot.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s'))
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s'))
logger = logging.getLogger()
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

TD_RECV_TIMEOUT = 0.01     # 최대한 짧게
bot_token = TG_KEY.bot_token
dm_noti_bot = Bot(token=bot_token)

tdjson_path = os.path.expanduser(TG_KEY.tdjson_path)
td_json = ctypes.CDLL(tdjson_path)
tdjson_create = td_json.td_json_client_create
tdjson_create.restype = ctypes.c_void_p
tdjson_send = td_json.td_json_client_send
tdjson_send.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
tdjson_receive = td_json.td_json_client_receive
tdjson_receive.argtypes = [ctypes.c_void_p, ctypes.c_double]
tdjson_receive.restype = ctypes.c_char_p
tdjson_destroy = td_json.td_json_client_destroy
tdjson_destroy.argtypes = [ctypes.c_void_p]
client = tdjson_create()

msg_queue = asyncio.Queue(maxsize=2000)  # 모든 이벤트가 들어갈 큐

async def async_print(*args, **kwargs):
    logger.info(*args)

async def td_send_async(query):
    try:
        query_str = json.dumps(query)
        tdjson_send(client, query_str.encode('utf-8'))
    except Exception as e:
        logger.error(f"Error sending query: {e}")

async def td_receive():
    try:
        result = tdjson_receive(client, TD_RECV_TIMEOUT)
        if result:
            return json.loads(result.decode('utf-8'))
    except Exception as e:
        logger.error(f"Error receiving data: {e}")
    return None

async def set_log_verbosity_level(level):
    await td_send_async({'@type': 'setLogVerbosityLevel', 'new_verbosity_level': level})

async def get_chat_info(chat_id):
    try:
        request_id = str(uuid.uuid4())
        await td_send_async({'@type': 'getChat', 'chat_id': chat_id, '@extra': request_id})
        while True:
            update = await td_receive()
            if update and update.get('@extra') == request_id and update.get('id') == chat_id:
                return update
    except Exception as e:
        logger.error(f"Error getting chat info: {e}")

async def get_user_info(user_id):
    try:
        request_id = str(uuid.uuid4())
        await td_send_async({'@type': 'getUser', 'user_id': user_id, '@extra': request_id})
        while True:
            update = await td_receive()
            if update and update.get('@extra') == request_id and update.get('id') == user_id:
                return update
    except Exception as e:
        logger.error(f"Error getting user info: {e}")

async def start_tdlib_user_account():
    try:
        await td_send_async({
            '@type': 'setTdlibParameters',
            'use_test_dc': False,
            'database_directory': 'tdlib',
            'use_file_database': False,
            'use_chat_info_database': True,
            'use_message_database': False,
            'use_secret_chats': False,
            'api_id': int(TG_KEY.api_id),
            'api_hash': TG_KEY.api_hash,
            'system_language_code': 'en',
            'device_model': 'Desktop',
            'application_version': '1.0',
        })
        while True:
            update = await td_receive()
            if update and update['@type'] == 'updateAuthorizationState':
                auth_state = update['authorization_state']
                if auth_state['@type'] == 'authorizationStateWaitPhoneNumber':
                    phone_number = input("Please enter your phone number: ")
                    await td_send_async({'@type': 'setAuthenticationPhoneNumber', 'phone_number': phone_number})
                elif auth_state['@type'] == 'authorizationStateWaitCode':
                    code = input("Please enter the authentication code you received: ")
                    await td_send_async({'@type': 'checkAuthenticationCode', 'code': code})
                elif auth_state['@type'] == 'authorizationStateWaitPassword':
                    password = input("Please enter your 2-step verification password: ")
                    await td_send_async({'@type': 'checkAuthenticationPassword', 'password': password})
                elif auth_state['@type'] == 'authorizationStateReady':
                    await async_print("Authorization complete.")
                    break
            await asyncio.sleep(0.1)
    except Exception as e:
        logger.error(f"Error during authentication: {e}")

async def send_alert_message(msg_text):
    try:
        chat_id = TG_KEY.admin_id
        await dm_noti_bot.send_message(chat_id=chat_id, text=msg_text)
    except Exception as e:
        logger.error(f"Error sending alert message: {e}")

### 메시지 빠짐 없이 큐에 넣어주는 Task
async def receive_task():
    while True:
        event = await td_receive()
        if event:   # 이벤트가 없다면 그냥 패스(짧은 timeout)
            await msg_queue.put(event)
        await asyncio.sleep(0.01)

### 큐에 담긴 메시지 하나씩 처리(딜레이 분리)
async def process_task():
    while True:
        event = await msg_queue.get()
        try:
            if event.get("@type") == "updateNewMessage":
                message = event['message']
                chat_id = message.get('chat_id')
                chat_info = await get_chat_info(chat_id)
                if chat_info and chat_info['type']['@type'] == 'chatTypePrivate':
                    sender_id = message['sender_id']['user_id']
                    user_info = await get_user_info(sender_id)
                    if user_info.get('type').get('@type') != 'userTypeBot' and user_info.get('id') != TG_KEY.admin_id:
                        # main에서 느리게 처리하던 구간도 큐 분리로 안전
                        await asyncio.sleep(0.5)
                        chat_info = await get_chat_info(chat_id)
                        unread_count = chat_info.get('unread_count')
                        if unread_count == 0:
                            msg_queue.task_done()
                            continue
                        tg_handle = user_info.get('usernames', {}).get('active_usernames', [None])[0]
                        tg_name = (user_info.get('first_name', '').strip() + ' ' + user_info.get('last_name', '').strip()).strip()
                        display_name = tg_name + (f" @{tg_handle}" if tg_handle else "")
                        content = message.get('content', {})
                        if content.get('@type') == "messageText":
                            text = content['text']['text']
                            msg_text = f"{display_name}:\n{text[:50]}"
                            await send_alert_message(msg_text)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
        finally:
            msg_queue.task_done()
        await asyncio.sleep(0.01)

async def main():
    try:
        await set_log_verbosity_level(1)
        await start_tdlib_user_account()
        # receive_task(), process_task()를 동시에 실행
        await asyncio.gather(
            receive_task(),
            process_task()
        )
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}")
    finally:
        tdjson_destroy(client)
        logger.info("TDLib client destroyed. Exiting...")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt. Exiting...")
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
