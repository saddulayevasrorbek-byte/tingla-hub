import os
import re
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from pytubefix import YouTube
import instaloader

# Telegram Bot Token
TOKEN = "7787334539:AAGR8YI-K9yYnQPlfQ2_h-68fFidN_E99mI"

bot = Bot(token=TOKEN)
dp = Dispatcher()
L = instaloader.Instaloader()

# Havolalarni tekshirish uchun Regex andozalari
YOUTUBE_REGEX = r'(https?://)?(www\.)?(youtube\.com|youtu\.be|youtube-nocookie\.com)/.+'
INSTAGRAM_REGEX = r'(https?://)?(www\.)?(instagram\.com)/(p|reel|tv|shorts)/.+'

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Salom! Menga YouTube (oddiy video yoki Shorts) yoki Instagram (Reels/Post) havolasini yuboring, men uni yuklab beraman! 🤖")

@dp.message(F.text)
async def handle_links(message: types.Message):
    url = message.text.strip()
    
    # 1. YOUTUBE HAVOLASI BO'LSA
    if re.match(YOUTUBE_REGEX, url):
        status = await message.answer("🔄 YouTube videosi yuklab olinmoqda, kuting...")
        try:
            if "shorts/" in url:
                url = url.replace("shorts/", "watch?v=")
            
            yt = YouTube(url)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').get_highest_resolution()
            
            if not stream:
                stream = yt.streams.filter(file_extension='mp4').get_highest_resolution()
                
            video_path = stream.download(output_path=".")
            
            await status.edit_text("📤 Video Telegram serveriga yuklanmoqda...")
            video_file = types.FSInputFile(video_path)
            await message.answer_video(video=video_file, caption=f"🎬 {yt.title}\n\n@TinglaHubbot orqali yuklandi")
            
            if os.path.exists(video_path):
                os.remove(video_path)
            await status.delete()
            
        except Exception as e:
            await status.edit_text(f"❌ YouTube yuklashda xatolik yuz berdi.")
            print(f"YouTube Error: {e}")

    # 2. INSTAGRAM HAVOLASI BO'LSA
    elif re.match(INSTAGRAM_REGEX, url):
        status = await message.answer("🔄 Instagram posti yuklab olinmoqda, kuting...")
        try:
            # Havolani to'g'ri tozalash va shortcode olish
            clean_url = url.split('?')[0].strip('/')
            parts = clean_url.split('/')
            shortcode = parts[-1]
            
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            if post.is_video:
                video_url = post.video_url
                await status.edit_text("📤 Video Telegramga yuborilmoqda...")
                await message.answer_video(video=video_url, caption=f"📸 Instagram Reels\n\n@TinglaHubbot orqali yuklandi")
            else:
                image_url = post.url
                await status.edit_text("📤 Rasm Telegramga yuborilmoqda...")
                await message.answer_photo(photo=image_url, caption=f"📸 Instagram Post\n\n@TinglaHubbot orqali yuklandi")
                
            await status.delete()
            
        except Exception as e:
            await status.edit_text("❌ Instagram yuklashda xatolik: Profil yopiq yoki havola noto'g'ri.")
            print(f"Instagram Error: {e}")
            
    else:
        await message.answer("⚠️ Noma'lum havola! Iltimos, faqat YouTube yoki Instagram havolalarini yuboring.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
