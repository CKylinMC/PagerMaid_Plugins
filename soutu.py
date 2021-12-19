"""
PagerMaid Plugin Soutu

Core codes copied from 666wcy/search_photo-telegram-bot-heroku and pic2sticker.py

"""
import re
import requests
import base64
import time
import datetime
from urllib import parse
from bs4 import BeautifulSoup
import os
from io import BytesIO
from telethon.tl.types import DocumentAttributeFilename, MessageMediaPhoto, MessageMediaWebPage
from PIL import Image, ImageOps
from math import floor
from pagermaid import bot
from pagermaid.utils import alias_command,pip_install,lang
from pagermaid.listener import listener

engines = ['iqdb','saucenao']

helpmsg = """
以图搜图

"""

@listener(is_plugin=True, outgoing=True, command=alias_command("soutu"), diagnostics=True, ignore_edited=True,
          description=helpmsg,
          parameters="<searchengine>")
async def sendatwrap(context):
    engine = 'saucenao'
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

    if photo:
        file = BytesIO()
        try:
            await context.edit(lang('sticker_resizing'))
        except:
            pass
        image = await resize_image(photo)
        if pic_round:
            try:
                await context.edit(lang('us_static_rounding'))
            except:
                pass
            image = await rounded_image(image)
        file.name = "sticker.webp"
        image.save(file, "WEBP")
        file.seek(0)
        try:
            await context.edit(lang('us_static_uploading'))
        except:
            pass
        await bot.send_file(context.chat_id, file, force_document=False)
        try:
            await context.delete()
        except:
            pass

async def saucenao(photo_file,context):
    try:
        url="https://saucenao.com/search.php"
        #url = "https://saucenao.com"
        Header = {
            'Host': 'saucenao.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0',
            'Accept': 'text/html, application/xhtml+xml, application/xml;q = 0.9, */*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        payloaddata = {
            'frame': 1,
            'hide': 0,
            'database': 999,
        }
        #photo_file=requests.get(photo_url)
        files = {"file": (
        "saucenao.jpg", photo_file.content, "image/png")}
        context.edit("正在搜索中...")
        #bot.send_message(chat_id=chat_id,text="正在搜索saucenao")
        r = session.post(url=url, headers=Header, data=payloaddata,files=files)
        #r = session .get(url=url,headers=Header)
        soup = BeautifulSoup(r.text, 'html.parser')
        #print(soup.prettify())
        result=0
        choice=0
        for img in soup.find_all('div', attrs={'class': 'result'}):  # 找到class="wrap"的div里面的所有<img>标签
            #print(img)
            if('hidden' in str(img['class']))==False:
                try:
                    name=img.find("div",attrs={'class': 'resulttitle'}).get_text()
                    img_url=str(img.img['src'])
                    describe_list=img.find("div",attrs={'class': 'resultcontentcolumn'})
                    url_list = img.find("div", attrs={'class': 'resultcontentcolumn'}).find_all("a",  attrs={'class': 'linkify'})
                    similarity = str(img.find("div", attrs={'class': 'resultsimilarityinfo'}).get_text())
                    print(name)
                except:
                    continue
                try:
                    describe = str(url_list[0].previous_sibling.string)
                    describe_id = str(url_list[0].string)
                    describe_url = str(url_list[0]['href'])
                    auther_url = str(url_list[1]['href'])
                    auther = str(url_list[1].previous_sibling.string)
                    auther_id = str(url_list[1].string)
                    '''print(name)
                    print(img_url)
                    print(describe)
                    print(describe_id)
                    print(similarity)
                    print(auther)
                    print(auther_id)
                    print(describe_url)'''
                    text = f"{name}\n{describe}[{describe_id}]({describe_url})\n{auther}:[{auther_id}]({auther_url})\n相似度{similarity}"
                except:
                    '''print(describe_list.get_text())
                    print(describe_list.strong.string)
                    print(describe_list.strong.next_sibling.string)
                    print(describe_list.small.string)
                    print(describe_list.small.next_sibling.next_sibling.string)'''
                    auther = str(describe_list.strong.string)
                    auther_id = str(describe_list.strong.next_sibling.string)
                    describe = str(describe_list.small.string) + "\n" + str(describe_list.small.next_sibling.next_sibling.string)
                    text = f"{name}\n{auther}:{auther_id}\n{describe}\n相似度{similarity}"

                photo_file = session.get(img_url)
                bot.send_photo(chat_id=context.chat_id,photo=photo_file.content,parse_mode='Markdown',caption=text)
                result=1
        if result==0:
            try:
                await content.edit("无匹配结果")
            except:
                pass
    except:
        try:
            await content.edit("搜索出错")
        except:
            pass