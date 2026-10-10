import json
import secrets
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from aiogram import F, Router, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..aki import Akinator, CantGoBackAnyFurther

AKINATOR_GAMES = {}

router = Router()

# функции чтения и сохранения URL → file_id
def utfi_read():
    with open('data/url_to_file_id.json', 'r') as f:
        data = json.load(f)
    return data

def utfi_write(data):
    with open('data/url_to_file_id.json', 'w') as f:
        json.dump(data, f)

def utfi_add(url, file_id):
    data = utfi_read()
    data[url] = file_id
    utfi_write(data)
    return data

# хранение URL → FILE_ID
UTFI = utfi_read()

# команда в группе
@router.message(Command('aki'))
async def akicmd(message, command):
    msg = await message.reply('⏳')
    game_id = secrets.token_hex(16)
    aki = Akinator()
    await aki.start_game(language=command.args if command.args else 'ru', child_mode=True)
    AKINATOR_GAMES[game_id] = {
        'player': message.from_user.id,
        'game': aki
    }
    rich_blocks = [
        types.InputRichBlockParagraph(
            text=[
                types.RichTextBold(
                    text=f'{aki.step}. '
                ),
                aki.question
            ]
        ),
        types.InputRichBlockFooter(
            text=f'прогресс: {aki.progression}%'
        ),
        types.InputRichBlockButtons(
            buttons=[
                types.RichMessageButton(
                    text='да',
                    callback_data=f'aki/{game_id}/y',
                    style='success'
                ),
                types.RichMessageButton(
                    text='нет',
                    callback_data=f'aki/{game_id}/n',
                    style='danger'
                )
            ]
        ),
        types.InputRichBlockButtons(
            buttons=[
                types.RichMessageButton(
                    text='не знаю',
                    callback_data=f'aki/{game_id}/idk'
                )
            ]
        ),
        types.InputRichBlockButtons(
            buttons=[
                types.RichMessageButton(
                    text='возможно',
                    callback_data=f'aki/{game_id}/p'
                ),
                types.RichMessageButton(
                    text='скорее нет',
                    callback_data=f'aki/{game_id}/pn'
                )
            ]
        ),
        types.InputRichBlockButtons(
            buttons=[
                types.RichMessageButton(
                    text='назад',
                    callback_data=f'aki/{game_id}/back'
                )
            ]
        )
    ]
    await msg.edit_text(
        rich_message=types.InputRichMessage(
            blocks=rich_blocks
        )
    )

# инлайн
@router.inline_query(F.query.startswith('aki'))
async def akiinline(query):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text='⏳',
        callback_data='wait'
    ))
    await query.answer(
        results=[
            types.InlineQueryResultArticle(
                id='aki/new/ru',
                title=f'🔮 акинатор 🇷🇺',
                description='начать новую игру на русском',
                input_message_content=types.InputTextMessageContent(
                    message_text='🔮 подождите...'
                ),
                reply_markup=builder.as_markup()
            ),
            types.InlineQueryResultArticle(
                id='aki/new/en',
                title=f'🔮 акинатор 🇺🇲',
                description='начать новую игру на английском',
                input_message_content=types.InputTextMessageContent(
                    message_text='🔮 подождите...'
                ),
                reply_markup=builder.as_markup()
            )
        ],
        cache_time=0,
        is_personal=True
    )

@router.chosen_inline_result(F.result_id.startswith('aki/new/'))
async def akichoosen(result):
    game_id = secrets.token_hex(16)
    language = result.result_id.split('/')[2]
    aki = Akinator()
    await aki.start_game(language=language, child_mode=True)
    AKINATOR_GAMES[game_id] = {
        'player': result.from_user.id,
        'game': aki
    }
    rich_blocks = [
        types.InputRichBlockParagraph(
            text=[
                types.RichTextBold(
                    text=f'{aki.step}. '
                ),
                aki.question
            ]
        ),
        types.InputRichBlockFooter(
            text=f'прогресс: {aki.progression}%'
        ),
        types.InputRichBlockButtons(
            buttons=[
                types.RichMessageButton(
                    text='да',
                    callback_data=f'aki/{game_id}/y',
                    style='success'
                ),
                types.RichMessageButton(
                    text='нет',
                    callback_data=f'aki/{game_id}/n',
                    style='danger'
                )
            ]
        ),
        types.InputRichBlockButtons(
            buttons=[
                types.RichMessageButton(
                    text='не знаю',
                    callback_data=f'aki/{game_id}/idk'
                )
            ]
        ),
        types.InputRichBlockButtons(
            buttons=[
                types.RichMessageButton(
                    text='возможно',
                    callback_data=f'aki/{game_id}/p'
                ),
                types.RichMessageButton(
                    text='скорее нет',
                    callback_data=f'aki/{game_id}/pn'
                )
            ]
        ),
        types.InputRichBlockButtons(
            buttons=[
                types.RichMessageButton(
                    text='назад',
                    callback_data=f'aki/{game_id}/back'
                )
            ]
        )
    ]
    await result.bot.edit_message_text(
        inline_message_id=result.inline_message_id,
        rich_message=types.InputRichMessage(
            blocks=rich_blocks
        )
    )

# обработка нажатий
@router.callback_query(F.data.startswith('aki/'))
async def akibutton(call):
    global UTFI
    if call.inline_message_id:
        _ = {
            'inline_message_id': call.inline_message_id
        }
    else:
        _ = {
            'chat_id': call.message.chat.id,
            'message_id': call.message.message_id
        }
    data = call.data.split('/')
    game_id = data[1]
    game = AKINATOR_GAMES.get(game_id)
    if not game:
        return await call.answer('данная игра не найдена в базе. запустите новую игру', show_alert=True)
    if game['player'] != call.from_user.id:
        return await call.answer('😠 не твоя игра', show_alert=True)
    aki = AKINATOR_GAMES.get(game_id)['game']
    if data[2] not in ['y', 'n', 'idk', 'p', 'pn', 'back']:
        return await call.answer('эээээээ, что?', show_alert=True)
    if data[2] == 'back':
        try:
            await aki.back()
        except CantGoBackAnyFurther:
            return await call.answer('это первый вопрос, куда ты назад собирался идти?', show_alert=True)
    else:
        await aki.answer(data[2])
    await call.answer()
    if aki.win:
        url = aki.photo
        file_id = UTFI.get(url)
        if not file_id:
            msg_image = await call.bot.send_photo(
                chat_id=-1003776214752,
                caption='#UTFI',
                photo=url
            )
            file_id = msg_image.photo[-1].file_id
            UTFI = utfi_add(url, file_id)
        if aki.finished:
            timestamp = int(datetime.strptime(aki.last_played, '%d/%m/%Y - %HH%M').replace(tzinfo=ZoneInfo('Europe/Paris')).timestamp())
            rich_blocks = [
                types.InputRichBlockPhoto(
                    photo=types.InputMediaPhoto(
                        media=file_id
                    )
                ),
                types.InputRichBlockParagraph(
                    text=types.RichTextBold(
                        text=f'ура 🎉 я угадал вашего персонажа {aki.name_proposition}!'
                    )
                ),
                types.InputRichBlockPullQuotation(
                    text=aki.description_proposition,
                    credit=aki.pseudo if aki.pseudo else None
                ),
                types.InputRichBlockFooter(
                    text=[
                        f'был сыгран уже {aki.already_played} раз\n'
                        'последний раз был отыгран ',
                        types.RichTextDateTime(
                            text=aki.last_played,
                            unix_time=timestamp,
                            date_time_format='r'
                        )
                    ]
                )
            ]
        else:
            rich_blocks = [
                types.InputRichBlockPhoto(
                    photo=types.InputMediaPhoto(
                        media=aki.photo
                    )
                ),
                types.InputRichBlockParagraph(
                    text=types.RichTextBold(
                        text=f'вы загадали {aki.name_proposition}?'
                    )
                ),
                types.InputRichBlockPullQuotation(
                    text=aki.description_proposition,
                    credit=aki.pseudo if aki.pseudo else None
                ),
                types.InputRichBlockButtons(
                    buttons=[
                        types.RichMessageButton(
                            text='да',
                            style='success',
                            callback_data=f'aki/{game_id}/y'
                        ),
                        types.RichMessageButton(
                            text='нет',
                            style='danger',
                            callback_data=f'aki/{game_id}/n'
                        )
                    ]
                )
            ]
    else:
        if aki.finished:
            rich_blocks = [
                types.InputRichBlockParagraph(
                    text='простите, я сдаюсь.'
                ),
                types.InputRichBlockFooter(
                    text='вы выиграли! 🥳'
                )
            ]
        else:
            rich_blocks = [
                types.InputRichBlockParagraph(
                    text=[
                        types.RichTextBold(
                            text=f'{aki.step}. '
                        ),
                        aki.question
                    ]
                ),
                types.InputRichBlockFooter(
                    text=f'прогресс: {aki.progression}%'
                ),
                types.InputRichBlockButtons(
                    buttons=[
                        types.RichMessageButton(
                            text='да',
                            callback_data=f'aki/{game_id}/y',
                            style='success'
                        ),
                        types.RichMessageButton(
                            text='нет',
                            callback_data=f'aki/{game_id}/n',
                            style='danger'
                        )
                    ]
                ),
                types.InputRichBlockButtons(
                    buttons=[
                        types.RichMessageButton(
                            text='не знаю',
                            callback_data=f'aki/{game_id}/idk'
                        )
                    ]
                ),
                types.InputRichBlockButtons(
                    buttons=[
                        types.RichMessageButton(
                            text='возможно',
                            callback_data=f'aki/{game_id}/p'
                        ),
                        types.RichMessageButton(
                            text='скорее нет',
                            callback_data=f'aki/{game_id}/pn'
                        )
                    ]
                ),
                types.InputRichBlockButtons(
                    buttons=[
                        types.RichMessageButton(
                            text='назад',
                            callback_data=f'aki/{game_id}/back'
                        )
                    ]
                )
            ]
    await call.bot.edit_message_text(
        **_,
        rich_message=types.InputRichMessage(
            blocks=rich_blocks
        )
    )
