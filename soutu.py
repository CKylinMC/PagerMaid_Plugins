"""
PagerMaid Plugin Soutu

Core codes copied from 666wcy/search_photo-telegram-bot-heroku and pic2sticker.py

"""
import re
import requests
import time
import os
from io import BytesIO
from telethon.tl.types import DocumentAttributeFilename, MessageMediaPhoto, MessageMediaWebPage
from PIL import Image, ImageOps
from math import floor
from pagermaid import bot
from pagermaid.utils import alias_command,pip_install,lang
from pagermaid.listener import listener

try:
    pip_install("pysaucenao")
    from pysaucenao import SauceNao
except:
    pass
SauceNaoAPIKEY = ""
engines = ['saucenao']

helpmsg = """
以图搜图

"""

@listener(is_plugin=True, outgoing=True, command=alias_command("soutu"), diagnostics=True, ignore_edited=True,
          description=helpmsg,
          parameters="<searchengine>")
async def sendatwrap(context):
    engine = 'saucenao'
    try:
        context.edit("准备中...")
    except:
        pass
    if len(context.parameter)>=1:
        if context.parameter[0] in engines:
            engine = context.parameter[0]
        else:
            try:
                await context.edit(lang('arg_error'))
            except:
                pass
            return
    message = await context.get_reply_message()
    if message and message.media:
        if isinstance(message.media, MessageMediaPhoto):
            photo = BytesIO()
            photo = await bot.download_media(message.photo, photo)
        elif isinstance(message.media, MessageMediaWebPage):
            try:
                await context.edit(lang('sticker_type_not_support'))
            except:
                pass
            return
        elif "image" in message.media.document.mime_type.split('/'):
            photo = BytesIO()
            try:
                await context.edit(lang('sticker_downloading'))
            except:
                pass
            await bot.download_file(message.media.document, photo)
            if (DocumentAttributeFilename(file_name='sticker.webp') in
                    message.media.document.attributes):
                try:
                    await context.edit(lang('sticker_type_not_support'))
                except:
                    pass
                return
        else:
            try:
                await context.edit(lang('sticker_type_not_support'))
            except:
                pass
            return
    else:
        try:
            await context.edit(lang('sticker_reply_not_sticker'))
        except:
            pass
        return
    try:
        if photo:
            try:
                await context.edit(lang('sticker_resizing'))
            except:
                pass
            # image = await resize_image(photo)
            # aimage = await resize_image(photo)
            aimage = Image.open(photo)
            afile = BytesIO()
            afile.name = "asticker.png"
            aimage.save(afile,"PNG")
            afile.seek(0)
            await searchByPySauceNao(afile,context)
    except Exception as e:
        try:
            await context.edit("搜索出错:"+str(e))
        except:
            pass

async def searchByPySauceNao(photo,context,requireFullImg = False):
    session = requests.Session()
    sauce = SauceNao(api_key=SauceNaoAPIKEY)
    results = await sauce.from_file(photo)
    if len(results) == 0:
        await edit(context,"没有找到结果")
    else:
        text = "**[{title}]({sourceurl})**\n作者: [{author}]({authorurl})\n[{provider}]({url})({similarity}%)".format(
            title = results[0].title,
            sourceurl = results[0].source_url,
            author = results[0].author_name,
            authorurl = results[0].author_url,
            provider = results[0].index,
            url = results[0].url,
            similarity = results[0].similarity
        )
        target = None
        if requireFullImg:
            target = session.get(results[0].thumbnail)
        else:
            target = session.get(results[0].thumbnail)
        await bot.send_file(context.chat_id,target.content,caption=text)
        try:
            await context.delete()
        except:
            pass


async def resize_image(photo):
    image = Image.open(photo)
    maxsize = (1024, 1024)
    if (image.width and image.height) < 1024:
        size1 = image.width
        size2 = image.height
        if image.width > image.height:
            scale = 1024 / size1
            size1new = 1024
            size2new = size2 * scale
        else:
            scale = 1024 / size2
            size1new = size1 * scale
            size2new = 1024
        size1new = floor(size1new)
        size2new = floor(size2new)
        size_new = (size1new, size2new)
        image = image.resize(size_new)
    else:
        image.thumbnail(maxsize)
    return image


async def edit(context,text=""):
    try:
        context.edit(text)
    except:
        pass
    return