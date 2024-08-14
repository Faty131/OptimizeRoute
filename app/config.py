from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    HERE_API_KEY = os.getenv('HERE_API_KEY')
