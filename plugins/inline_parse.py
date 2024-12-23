from pyrogram import Client
from pyrogram.errors import MessageNotModified
from pyrogram.types import (
    InlineQuery,
    InputTextMessageContent,
    InlineQueryResultArticle,
    ChosenInlineResult,
    InputMediaVideo,
)

from methods import TgParseHub
from plugins.start import get_supported_platforms
from utiles.filters import platform_filter
from utiles.utile import progress


@Client.on_inline_query(~platform_filter)
async def inline_parse_tip(_, iq: InlineQuery):
    results = [
        InlineQueryResultArticle(
            title="聚合解析",
            description="请在聊天框输入链接",
            input_message_content=InputTextMessageContent(get_supported_platforms()),
            thumb_url="https://i.imgloc.com/2023/06/15/Vbfazk.png",
        )
    ]
    await iq.answer(results=results, cache_time=1)


@Client.on_inline_query(platform_filter)
async def call_inline_parse(_, iq: InlineQuery):
    pp = await TgParseHub().parse(iq.query)
    await pp.inline_upload(iq)


async def callback(
    current, total, status: str, client: Client, inline_message_id, pp: TgParseHub
):
    text = progress(current, total, status)
    if not text:
        return
    text = f"{pp.operate.content_and_no_url}\n\n{text}"
    try:
        await client.edit_inline_text(
            inline_message_id, text, reply_markup=pp.operate.button(hide_summary=True)
        )
    except MessageNotModified:
        ...


@Client.on_chosen_inline_result()
async def inline_result_jx(client: Client, cir: ChosenInlineResult):
    if not cir.result_id.startswith("download_"):
        return
    index = int(cir.result_id.split("_")[1])
    imid = cir.inline_message_id

    try:
        pp = await TgParseHub().parse(cir.query)
        await pp.download(
            callback,
            (client, imid, pp),
        )
    except Exception as e:
        await client.edit_inline_text(imid, f"{e}")
        raise e
    else:
        await client.edit_inline_text(
            imid,
            f"{pp.operate.content_and_no_url}\n\n上 传 中...",
            reply_markup=pp.operate.button(hide_summary=True),
        )
        await client.edit_inline_media(
            imid,
            media=InputMediaVideo(
                pp.operate.download_result.media[index].path
                if isinstance(pp.operate.download_result.media, list)
                else pp.operate.download_result.media.path,
                caption=pp.operate.content_and_no_url,
            ),
            reply_markup=pp.operate.button(),
        )
