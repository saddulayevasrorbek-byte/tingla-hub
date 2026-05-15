import logging
import os
import asyncio
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile

BOT_TOKEN = "8884399790:AAFOh8KumpO4yXXx-QkZBxaclkelIPuZpiI"
COOKIES_FILE = "/app/cookies.txt"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Salom! 🎵\n"
        "YouTube yoki Instagram linkini yuboring — video/audio yuklab beraman!\n\n"
        "Misol: https://www.youtube.com/watch?v=..."
    )

@dp.message()
async def handle_link(message: types.Message):
    url = message.text.strip()

    if not ("youtube.com" in url or "youtu.be" in url or "instagram.com" in url):
        await message.answer("❌ Faqat YouTube yoki Instagram link yuboring!")
        return

    msg = await message.answer("⏳ Yuklanmoqda...")

    try:
        output_path = f"/tmp/{message.from_user.id}_%(title)s.%(ext)s"

        cmd = [
            "yt-dlp",
            "--cookies", COOKIES_FILE,
            "--no-playlist",
            "-f", "best[filesize<50M]/best",
            "--max-filesize", "50m",
            "-o", output_path,
            "--print", "after_move:filepath",
            url
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            cmd_audio = [
                "yt-dlp",
                "--cookies", COOKIES_FILE,
                "--no-playlist",
                "-f", "bestaudio",
                "--extract-audio",
                "--audio-format", "mp3",
                "--max-filesize", "50m",
                "-o", output_path,
                "--print", "after_move:filepath",
                url
            ]
            result = subprocess.run(cmd_audio, capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            filepath = result.stdout.strip().split('\n')[-1]

            if os.path.exists(filepath):
                await msg.edit_text("📤 Yuborilmoqda...")

                if filepath.endswith('.mp3'):
                    await message.answer_audio(FSInputFile(filepath))
                else:
                    await message.answer_video(FSInputFile(filepath))

                os.remove(filepath)
                await msg.delete()
            else:
                await msg.edit_text("❌ Fayl topilmadi. Qayta urining!")
        else:
            error = result.stderr[-500:] if result.stderr else "Noma'lum xatolik"
            logging.error(f"yt-dlp error: {error}")
            await msg.edit_text("❌ Yuklab bo'lmadi! Video himoyalangan bo'lishi mumkin.")

    except subprocess.TimeoutExpired:
        await msg.edit_text("❌ Vaqt tugadi! Video juda katta bo'lishi mumkin.")
    except Exception as e:
        logging.error(f"Error: {e}")
        await msg.edit_text(f"❌ Xatolik: {str(e)[:200]}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
