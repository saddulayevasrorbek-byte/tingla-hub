import os
import re
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from pytubefix import YouTube
import instaloader

# BotFather bergan mutlaqo yangi faol token
TOKEN = "8884399790:AAEOH3RNld8yDBh23lV-W8vAFjSHbnkkLX0"

bot = Bot(token=TOKEN)
dp = Dispatcher()
L = instaloader.Instaloader()

YOUTUBE_REGEX = r'(https?://)?(www\.)?(youtube\.com|youtu\.be|youtube-nocookie\.com)/.+'
INSTAGRAM_REGEX = r'(https?://)?(www\.)?(instagram\.com)/(p|reel|tv|shorts)/.+'

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Salom! Menga YouTube yoki Instagram havolasini yuboring, yuklab beraman! 🤖")

@dp.message(F.text)
async def handle_links(message: types.Message):
    url = message.text.strip()
    
    if re.match(YOUTUBE_REGEX, url):
        status = await message.answer("🔄 YouTube yuklanmoqda...")
        try:
            if "shorts/" in url:
                url = url.replace("shorts/", "watch?v=")
            
            yt = YouTube(url)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').get_highest_resolution()
            if not stream:
                stream = yt.streams.filter(file_extension='mp4').get_highest_resolution()
                
            video_path = stream.download(output_path=".")
            video_file = types.FSInputFile(video_path)
            await message.answer_video(video=video_file, caption=f"🎬 {yt.title}")
            
            if os.path.exists(video_path):
                os.remove(video_path)
            await status.delete()
        except Exception as e:
            await status.edit_text(f"❌ YouTube yuklashda xatolik yuz berdi.")
            print(e)

    elif re.match(INSTAGRAM_REGEX, url):
        status = await message.answer("🔄 Instagram yuklanmoqda...")
        try:
            if '?' in url:
                clean_url = url.split('?')[0]
            else:
                clean_url = url
            
            clean_url = clean_url.strip('/')
            shortcode = clean_url.split('/')[-1]
            
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            if post.is_video:
                await message.answer_video(video=post.video_url, caption="📸 Instagram Reels")
            else:
                await message.answer_photo(photo=post.url, caption="📸 Instagram Post")
            await status.delete()
        except Exception as e:
            await status.edit_text("❌ Instagram yuklashda xatolik.")
            print(e)
    else:
        await message.answer("⚠️ Noma'lum havola! Faqat YouTube yoki Instagram havolalarini yuboring.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
