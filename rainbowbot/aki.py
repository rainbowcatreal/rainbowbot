'''
модуль для игры в акинатора
'''

import re
import curl_cffi
import asyncio
from bs4 import BeautifulSoup

ANSWERS = {
    'y': '0',
    'n': '1',
    'idk': '2',
    'p': '3',
    'pn': '4'
}

class InvalidChoiceError(Exception):
    def __init__(self, choice):
        super().__init__(choice)

class CantGoBackAnyFurther(Exception):
    def __init__(self):
        super().__init__()

class Akinator():
    def __init__(self):
        self.question = ''
        self.step = 1
        self.progression = 0.0
        self.slp = ''
        self.akitude = 'serein_2'
        self._signature = ''
        self._session = ''
        self._identifiant = ''
        self.win = False
        self.finished = False
        self.name_proposition = ''
        self.description_proposition = ''
        self.pseudo = ''
        self.photo = ''
        self.already_played = 0
        self.last_played = ''
        self._base_url = ''
        self.id_proposition = 0
        self.flag_photo = 0
        self.child_mode = False
        self._no_question = False
        self.is_nsfw_proposition = False
        self._step = 1
        self._client = curl_cffi.AsyncSession(timeout=30, impersonate='firefox')

    async def start_game(self, language='en', child_mode=False):
        self._base_url = f'https://{language}.akinator.com'
        self.child_mode = child_mode
        r = await self._client.post(f'{self._base_url}/game', data={
            'sid': 1,
            'cm': self.child_mode,
            'anim': False
        })
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        self.question = soup.find('p', id='question-label').text
        self._session = re.search(
            r"localStorage\.setItem\('session', '(.+?)'\)",
            r.text
        ).group(1)
        self._identifiant = re.search(
            r"localStorage\.setItem\('identifiant', '(.+?)'\)",
            r.text
        ).group(1)

    async def _handle_answer_response(self, response):
        #print(response)
        self._step = response['step']
        if 'id_proposition' in response:
            self.win = True
            self.id_proposition = response['id_proposition']
            self.name_proposition = response['name_proposition']
            self.description_proposition = response['description_proposition']
            self.photo = response['photo']
            self.pseudo = response['pseudo']
            self.is_nsfw_proposition = (response['valide_contrainte'] == 0)
            self._no_question = (response['no_question'] == '1')
        else:
            self.win = False
            self.question = response['question']
            self.progression = float(response['progression'])

    async def answer(self, answer):
        if answer not in ANSWERS:
            raise InvalidChoiceError(answer)
        if self.win:
            if answer == 'y':
                r = await self._client.post(f'{self._base_url}/choice', data={
                    'session': self._session,
                    'identifiant': self._identifiant,
                    'step': self._step,
                    'sid': 1,
                    'pid': self.id_proposition,
                    'charac_name': self.name_proposition,
                    'charac_desc': self.description_proposition
                })
                # let timesSelected = "337";
                self.already_played = int(re.search(
                    r'let timesSelected = "(.+?)";',
                    r.text
                ).group(1))
                self.last_played = re.search(
                    r'let previousPlayed = "(.+?)";',
                    r.text
                ).group(1)
                self.finished = True
            elif answer == 'n':
                if self._no_question:
                    self.win = False
                    self.finished = True
                    return
                r = await self._client.post(f'{self._base_url}/exclude', data={
                    'step': self._step,
                    'sid': 1,
                    'cm': self.child_mode,
                    'progression': self.progression,
                    'session': self._session,
                    'forward_answer': '1'
                })
                resp = r.json()
                await self._handle_answer_response(resp)
                self.step += 1
        else:
            r = await self._client.post(f'{self._base_url}/answer', data={
                'step': self._step,
                'progression': self.progression,
                'sid': 1,
                'cm': self.child_mode,
                'answer': ANSWERS[answer],
                'step_last_proposition': self.slp,
                'session': self._session
            })
            resp = r.json()
            await self._handle_answer_response(resp)
            self.step += 1

    async def back(self):
        if self.step <= 1:
            raise CantGoBackAnyFurther()
        r = await self._client.post(f'{self._base_url}/cancel_answer', data={
            'step': self._step,
            'progression': self.progression,
            'sid': 1,
            'cm': self.child_mode,
            'session': self._session
        })
        resp = r.json()
        await self._handle_answer_response(resp)
        self.step -= 1

    @property
    def akitude_url(self):
        return f'https://ru.akinator.com/assets/img/akitudes_670x1096/{self.akitude}.png'

async def main():
    aki = Akinator()
    await aki.start_game(language=input('Select language: '), child_mode=input('Do you want child mode? ') == 'y')
    while not aki.finished:
        if aki.win:
            print(f'Are you thinking of {aki.name_proposition}? ({aki.description_proposition})')
            if aki.is_nsfw_proposition:
                print('Do note that Akinator considers this character not for children and you have child mode ON.')
        else:
            print(f'{aki.step}: {aki.question}\n(Progression: {aki.progression}%)')
        answer = input('>> ')
        if answer == 'b':
            try:
                await aki.back()
            except CantGoBackAnyFurther:
                pass
        else:
            try:
                await aki.answer(answer)
            except InvalidChoiceError:
                pass
    if aki.win:
        print('Yay I won!')
        print(aki.name_proposition)
        print(aki.description_proposition)
        print(aki.pseudo)
        print(aki.photo)
        print('Already played', aki.already_played, 'times')
        print('Previous played', aki.last_played)
    else:
        print('You have defeated me.')

if __name__ == '__main__':
    asyncio.run(main())
