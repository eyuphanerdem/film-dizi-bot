# -*- coding: utf-8 -*-
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import random
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_TOKEN')

# Örnek Film ve Dizi Verileri
FILMLER = [
    {
        'title': 'Inception',
        'year': 2010,
        'rating': 8.8,
        'description': 'Bir hırsız, insanların rüyalarına girerek fikirler çalmayı öğrenmiştir.'
    },
    {
        'title': 'The Dark Knight',
        'year': 2008,
        'rating': 9.0,
        'description': 'Batman, Gotham şehrinin en tehlikeli suçlusuna karşı savaşır.'
    },
    {
        'title': 'Forrest Gump',
        'year': 1994,
        'rating': 8.8,
        'description': 'Basit ama iyi niyetli bir adam, 20. yüzyılın önemli tarihsel olaylarına şahitlik eder.'
    },
    {
        'title': 'Pulp Fiction',
        'year': 1994,
        'rating': 8.9,
        'description': 'Tarantino\'nun ikonik filmi: suçlular, kumarbazlar ve bir gangsterin karısı.'
    },
    {
        'title': 'The Shawshank Redemption',
        'year': 1994,
        'rating': 9.3,
        'description': 'Bir adam, cezaevinde yaşadığı yıllarda dostluk ve umut bulur.'
    }
]

DIZILER = [
    {
        'title': 'Breaking Bad',
        'year': 2008,
        'rating': 9.5,
        'description': 'Bir kimya öğretmeni uyuşturucu üretim işine girer.'
    },
    {
        'title': 'Game of Thrones',
        'year': 2011,
        'rating': 9.3,
        'description': 'Düzine krallık, taht için savaşır ve ejderha uyanır.'
    },
    {
        'title': 'Stranger Things',
        'year': 2016,
        'rating': 8.7,
        'description': 'Bir kasabada garip olaylar meydana gelir ve çocuklar adalet araştırır.'
    },
    {
        'title': 'The Office',
        'year': 2005,
        'rating': 9.0,
        'description': 'Bir kağıt şirketinin ofis çalışanlarının komik ve duygusal hikayeleri.'
    },
    {
        'title': 'Sherlock',
        'year': 2010,
        'rating': 9.1,
        'description': 'Modern zamanda efsanevi dedektif Sherlock Holmes\'un macerası.'
    }
]

def get_random_film():
    """Rastgele film seç"""
    return random.choice(FILMLER)

def get_random_dizi():
    """Rastgele dizi seç"""
    return random.choice(DIZILER)

def format_movie_message(movie, movie_type="Film"):
    """Film/Dizi mesajını formatla"""
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

if __name__ == '__main__':
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN çevre değişkeni ayarlanmamış!")
    
    logger.info("Film/Dizi Botu başlanıyor...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("film", film_command))
    app.add_handler(CommandHandler("dizi", dizi_command))
    
    app.run_polling()
