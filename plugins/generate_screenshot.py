#------------------------------------- https://github.com/m4mallu/ashesOFpheonix -------------------------------------#

import os
import time
import logging
import shutil
from pyrogram.types import InputMediaPhoto
from pyrogram.errors import FloodWait
from helper.gen_ss_help import generate_screen_shots
from translation import Translation
from plugins.trim_video import trim

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

#---------------------------------- Generating Screenshots from the downloaded media ---------------------------------#
async def generate_screen_shot(bot, update):
    tmp_directory_for_each_user = os.path.join(os.getcwd(), "Screenshots", str(update.from_user.id))
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)
    ss_folder = [f for f in os.listdir(tmp_directory_for_each_user)]
    for f in ss_folder:
        try:
            os.remove(os.path.join(tmp_directory_for_each_user, f))
        except IndexError:
            pass
    saved_file_path = os.getcwd() + "/" + "downloads" + "/" + str(update.from_user.id) + "/"
    for file in os.listdir(saved_file_path):
        dir_content = (os.path.join(saved_file_path, file))
        if dir_content is not None:
            images = await generate_screen_shots(
                dir_content,
                tmp_directory_for_each_user,
                5,
                9
            )
            media_album_p = []
            if images is not None:
                i = 0
                for image in images:
                    if os.path.exists(image):
                        if i == 0:
                            media_album_p.append(
                                InputMediaPhoto(
                                    media=image,
                                    caption=Translation.CAPTION_TEXT,
                                    parse_mode="html"
                                )
                            )
                        else:
                            media_album_p.append(
                                InputMediaPhoto(
                                    media=image
                                )
                            )
                        i = i + 1
            await bot.send_chat_action(chat_id=update.message.chat.id, action="upload_photo")
            try:
                await bot.send_media_group(
                    chat_id=update.message.chat.id,
                    disable_notification=True,
                    reply_to_message_id=update.message.message_id,
                    media=media_album_p
                )
            except FloodWait as e:
                time.sleep(e.x)
            try:
                shutil.rmtree(tmp_directory_for_each_user)
                #---------- Jumping to Trim media Function for generating sample video ----------#
                await trim(bot, update)
            except Exception:
                pass
