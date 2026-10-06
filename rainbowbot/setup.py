import logging
from datetime import datetime

class BeautifulFormatter(logging.Formatter):
    LEVEL_COLORS = {
        'DEBUG': '\x1b[1;32mDBG\x1b[0m',
        'INFO': '\x1b[1;34mINF\x1b[0m',
        'WARNING': '\x1b[1;33mWRN\x1b[0m',
        'ERROR': '\x1b[1;31mERR\x1b[0m',
        'CRITICAL': '\x1b[1;35mCRT\x1b[0m'
    }

    def format(self, record):
        message = record.getMessage()
        level = self.LEVEL_COLORS[record.levelname]
        date = datetime.fromtimestamp(record.created)
        time = f'{date.hour:02}:{date.minute:02}:{date.second:02}'
        log = f'\x1b[30;1m{time}\x1b[0m {level} {message}'
        return log

handler = logging.StreamHandler()
handler.setFormatter(BeautifulFormatter())

logging.basicConfig(
    level=logging.INFO,
    handlers=[handler]
)
