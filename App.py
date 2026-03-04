import os
import yt_dlp
import asyncio
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Token'ı environment variable'dan al (HF Secrets'tan)
TOKEN = os.environ.get("BOT_TOKEN", "")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable tanımlanmamış!")

class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Jarwis Online")
    def log_message(self, format, *args):
        pass  # Log spam'i kapat

def run_port():
    try:
        server = HTTPServer(('0.0.0.0', 7860), HealthCheck)
        server.serve_forever()
    except Exception as e:
        print(f"HTTP server hatası: {e}")

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    await u.message.reply_text(
        "🤖 *Jarwis Çevrimiçi.*\nEfendim, emrinizdeyim.",
        parse_mode="Markdown"
    )

async def handle_msg(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.message.text
    sq = q if q.startswith("http") else f"ytsearch5:{q}"
    s = await u.message.reply_text("🖥️ *Aranıyor...*", parse_mode="Markdown")
    try:
        loop = asyncio.get_event_loop()
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'noplaylist': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(sq, download=False))

        res = info.get('entries', [info])
        await s.delete()

        for e in res[:5]:  # Max 5 sonuç
            vid = e.get('id')
            if not vid:
                continue
            url = f"https://www.youtube.com/watch?v={vid}"
            title = e.get('title', 'Bilinmeyen')
            duration = e.get('duration', 0)
            dur_str = f"{duration//60}:{duration%60:02d}" if duration else "?"
            kb = [[InlineKeyboardButton("📥 İndir (MP3)", callback_data=url)]]
            await u.message.reply_text(
                f"🎧 *{title}*\n⏱ {dur_str}",
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="Markdown"
            )
    except Exception as e:
        await s.edit_text(f"❌ Hata: {str(e)}")

async def btn(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query
    url = q.data
    await q.answer("İndiriliyor, lütfen bekleyin...")
    m = await q.message.reply_text("📥 *İndiriliyor...*", parse_mode="Markdown")
    
    # /tmp kullan — Docker'da yazılabilir alan
    fname = f"/tmp/{int(time.time())}.mp3"
    
    try:
        opts_dl = {
            'format': 'bestaudio/best',
            'outtmpl': fname.replace('.mp3', '.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }
        loop = asyncio.get_event_loop()
        with yt_dlp.YoutubeDL(opts_dl) as ydl:
            await loop.run_in_executor(None, lambda: ydl.download([url]))

        # Dosyayı bul (uzantı değişmiş olabilir)
        actual_file = fname
        if not os.path.exists(actual_file):
            # .mp3 uzantısıyla ara
            base = fname.replace('.mp3', '')
            for ext in ['.mp3', '.m4a', '.webm', '.opus']:
                if os.path.exists(base + ext):
                    actual_file = base + ext
                    break

        if os.path.exists(actual_file):
            with open(actual_file, 'rb') as f:
                await c.bot.send_audio(chat_id=q.message.chat_id, audio=f)
            os.remove(actual_file)
            await m.delete()
        else:
            await m.edit_text("❌ Dosya oluşturulamadı.")

    except Exception as e:
        print(f"İndirme hatası: {e}")
        await m.edit_text(f"❌ İndirme başarısız: {str(e)[:100]}")
        # Temizlik
        for ext in ['.mp3', '.m4a', '.webm', '.opus']:
            f = fname.replace('.mp3', ext)
            if os.path.exists(f):
                os.remove(f)
