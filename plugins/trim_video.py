#------------------------------------- https://github.com/m4mallu/ashesOFpheonix -------------------------------------#
import os
import time
import logging
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from helper.gen_ss_help import cult_small_video
from translation import Translation

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

async def trim(bot, update):
    output_directory = os.path.join(os.getcwd(), "sample_video")
    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)
    trim_folder = [f for f in os.listdir(output_directory)]
    for f in trim_folder:
        try:
            os.remove(os.path.join(output_directory, f))
        except IndexError:
            pass
    thumb_image_path = os.getcwd() + "/" + "thumbnails" + "/" + str(update.from_user.id) + ".jpg"
    if not os.path.exists(thumb_image_path):
        thumb_image_path = None
    saved_file_path = os.getcwd() + "/" + "downloads" + "/" + str(update.from_user.id) + "/"
    for file in os.listdir(saved_file_path):
        dir_content = (os.path.join(saved_file_path, file))
        if dir_content is not None:
            start_time = "00:04:00"
            end_time = "00:05:00"
            # Let's give a code pause to trim fun: to over ride execution delay
            time.sleep(5)
            a = await bot.send_message(text=Translation.TRIM_WAIT, chat_id=update.message.chat.id)
            time.sleep(3)
            try:
                med = await cult_small_video(dir_content, output_directory, start_time, end_time)
            except FloodWait as e:
                # code pause for the trimming function to be completed
                time.sleep(e.x)
            else:
                await a.delete()
                await bot.send_chat_action(chat_id=update.message.chat.id, action="upload_video")
                if med is not None:
                    try:
                        await bot.send_video(
                            chat_id=update.message.chat.id,
                            video=med,
                            thumb=thumb_image_path,
                            caption="Sample Video:",
                            supports_streaming=True,
                        )
                    except FloodWait as e:
                        time.sleep(e.x)
                try:
                    os.remove(med)
                    await bot.send_message(
                        text=Translation.MAKE_A_COPY_TEXT,
                        chat_id=update.message.chat.id,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [InlineKeyboardButton("📘 Document", callback_data="d_copy"),
                                 InlineKeyboardButton("🎞 Video", callback_data="v_copy")],
                                [InlineKeyboardButton(" Close", callback_data="clear_med")]
                            ])
                    )
                except Exception:
                    pass
