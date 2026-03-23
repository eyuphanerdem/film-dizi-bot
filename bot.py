# -*- coding: utf-8 -*-
import os
import logging
import random
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Verileri harici dosyadan içe aktarıyoruz
try:
    from data import FILMLER, DIZILER
except ImportError:
    # Eğer henüz data.py oluşturulmadıysa hata vermemesi için geçici boş listeler
    FILMLER = []
    DIZILER = []
    print("UYARI: data.py dosyası bulunamadı! Lütfen verileri içeren dosyayı oluşturun.")

# Logging yapılandırması
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_TOKEN')
USER_ID = 8162765467  # Senin User ID'n

def get_random_film():
    """Rastgele film seç"""
    return random.choice(FILMLER) if FILMLER else None

def get_random_dizi():
    """Rastgele dizi seç"""
    return random.choice(DIZILER) if DIZILER else None

def format_movie_message(movie, movie_type="Film"):
    """Film/Dizi mesajını formatla"""
    if not movie:
        return "Üzgünüm, şu an öneri listesi boş."
        
    return f"""
==================================
  GÜNÜN {movie_type.upper()} ÖNERİSİ
  {datetime.now().strftime('%d.%m.%Y %H:%M')}
==================================

🎬 {movie['title']}
📅 Yıl: {movie['year']}
⭐ IMDb: {movie['rating']}/10

📝 Açıklama:
{movie['description']}

==================================
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komutu"""
    await update.message.reply_text(
        "🎬 Film/Dizi Önerisi Botu'na hoş geldiniz!\n\n"
        "/film - Günün film önerisi\n"
        "/dizi - Günün dizi önerisi\n\n"
        "Her 3 saatte bir otomatik öneriler alacaksınız!"
    )
    
    # İlk defa çalıştırıldığında scheduler'ı başlat
    if not context.job_queue.get_jobs_by_name("auto_recommendation"):
        context.job_queue.run_repeating(
            send_scheduled_recommendation,
            interval=3 * 60 * 60,  # 3 saat
            first=0,
            context=USER_ID,
            name="auto_recommendation"
        )
        logger.info("Otomatik öneriler başlatıldı! (3 saatte bir)")

async def film_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Film önerisi"""
    try:
        movie = get_random_film()
        msg = format_movie_message(movie, "Film")
        await update.message.reply_text(msg)
    except Exception as e:
        logger.error(f"Hata: {e}")
        await update.message.reply_text("Film önerisi alınırken hata oluştu!")

async def dizi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dizi önerisi"""
    try:
        show = get_random_dizi()
        msg = format_movie_message(show, "Dizi")
        await update.message.reply_text(msg)
    except Exception as e:
        logger.error(f"Hata: {e}")
        await update.message.reply_text("Dizi önerisi alınırken hata oluştu!")

async def send_scheduled_recommendation(context: ContextTypes.DEFAULT_TYPE):
    """Her 3 saatte bir otomatik öneri gönder"""
    try:
        chat_id = context.job.context
        content_type = random.choice(['film', 'dizi'])
        
        if content_type == 'film':
            content = get_random_film()
            label = "Film"
        else:
            content = get_random_dizi()
            label = "Dizi"
        
        if content:
            msg = format_movie_message(content, label)
            await context.bot.send_message(chat_id=chat_id, text=msg)
            logger.info(f"Otomatik öneri gönderildi! ({content_type})")
    except Exception as e:
        logger.error(f"Scheduled recommendation hatası: {e}")

if __name__ == '__main__':
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN çevre değişkeni ayarlanmamış!")
    
    logger.info("Film/Dizi Botu başlatılıyor...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("film", film_command))
    app.add_handler(CommandHandler("dizi", dizi_command))
    
    app.run_polling()
