import asyncio
import os
import re
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
import yt_dlp

BOT_TOKEN = "8884399790:AAEtfajTXcCyx48c_qSf9EjznJFbBUKfzoU"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

COMMON_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'cookiefile': 'cookies.txt',
    'extractor_args': {'youtube': {'player_client': ['android']}},
    'http_headers': {
        'User-Agent': 'com.google.android.youtube/17.36.4 (Linux; U; Android 12; GB) gzip',
    },
}

def is_valid_url(text):
    pattern = r'(https?://)?(www\.)?(youtube\.com|youtu\.be|instagram\.com|vm\.tiktok\.com|tiktok\.com)/.+'
    return re.match(pattern, text.strip()) is not None

def get_video_info(url):
    ydl_opts = {**COMMON_OPTS}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            'title': info.get('title', "Noma'lum"),
            'thumbnail': info.get('thumbnail', ''),
            'duration': info.get('duration', 0),
            'uploader': info.get('uploader', ''),
        }

def download_video(url, audio_only=False):
    os.makedirs('downloads', exist_ok=True)
    if audio_only:
        ydl_opts = {
            **COMMON_OPTS,
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:
        ydl_opts = {
            **COMMON_OPTS,
            'format': 'bestvideo[ext=mp4][filesize<50M]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
        }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if audio_only:
            filename = filename.rsplit('.', 1)[0] + '.mp3'
        return filename

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Salom! Men video yuklovchi botman.\n\n"
        "📎 YouTube yoki Instagram havolasini yuboring,\n"
        "men esa Video yoki Audio yuklab beraman!\n\n"
        "🔗 Misol: https://youtube.com/shorts/..."
    )

@dp.message(F.text)
async def handle_url(message: types.Message):
    url = message.text.strip()
    if not is_valid_url(url):
        await message.answer("❌ Iltimos, YouTube yoki Instagram havolasini yuboring.")
        return
    wait_msg = await message.answer("⏳ Ma'lumot olinmoqda...")
    try:
        info = get_video_info(url)
        title = info['title']
        uploader = info['uploader']
        duration_sec = info['duration']
        minutes = duration_sec // 60
        seconds = duration_sec % 60
        duration_str = f"{minutes}:{seconds:02d}" if duration_sec else "Noma'lum"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🎬 Video", callback_data=f"video|{url}"),
                InlineKeyboardButton(text="🎵 Audio", callback_data=f"audio|{url}"),
            ]
        ])
        caption = (
            f"🎬 <b>{title}</b>\n"
            f"👤 {uploader}\n"
            f"⏱ {duration_str}\n\n"
            f"⬇️ Yuklab olish formatini tanlang:"
        )
        await wait_msg.delete()
        if info['thumbnail']:
            try:
                await message.answer_photo(
                    photo=info['thumbnail'],
                    caption=caption,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            except:
                await message.answer(caption, reply_markup=keyboard, parse_mode="HTML")
        else:
            await message.answer(caption, reply_markup=keyboard, parse_mode="HTML")
    except Exception as e:
        await wait_msg.delete()
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}\n\nHavolani tekshirib qaytadan yuboring.")

@dp.callback_query(F.data.startswith("video|"))
async def download_video_handler(callback: types.CallbackQuery):
    url = callback.data.split("|", 1)[1]
    wait_msg = await callback.message.answer("⬇️ Video yuklanmoqda... iltimos kuting ⏳")
    await callback.answer()
    try:
        filepath = download_video(url, audio_only=False)
        with open(filepath, 'rb') as f:
            video_data = f.read()
        await callback.message.answer_video(
            video=types.BufferedInputFile(video_data, filename="video.mp4"),
            caption="✅ Mana videongiz!"
        )
        os.remove(filepath)
        await wait_msg.delete()
    except Exception as e:
        await wait_msg.delete()
        await callback.message.answer(f"❌ Video yuklab bo'lmadi: {str(e)}")

@dp.callback_query(F.data.startswith("audio|"))
async def download_audio_handler(callback: types.CallbackQuery):
    url = callback.data.split("|", 1)[1]
    wait_msg = await callback.message.answer("⬇️ Audio yuklanmoqda... iltimos kuting ⏳")
    await callback.answer()
    try:
        filepath = download_video(url, audio_only=True)
        with open(filepath, 'rb') as f:
            audio_data = f.read()
        await callback.message.answer_audio(
            audio=types.BufferedInputFile(audio_data, filename="audio.mp3"),
            caption="✅ Mana musiqangiz!"
        )
        os.remove(filepath)
        await wait_msg.delete()
    except Exception as e:
        await wait_msg.delete()
        await callback.message.answer(f"❌ Audio yuklab bo'lmadi: {str(e)}")

async def main():
    print("✅ Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
