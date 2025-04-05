from dataclasses import dataclass

@dataclass
class TelegramKey:
    admin_id: int
    bot_token: str
    tdjson_path: str
    api_id: int
    api_hash: str
    
# trading account
TG_KEY = TelegramKey(
    admin_id = 1234, # your tg id in int, use @username_to_id_bot
    bot_token= 'noti_bot_token',
    tdjson_path= "~/td/tdlib/lib/libtdjson.so", # example of tdjson library path
    api_id = 1234, # your tdjson api_id @https://my.telegram.org/apps
    api_hash = "your tdjson hash", # @https://my.telegram.org/apps
) 