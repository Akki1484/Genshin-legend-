class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "5282482434"
    sudo_users = [5282482434]
    GROUP_ID = -1002255658511
    TOKEN = "7815890014:AAEkrcZOnvlv2PUU2A5IjEvxM7Xo3aYpwWo"
    mongo_url = "mongodb://atlas-sql-67a756a7fe83b52654c45c5e-q1tei.a.query.mongodb.net/sample_mflix?ssl=true&authSource=admin"
    PHOTO_URL = ["https://ibb.co/zhnpSBGR"]
    SUPPORT_CHAT = "genshincatcher"
    UPDATE_CHAT = "genshincatcher"
    BOT_USERNAME = "GenshinC_bot"
    CHARA_CHANNEL_ID = "-1002255658511"
    api_id =  22085011
    api_hash = "c098a7ff625c4a7c486cb6453aab0002"

    
class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
