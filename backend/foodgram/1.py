import os
from dotenv import load_dotenv
from pathlib import Path
# load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = Path.cwd() / 'infra' / '.env'
load_dotenv(dotenv_path=ENV_PATH)
a = os.getenv('ALLOWED_HOSTS')
# ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split()
print(ENV_PATH)