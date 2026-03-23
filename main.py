import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

# --- الإعدادات ---
API_TOKEN = '8609584907:AAGrtBOu6anRKW1iSQH3kAJiv4umJUkb1m8'
CHANNEL_ID = '@Ramy_Premium'
CHANNEL_LINK = 'https://t.me/Ramy_Premium'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def sub_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="اضغط هنا للاشتراك في القناة ✅", url=CHANNEL_LINK)]
    ])

def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"أهلاً بك {message.from_user.first_name}!\nأرسل رابط إنستغرام الآن وسأقوم بتحميله فوراً 🚀", reply_markup=sub_kb())

@dp.message()
async def handle_message(message: types.Message):
    if not message.text or "instagram.com" not in message.text:
        return

    # التحقق من الاشتراك
    try:
        user = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=message.from_user.id)
        if user.status in ['left', 'kicked']:
            return await message.answer("⚠️ يجب الاشتراك في القناة أولاً لاستخدام البوت!", reply_markup=sub_kb())
    except:
        pass

    msg = await message.answer("⏳ جاري التحميل بأقصى سرعة...")
    
    try:
        # تشغيل التحميل في "خيط" منفصل لعدم تعليق البوت
        video_file = await asyncio.to_thread(download_video, message.text)
        
        # إرسال الفيديو
        video = types.FSInputFile(video_file)
        await message.answer_video(video, caption="✅ تم التحميل بواسطة بوت رامي")
        
        # حذف الفيديو من السيرفر بعد الإرسال لتوفير المساحة
        os.remove(video_file)
        await msg.delete()
    except Exception as e:
        logging.error(e)
        await msg.edit_text("❌ عذراً، فشل التحميل. تأكد أن الحساب عام وليس خاصاً.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
