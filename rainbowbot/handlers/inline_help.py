from aiogram import F, Router, types

router = Router()

@router.inline_query()
async def helpinline(query):
    rich_blocks = [
        types.InputRichBlockParagraph(
            text=types.RichTextBold(
                text='📖 помощь по инлайну',
            )
        ),
        types.InputRichBlockDetails(
            summary='🌛 развлечения',
            blocks=[
                types.InputRichBlockList(
                    items=[
                        types.InputRichBlockListItem(
                            blocks=[
                                types.InputRichBlockParagraph(
                                    text=[
                                        types.RichTextButton(
                                            button=types.RichMessageButton(
                                                text='🔮 акинатор',
                                                switch_inline_query_current_chat='aki'
                                            )
                                        ),
                                        ' — джинн, читающий ваши мысли'
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        types.InputRichBlockFooter(
            text=[
                types.RichTextItalic(
                    text='есть предложения для новых функций/игр? пишите @aryu20\n'
                ),
                types.RichTextUrl(
                    text=types.RichTextItalic(
                        text='я опенсурс!'
                    ),
                    url='https://github.com/rainbowcatreal/rainbowbot'
                )
            ]
        )
    ]
    await query.answer(
        results=[
            types.InlineQueryResultArticle(
                id='help',
                title='📖 помощь по инлайну',
                description='что есть в инлайне?',
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
