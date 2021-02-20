#------------------------------------- https://github.com/m4mallu/ashesOFpheonix -------------------------------------#

import asyncio
import logging
import os
import time
from plugins.help_text import start_bot, bot_settings
from plugins.sub_functions import view_thumbnail, delete_thumbnail, del_thumb_confirm, close_button
from plugins.multimedia import rename_file, convert_to_video
from plugins.make_another_copy import convert_to_doc_copy, convert_to_video_copy, clear_media
from pyrogram import Client, ContinuePropagation
from pyrogram.types import (InlineKeyboardMarkup, InlineKeyboardButton, InputMediaDocument,
                            InputMediaVideo, InputMediaAudio)
from helper.ffmfunc import duration
from helper.ytdlfunc import downloadvideocli, downloadaudiocli
from translation import Translation
from plugins.generate_screenshot import generate_screen_shot

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

if bool(os.environ.get("ENV", False)):
    from sample_config import Config
else:
    from config import Config


@Client.on_callback_query()
async def catch_youtube_fmtid(bot, update):
    cb_data = update.data
    if cb_data.startswith("ytdata||"):
        yturl = cb_data.split("||")[-1]
        format_id = cb_data.split("||")[-2]
        media_type = cb_data.split("||")[-3].strip()
        print(media_type)
        if media_type == 'audio':
            buttons = InlineKeyboardMarkup([[InlineKeyboardButton(
                "Audio", callback_data=f"{media_type}||{format_id}||{yturl}"),
                InlineKeyboardButton("Document", callback_data=f"docaudio||{format_id}||{yturl}")]])
        else:
            buttons = InlineKeyboardMarkup([[InlineKeyboardButton(
                "Video", callback_data=f"{media_type}||{format_id}||{yturl}"),
                InlineKeyboardButton("Document", callback_data=f"docvideo||{format_id}||{yturl}")]])

        await update.edit_message_reply_markup(buttons)

    else:
        raise ContinuePropagation


@Client.on_callback_query()
async def catch_youtube_dldata(bot, update):
    thumb_image_path = os.getcwd() + "/" + "thumbnails" + "/" + str(update.from_user.id) + ".jpg"
    yt_thumb_image_path = os.getcwd() + "/" + "YouTubeThumb" + "/" + str(update.from_user.id) + ".jpg"
    if os.path.exists(thumb_image_path):
        thumb_image = thumb_image_path
    else:
        thumb_image = yt_thumb_image_path
    file_name = str(Config.PRE_FILE_TXT)
    cb_data = update.data
    # Callback Data Check (for Youtube formats)
    if cb_data.startswith(("video", "audio", "docaudio", "docvideo")):
        yturl = cb_data.split("||")[-1]
        format_id = cb_data.split("||")[-2]
        if not cb_data.startswith(("video", "audio", "docaudio", "docvideo")):
            print("no data found")
            raise ContinuePropagation

        new_filext = "%(title)s.%(ext)s"
        filext = file_name + new_filext
        saved_file_path = os.getcwd() + "/" + "downloads" + "/" + str(update.from_user.id) + "/"
        if not os.path.isdir(saved_file_path):
            os.makedirs(saved_file_path)
        dl_folder = [f for f in os.listdir(saved_file_path)]
        for f in dl_folder:
            try:
                os.remove(os.path.join(saved_file_path, f))
            except IndexError:
                pass
        await update.edit_message_text(text=Translation.DOWNLOAD_START)
        filepath = os.path.join(saved_file_path, filext)

        audio_command = [
            "youtube-dl",
            "-c",
            "--prefer-ffmpeg",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", format_id,
            "-o", filepath,
            yturl,

        ]

        video_command = [
            "youtube-dl",
            "-c",
            "--embed-subs",
            "-f", f"{format_id}+bestaudio",
            "-o", filepath,
            "--hls-prefer-ffmpeg", yturl]

        loop = asyncio.get_event_loop()
        med = None
        if cb_data.startswith("audio"):
            filename = await downloadaudiocli(audio_command)
            med = InputMediaAudio(
                media=filename,
                caption=os.path.basename(filename),
                title=os.path.basename(filename),
                thumb=thumb_image
            )

        if cb_data.startswith("video"):
            description = Translation.CUSTOM_CAPTION_VIDEO
            filename = await downloadvideocli(video_command)
            dur = round(duration(filename))
            med = InputMediaVideo(
                media=filename,
                duration=dur,
                caption=description,
                thumb=thumb_image,
                supports_streaming=True
            )

        if cb_data.startswith("docaudio"):
            filename = await downloadaudiocli(audio_command)
            med = InputMediaDocument(
                media=filename,
                caption=os.path.basename(filename),
                thumb=thumb_image
            )

        if cb_data.startswith("docvideo"):
            description = Translation.CUSTOM_CAPTION_DOC
            filename = await downloadvideocli(video_command)
            dur = round(duration(filename))
            med = InputMediaDocument(
                media=filename,
                caption=description,
                thumb=thumb_image
            )

        if med:
            loop.create_task(send_file(bot, update, med))

        else:
            print("med not found")


######################################### CB Data query for Bot Settings ###############################################
    else:
        # Callback Data Check (for bot settings)
        if cb_data.startswith(("close", "view_thumb", "del_thumb", "conf_thumb", "start_help", "settings",
                               "rename_doc", "convert_video", "d_copy", "v_copy", "clear_med")):
            if "close" in cb_data:
                await close_button(bot, update)
            elif "view_thumb" in cb_data:
                await view_thumbnail(bot, update)
            elif "del_thumb" in cb_data:
                await delete_thumbnail(bot, update)
            elif "conf_thumb" in cb_data:
                await del_thumb_confirm(bot, update)
            elif "start_help" in cb_data:
                await start_bot(bot, update)
            elif "settings" in cb_data:
                await bot_settings(bot, update)
            elif "rename_doc" in cb_data:
                await rename_file(bot, update)
            elif "convert_video" in cb_data:
                await convert_to_video(bot, update)
            elif "d_copy" in cb_data:
                await convert_to_doc_copy(bot, update)
            elif "v_copy" in cb_data:
                await convert_to_video_copy(bot, update)
            elif "clear_med" in cb_data:
                await clear_media(bot, update)
########################################################################################################################

async def send_file(bot, update, med):
    try:
        await update.edit_message_text(text=Translation.UPLOAD_START)
        await bot.send_chat_action(chat_id=update.message.chat.id, action="upload_document")
        await update.edit_message_media(media=med)
        a = await bot.send_message(text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG, chat_id=update.message.chat.id)
        time.sleep(5)
        await a.delete()
        await generate_screen_shot(bot, update)
    except IndexError as e:
        print(e)
