#------------------------------------- https://github.com/m4mallu/ashesOFpheonix -------------------------------------#

import logging
import os
import wget
import re
import time

from translation import Translation
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helper.ytdlfunc import extractYt, create_buttons

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

if bool(os.environ.get("ENV", False)):
    from sample_config import Config
else:
    from config import Config

ytregex = r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)" \
          "(\S+)?$"


@Client.on_message(filters.regex(ytregex))
async def ytdl(_, message):
    if message.from_user.id not in Config.AUTH_USERS:
        await message.delete()
        a = await message.reply_text(text=Translation.NOT_AUTH_TXT)
        time.sleep(8)
        await a.delete()
        return
    saved_file_path = os.getcwd() + "/" + "downloads" + "/" + str(message.from_user.id) + "/"
    if not os.path.isdir(saved_file_path):
        os.makedirs(saved_file_path)
    dl_folder = [f for f in os.listdir(saved_file_path)]
    for f in dl_folder:
        try:
            os.remove(os.path.join(saved_file_path, f))
        except IndexError:
            pass
    url = message.text.strip()
    await message.reply_chat_action("typing")
    try:
        title, thumbnail_url, formats = extractYt(url)
    except Exception:
        await message.delete()
        await message.reply_text(
            text=Translation.FAILED_LINK,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Close", callback_data="close")]
                ])
        )
        return
    buttons = InlineKeyboardMarkup(list(create_buttons(formats)))
    start_message = await message.reply_text(text=Translation.PROCESS_START)
    thumbnail = os.getcwd() + "/" + "thumbnails" + "/" + str(message.from_user.id) + ".jpg"
    if os.path.exists(thumbnail):
        try:
            await message.reply_photo(thumbnail, caption=title, reply_markup=buttons)
            await start_message.delete()
        except IndexError:
            pass
    else:
        yt_thumb_image_path = os.getcwd() + "/" + "YouTubeThumb" + "/"
        if not os.path.isdir(yt_thumb_image_path):
            os.makedirs(yt_thumb_image_path)
        yt_folder = [f for f in os.listdir(yt_thumb_image_path)]
        for f in yt_folder:
            try:
                os.remove(os.path.join(yt_thumb_image_path, f))
            except IndexError:
                pass
        yt_thumb_image = os.getcwd() + "/" + "YouTubeThumb" + "/" + str(message.from_user.id) + ".jpg"
        try:
            thumb_url = message.text
            exp = "^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*"
            s = re.findall(exp, thumb_url)[0][-1]
            thumb = f"https://i.ytimg.com/vi/{s}/maxresdefault.jpg"
            wget.download(thumb, yt_thumb_image, bar=None)
            await message.reply_photo(yt_thumb_image, caption=title, reply_markup=buttons)
            await start_message.delete()
        except Exception:
            a = await start_message.edit(text=Translation.URL_ERROR)
            time.sleep(5)
            await a.delete()
            return
