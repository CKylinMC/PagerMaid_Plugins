"""
PagerMaid Plugin Soutu

Some of codes was copied from pic2sticker.

**This not a ready-to-use plugin, you need to specify a API KEY first!**
"""
import re
import requests
import time
import json
import os
from bs4 import BeautifulSoup
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
使用 SauceNao 搜索图片
对一个图片回复
-soutu
即可，使用
-soutu full
尝试自动从Pixiv下载原图
"""

#TODO: Use redis to allow set key from commands
@listener(is_plugin=True, outgoing=True, command=alias_command("soutu"), diagnostics=True, ignore_edited=True,
          description=helpmsg,
          parameters="<searchengine>")
async def sendatwrap(context):
    engine = 'saucenao'
    fi = False
    try:
        context.edit("准备中...")
    except:
        pass
    message = await context.get_reply_message()
    if len(context.parameter)>0 and (context.parameter[0] == "full" or context.parameter[0] == "org"):
        fi = True
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
                await context.edit("正在准备...")
            except:
                pass
            # image = await resize_image(photo)
            # aimage = await resize_image(photo)
            aimage = Image.open(photo)
            afile = BytesIO()
            afile.name = "asticker.png"
            aimage.save(afile,"PNG")
            afile.seek(0)
            try:
                await context.edit("正在搜索...")
            except:
                pass
            await searchByPySauceNao(afile,context,fi)
    except Exception as e:
        try:
            await context.edit("搜索出错:"+str(e))
        except:
            pass

async def searchByPySauceNao(photo,context,reqFullImg=False):
    s = requests.Session()
    sauce = SauceNao(api_key=SauceNaoAPIKEY)
    results = await sauce.from_file(photo)
    if len(results) == 0:
        try:
            await context.edit("没有找到结果...")
        except:
            pass
    else:
        try:
            await context.edit("已找到匹配...")
        except:
            pass
        text = "**[{title}]({sourceurl})**\n作者: [{author}]({authorurl})\n[{provider}]({url})({similarity}%)".format(
            title = results[0].title,
            sourceurl = results[0].source_url,
            author = results[0].author_name,
            authorurl = results[0].author_url,
            provider = results[0].index,
            url = results[0].url,
            similarity = results[0].similarity
        )
        target = s.get(results[0].thumbnail)
        await bot.send_file(context.chat_id,target.content,caption=text)
        if reqFullImg:
            try:
                await context.edit("正在上传原图...")
            except:
                pass
            r = s.get(results[0].url)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'lxml')
                dataelem = soup.find('meta', id='meta-preload-data')
                if dataelem is not None :
                    try:
                        data = json.loads(soup.find('meta', id='meta-preload-data')['content'])
                        iid = list(data['illust'].keys())[0]
                        original = data['illust'][list(data['illust'].keys())[0]]['urls']['original']
                        org = s.get(original,headers={'Referer':'https://app-api.pixiv.net/'})
                        if org.status_code == 200:
                            await bot.send_file(context.chat_id,org.content,caption="Pixiv illust="+iid+"\n原图")
                            try:
                                await context.delete()
                            except:
                                pass
                        else:
                            try:
                                await context.edit("下载原图失败")
                            except:
                                pass
                    except Exception as e:
                        try:
                            await context.edit("解析原图信息失败:"+str(e))
                        except:
                            pass
                else:
                    try:
                        await context.edit("获取原图信息失败")
                    except:
                        pass
            else:
                try:
                    await context.edit("获取原图失败，原图可能已经删除")
                except:
                    pass
        else:
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