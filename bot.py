import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from pytubefix import YouTube
import re
import tempfile

logging.basicConfig(level=logging.INFO)

TOKEN = "8884399790:AAEWTjkV9XZWb9j81CiA6kc9M_qjTpBU640"

bot = Bot(token=TOKEN)
dp = Dispatcher()

def is_youtube_url(url: str) -> bool:
    patterns = [
        r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+',
        r'(https?://)?(www\.)?youtu\.be/.+'
    ]
    return any(re.match(p, url) for p in patterns)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Salom! 👋 Men TinglaHub botiman!\n\n"
        "YouTube havolasini yuboring — video yoki musiqa yuklab beraman! 🎬🎵"
    )

@dp.message(F.text)
async def handle_link(message: Message):
    url = message.text.strip()

    if not is_youtube_url(url):
        await message.answer("❌ Faqat YouTube havolalarini qabul qilaman!")
        return

    try:
        yt = YouTube(url)
        title = yt.title
        duration = yt.length
        mins = duration // 60
        secs = duration % 60

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🎬 Video", callback_data=f"video|{url}"),
                InlineKeyboardButton(text="🎵 Audio", callback_data=f"audio|{url}")
            ]
        ])

        await message.answer(
            f"🎥 <b>{title}</b>\n⏱ {mins}:{secs:02d}\n\nNimani yuklab olmoqchisiz?",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Error: {e}")
        await message.answer("❌ Xatolik yuz berdi. Havolani tekshirib qayta yuboring.")

@dp.callback_query(F.data.startswith("video|"))
async def download_video(callback: CallbackQuery):
    url = callback.data.split("|", 1)[1]
    await callback.message.answer("⏳ Video yuklanmoqda...")
    await callback.answer()

    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').last()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = stream.download(output_path=tmpdir)
            with open(path, 'rb') as f:
                await callback.message.answer_video(f, caption=f"🎬 {yt.title}")
    except Exception as e:
        logging.error(f"Video error: {e}")
        await callback.message.answer("❌ Video yuklab bo'lmadi. Boshqa havola sinab ko'ring.")

@dp.callback_query(F.data.startswith("audio|"))
async def download_audio(callback: CallbackQuery):
    url = callback.data.split("|", 1)[1]
    await callback.message.answer("⏳ Musiqa yuklanmoqda...")
    await callback.answer()

    try:
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True).first()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = stream.download(output_path=tmpdir, filename="audio.mp4")
            mp3_path = path.replace(".mp4", ".mp3")
            os.rename(path, mp3_path)
            with open(mp3_path, 'rb') as f:
                await callback.message.answer_audio(f, title=yt.title, performer="TinglaHub")
    except Exception as e:
        logging.error(f"Audio error: {e}")
        await callback.message.answer("❌ Audio yuklab bo'lmadi. Boshqa havola sinab ko'ring.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
