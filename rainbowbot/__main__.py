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

from .bot import main
from . import setup

# создаём папку data (если не существует)
data_folder = Path('data').mkdir(exist_ok=True)

# добавляем url_to_file_id.json в него
if not Path('data/url_to_file_id.json').is_file():
    with open('data/url_to_file_id.json', 'w') as f:
        json.dump({}, f)

if __name__ == '__main__':
    asyncio.run(main())
