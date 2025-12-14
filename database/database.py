from pymongo import MongoClient
from config import MONGODB_URI, DATABASE_NAME

# MongoDB Client
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

# Collections
users_collection = db['users']
downloads_collection = db['downloads']
subscriptions_collection = db['subscriptions']
force_sub_channels_collection = db['force_sub_channels']
bot_config_collection = db['bot_config']
redeem_codes_collection = db['redeem_codes']
ongoing_processes_collection = db['ongoing_processes']


def init_db():
    """Initialize the database by creating indexes"""
    # Create indexes for better performance
    users_collection.create_index("id", unique=True)
    force_sub_channels_collection.create_index("channel_id", unique=True)
    bot_config_collection.create_index("setting_name", unique=True)
    redeem_codes_collection.create_index("code", unique=True)
    ongoing_processes_collection.create_index("user_id")
    
    print("MongoDB initialized successfully!")


def get_db():
    """Get database instance"""
    return db
