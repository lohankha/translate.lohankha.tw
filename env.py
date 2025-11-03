# env.py
import os
from dotenv import load_dotenv

def load_env():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, '.env')

    if not os.environ.get("DJANGO_ENV_LOADED"):
        load_dotenv(dotenv_path=env_path)
        os.environ["DJANGO_ENV_LOADED"] = "1"
