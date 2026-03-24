import asyncio
import logging
import os
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web
import yt_dlp

# --- الإعدادات ---
API_TOKEN = '8609584907:AAGrtBOu6anRKW1iSQH3kAJiv4umJUkb1m8'
CHANNEL_ID = '@Ramy_Premium'
CHANNEL_LINK = 'https://t.me/Ramy_Premium'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- دالة التحميل مع اسم ملف فريد لمنع التضارب ---
def download_video(url):
    unique_filename = f"video_{uuid.uuid4().hex}.mp4"
    ydl_opts = {
        'format': 'best',
        'outtmpl': unique_filename,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return unique_filename

def sub_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="انضم لمتجر رامي بريميوم 🛒🔥", url=CHANNEL_LINK)]
    ])

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"أهلاً بك {message.from_user.first_name}! أرسل رابط إنستغرام للتحميل الفوري 📥\nولا تنسَ زيارة متجرنا: @Ramy_Premium", reply_markup=sub_kb())

@dp.message()
async def handle_message(message: types.Message):
    if not message.text or "instagram.com" not in message.text:
        return

    msg = await message.answer("⏳ جاري التحميل من متجر رامي...")
    
    try:
        video_file = await asyncio.to_thread(download_video, message.text)
        caption_text = "✅ تم التحميل بنجاح!\n🛒 @Ramy_Premium"
        
        video = types.FSInputFile(video_file)
        await message.answer_video(video, caption=caption_text, reply_markup=sub_kb())
        
        if os.path.exists(video_file):
            os.remove(video_file)
        await msg.delete()
    except Exception as e:
        logging.error(e)
        await msg.edit_text("❌ عذراً، تأكد من الرابط وحاول مجدداً.")

# --- حل مشكلة Render Timed Out (فتح Port) ---
async def handle(request):
    return web.Response(text="Bot is Live and Stable! ✅")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Web server started on port {port}")

async def main():
    # تشغيل السيرفر الوهمي في الخلفية
    asyncio.create_task(start_web_server())
    # تشغيل البوت
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
