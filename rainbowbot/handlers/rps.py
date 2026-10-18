import json
import random

from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from openai import AsyncOpenAI

from ..config import AI_API_KEY, AI_BASE_URL, AI_MODEL

router = Router()

SYSTEM_PROMPT = '''
это игра — камень-ножницы-бумага (с нюансом).
пиши с маленькой буквы.
ответ пользователя всегда будет JSON такого формата:
{
  "guess": "текущий выбор (например, бумага)",
  "previous_guess": "предыдущий выбор (например, камень)"
}
ты должен ответить СТРОГО ВАЛИДНЫМ JSON БЕЗ MARKDOWN такого формата:
{
  "wins": true или false,
  "explanation": "объяснение результата"
}
правила:
1. пользователь может выбрать всё что угодно, включая любой предмет, любого человека, любое явление и т.д.
2. определи результат на основе обычных свойств выбранных объектов и их взаимодействия
3. если `guess` может победить `previous_guess`, поставь `"wins": true`
4. если `guess` не может победить `previous_guess`, поставь `"wins": false`
5. если `guess` невозможно понять, поставь `"wins": false` и объясни, что не понимаешь что это
6. если оба объекта практически одинаковы и ни один не получает не получает преимущества, поставь `"wins": false`
7. не придумывай свойства объектов без необходимости, используй наиболее очевидные и общеизвестные свойства
8. не считай автоматически, что более большое, сильное, редкое или абстрактное понятие побеждает
9. `explanation` должно быть коротким, понятным и соответствовать результату. можно использовать юмор, если он подходит ситуации
примеры:
1. previous_guess: Бумага, guess: Ножницы
ответ:
emoji: ✂️, wins: true
explanation: "ножницы разрезают бумагу, это же классика."
2. previous_guess: Камень, guess: Второй камень
emoji: 🪨, wins: false
explanation: "да ладно, второй камень вообще ничем не отличается от первого камня, ты не можешь победить просто взяв второй камень."
3. previous_guess: Камень, guess: хлеб
emoji: 🍞, wins: false
explanation: "хлеб может конечно и является основой жизни, но камень всё равно намного сильнее обычного хлеба и запросто разобьёт его в крошки."
4. previous_guess: Камень, guess: ъфыхъфхйъхйхйхйхц
emoji: 🤷‍♂️, wins: false
explanation: "что такое "ъфыхъфхйъхйхйхйхц"? для меня это просто каша из букв и камень всё равно побеждает потому что я вообще понятию не имею что ты хочешь сказать."
'''

RPS_GAMES = {}
ENCODED_CHARS = {
    'a': chr(8203),
    'b': chr(8204),
    'c': chr(8205)
}
DECODED_CHARS = {v: k for k, v in ENCODED_CHARS.items()}
AVAIL_CHARS = list(ENCODED_CHARS.keys())

ai = AsyncOpenAI(
    base_url=AI_BASE_URL,
    api_key=AI_API_KEY
)

def encode_game_id(decoded):
    encoded = ''
    for char in decoded:
        encoded += ENCODED_CHARS[char]
    return encoded

def decode_game_id(encoded):
    decoded = ''
    for char in encoded:
        decoded += DECODED_CHARS[char]
    return decoded

async def incorrect_format(query, text='не стирайте уже введёное!', code='incorrect-format'):
    await query.answer(
        results=[
        #    types.InlineQueryResultArticle(
        #        id='rps/incorrect',
        #        title=f'🪨✂️📄 не стирайте уже введёное!',
        #        description='пж',
        #        input_message_content=types.InputTextMessageContent(
        #            content='НЕ СТИРАЙТЕ'
        #        )
        #    )
        ],
        button=types.InlineQueryResultsButton(
            text=text,
            start_parameter=f'rps_{code}'
        ),
        cache_time=0,
        is_personal=True
    )

@router.inline_query(F.query.startswith('rps') or F.query.startswith('rock') or F.query.startswith('whatbeat') or F.query.startswith('what beat'))
async def rpsinline(query):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text='⏳',
        callback_data='wait'
    ))
    rich_blocks = [
        types.InputRichBlockParagraph(
            text='🪨✂️📄 подождите...'
        )
    ]
    await query.answer(
        results=[
            types.InlineQueryResultArticle(
                id='rps/new',
                title='🪨✂️📄 камень-ножницы-бумага',
                description='начать игру',
                input_message_content=types.InputRichMessageContent(
                    rich_message=types.InputRichMessage(
                        blocks=rich_blocks
                    )
                ),
                reply_markup=builder.as_markup()
            )
        ],
        cache_time=0,
        is_personal=True
    )

@router.inline_query(F.query.startswith(chr(8288)))
async def rpsgame(query):
    data = query.query.split(chr(8288))
    if len(data) != 3:
        await incorrect_format(query)
    game_id = decode_game_id(data[1])
    game = RPS_GAMES.get(game_id)
    if not game:
        await incorrect_format(query, 'вы нажали куда-то не туда', 'game-not-found')
        return
    if query.from_user.id != game['player']:
        rich_blocks = [
            types.InputRichBlockParagraph(
                text='😡 не твоя игра'
            ),
            types.RichMessageButtons(
                buttons=[
                    types.RichMessageButton(
                        text='➡️ создать свою ⬅️',
                        #style='primary',
                        switch_inline_query_current_chat='rps'
                    )
                ]
            )
        ]
        return await query.answer(
            results=[
                types.InlineQueryResultArticle(
                    id='rps/not_yours/{game_id}',
                    title='😡 не твоя игра',
                    description='кыш',
                    input_message_content=types.InputRichMessageContent(
                        rich_message=types.InputRichMessage(
                            blocks=rich_blocks
                        )
                    )
                )
            ],
            cache_time=0,
            is_personal=True
        )
    la = game['history'][-1]
    user_query = data[2]
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text='⏳',
        callback_data='wait'
    ))
    if not user_query:
        rich_blocks = [
            types.InputRichBlockParagraph(
                text=[
                    'что бьёт ',
                    types.RichTextBold(
                        text=la
                    ),
                    ': ',
                    types.RichTextButton(
                        button=types.RichMessageButton(
                            text='ответить',
                            #style='primary',
                            switch_inline_query_current_chat=f'{chr(8288)}{encode_game_id(game_id)}{chr(8288)}'
                        )
                    )
                ]
            )
        ]
        return await query.answer(
            results=[
                types.InlineQueryResultArticle(
                    id='rps/pls_type/{game_id}',
                    title=f'🪨✂️📄 что бьёт {la}?',
                    description='начинайте писать!',
                    input_message_content=types.InputRichMessageContent(
                        rich_message=types.InputRichMessage(
                            blocks=rich_blocks
                        )
                    )
                )
            ],
            cache_time=0,
            is_personal=True
        )
    rich_blocks = [
        types.InputRichBlockParagraph(
            text=types.RichTextBold(
                text=f'{user_query} vs {la}'
            )
        ),
        types.InputRichBlockFooter(
            text=types.RichTextItalic(
                text='бьём... бьём... бьём...'
            )
        )
    ]
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text='⏳',
        callback_data='wait'
    ))
    await query.answer(
        results=[
            types.InlineQueryResultArticle(
                id='rps/game/{game_id}',
                title=f'🪨✂️📄 {user_query} vs {la}',
                description='БИТЬ',
                input_message_content=types.InputRichMessageContent(
                    rich_message=types.InputRichMessage(
                        blocks=rich_blocks
                    )
                ),
                reply_markup=builder.as_markup()
            )
        ],
        cache_time=0,
        is_personal=True
    )

@router.chosen_inline_result(F.result_id.startswith('rps/'))
async def rpsresult(result):
    data = result.result_id.split('/')
    if data[1] == 'new':
        game_id = ''
        for i in range(10):
            game_id = f'{game_id}{random.choice(AVAIL_CHARS)}'
        RPS_GAMES[game_id] = {
            'player': result.from_user.id,
            'history': [
                'камень'
            ]
        }
        rich_blocks = [
            types.InputRichBlockParagraph(
                text=[
                    'что бьёт ',
                    types.RichTextBold(
                        text='камень'
                    ),
                    ': ',
                    types.RichTextButton(
                        button=types.RichMessageButton(
                            text='ответить',
                            #style='primary',
                            switch_inline_query_current_chat=f'{chr(8288)}{encode_game_id(game_id)}{chr(8288)}'
                        )
                    )
                ]
            )
        ]
        return await result.bot.edit_message_text(
            inline_message_id=result.inline_message_id,
            rich_message=types.InputRichMessage(
                blocks=rich_blocks
            )
        )
    elif data[1] in ['pls_type', 'not_yours']:
        return
    query_data = result.query.split(chr(8288))
    game_id = decode_game_id(query_data[1])
    game = RPS_GAMES.get(game_id)
    if not game:
        return
    la = game['history'][-1]
    user_query = query_data[2]
    #yaubyutebyazatochtoslilchayketosoobscheniekotoroeyaperedumalotpravlyatiudalil
    response = await ai.chat.completions.create(
        model=AI_MODEL,
        messages=[
            {
                'role': 'system',
                'content': SYSTEM_PROMPT
            },
            {
                'role': 'user',
                'content': json.dumps({
                    'guess': user_query,
                    'previous_guess': la
                })
            }
        ]
    )
    data = json.loads(response.choices[0].message.content)
    wins = data['wins']
    explanation = data['explanation']
    emoji = '✅' if wins else '❌'
    rich_blocks = [
        types.InputRichBlockParagraph(
            text=[
                types.RichTextBold(
                    text=f'{emoji} {user_query} '
                ),
                types.RichTextButton(
                    button=types.RichMessageButton(
                        text='БЬЁТ' if wins else 'НЕ БЬЁТ',
                        style='success' if wins else 'danger',
                        #disabled=types.DisabledButton()
                        callback_data='nothing'
                    )
                ),
                types.RichTextBold(
                    text=f' {la}!'
                )
            ]
        ),
        types.InputRichBlockFooter(
            text=explanation
        ),
        types.InputRichBlockButtons(
            buttons=[
                types.RichMessageButton(
                    text='продолжить' if wins else 'начать новую игру',
                    switch_inline_query_current_chat=f'{chr(8288)}{query_data[1]}{chr(8288)}' if wins else 'rps'
                )
            ]
        )
    ]
    if wins:
        game['history'].append(user_query)
    else:
        del RPS_GAMES[game_id]
    await result.bot.edit_message_text(
        inline_message_id=result.inline_message_id,
        rich_message=types.InputRichMessage(
            blocks=rich_blocks
        )
    )
