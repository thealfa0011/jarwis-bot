import os, yt_dlp, asyncio, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# TOKEN (BotFather'dan aldığın kod)
TOKEN = "8645918798:AAGvYdTUH4giglOJQ4BD22C4wu3p-t9PoGg"

# Render'ın botu canlı görmesi için gerekli port ayarı
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Jarwis Online")

def run_port():
    # Render 10000 portunu kontrol eder, bu kısmı değiştirme
    server = HTTPServer(('0.0.0.0', 10000), HealthCheck)
    server.serve_forever()

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await u.message.reply_text("🤖 *Jarwis Çevrimiçi.*\nEfendim, emrinizdeyim.", parse_mode="Markdown")

async def handle_msg(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.message.text
    sq = q if q.startswith("http") else f"ytsearch5:{q}"
    s = await u.message.reply_text("🖥️ *Aranıyor...*")
    opts = {'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True}
    try:
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(sq, download=False))
        res = info['entries'] if 'entries' in info else [info]
        await s.delete()
        for e in res:
            vid = e.get('id')
            url = f"https://www.youtube.com/watch?v={vid}"
            kb = [[InlineKeyboardButton("📥 İndir", callback_data=url)]]
            await u.message.reply_text(f"🎧 *{e.get('title')}*", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
    except:
        await s.edit_text("❌ Hata oluştu efendim.")

async def btn(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query
    url = q.data
    await q.answer()
    m = await q.message.reply_text("📥 *İndiriliyor...*")
    try:
        opts_dl = {'format': 'bestaudio/best', 'outtmpl': '%(title)s.%(ext)s'}
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(opts_dl) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            fname = ydl.prepare_filename(info)
        await c.bot.send_audio(chat_id=q.message.chat_id, audio=open(fname, 'rb'))
        os.remove(fname)
        await m.delete()
    except:
        await q.message.reply_text("❌ Başarısız.")

if __name__ == '__main__':
    # Web sunucusunu ayrı bir kolda başlatıyoruz
    threading.Thread(target=run_port, daemon=True).start()
    # Botu başlatıyoruz
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    app.add_handler(CallbackQueryHandler(btn))
    print("Jarwis başlatılıyor...")
    app.run_polling()
