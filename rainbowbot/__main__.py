'''
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠤⠤⠤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠣⣀⣀⣀⠜⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣠⡶⠒⠶⢦⣄⠀⠀⠀⠀⣾⠓⢆⠀⠀⠀⠀⣠⡞⠹⡆⠀⠀⢀⣤⠶⠛⠙⢶⣤
⠹⢆⠀⠀⠀⠉⠳⠦⠀⣼⠇⠀⠊⠙⠉⠋⠙⠉⡠⠀⢷⠀⠴⠋⠀⠀⠀⢀⡼⠋
⠀⠀⢳⡄⠀⠀⠀⢀⣴⠟⠀⣴⣧⠀⠀⠀⠀⣼⣦⠀⠈⢷⡀⠀⠀⠀⠴⡏⠁⠀
⠀⠀⣟⡁⠀⠀⠀⢸⠇⠀⠀⢻⠏⠀⠀⠀⠀⠻⡟⠀⠀⠈⡧⠀⠀⠀⣈⣿⠀⠀
⠀⠀⣸⠟⠀⠀⠀⠈⠳⣠⣀⠀⠀⠀⠀⠀⠀⠀⡀⣀⣴⠞⠁⠀⠀⠀⢻⡆⠀⠀
⠀⠀⠉⠶⠖⠆⠀⠀⢰⠞⠉⠠⠛⠓⢤⠀⣰⠞⠂⠘⢦⡀⠀⠀⠘⠛⠛⠃⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⡟⠀⠀⣤⣤⣴⠛⠀⣿⣀⣤⠀⠈⠷⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
'''

import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv

from . import setup

# загружаем секреты из .env
env_file = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_file)
# /КОНЕЦ/

from .bot import main

# создаём папку data (если не существует)
data_folder = Path('data').mkdir(exist_ok=True)

# добавляем url_to_file_id.json в него
if not Path('data/url_to_file_id.json').is_file():
    with open('data/url_to_file_id.json', 'w') as f:
        json.dump({}, f)

if __name__ == '__main__':
    asyncio.run(main())
