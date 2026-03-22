# -*- coding: utf-8 -*-
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import aiohttp
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_TOKEN')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

async def get_news():
    """NewsAPI'den son haberleri çek"""
    try:
        async with aiohttp.ClientSession() as session:
            url = f'https://newsapi.org/v2/top-headlines?country=tr&language=tr&sortBy=publishedAt&apiKey={NEWS_API_KEY}'
            logger.info(f"API URL: {url}")
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                logger.info(f"API Status: {resp.status}")
                data = await resp.json()
                logger.info(f"API Response: {data}")
                if resp.status == 200:
                    articles = data.get('articles', [])[:5]  # Son 5 haber
                    return articles
    except Exception as e:
        logger.error(f"News API hatası: {e}")
    
    return []

def format_news_message(articles):
    """Haberleri güzel formatta göster"""
    if not articles:
        return "Haber bulunamadı. Daha sonra tekrar deneyin."
    
    message = f"""
==================================
  SON HABERLER
  {datetime.now().strftime('%d.%m.%Y %H:%M')}
==================================

"""
    
    for i, article in enumerate(articles, 1):
        title = article.get('title', 'Başlık yok')
        url = article.get('url', '')
        source = article.get('source', {}).get('name', 'Kaynak bilinmiyor')
        
        message += f"{i}. {title}\n"
        message += f"   Kaynak: {source}\n"
        message += f"   Link: {url}\n\n"
    
    message += "==================================\n"
    return message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komutu"""
    await update.message.reply_text("Haber Botu aktif! /haberler yazarak son haberleri görebilirsiniz.")

async def haberler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Haberleri göster"""
    try:
        articles = await get_news()
        msg = format_news_message(articles)
        await update.message.reply_text(msg)
    except Exception as e:
        logger.error(f"Hata: {e}")
        await update.message.reply_text("Haberler alınırken hata oluştu!")

if __name__ == '__main__':
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN çevre değişkeni ayarlanmamış!")
    
    if not NEWS_API_KEY:
        raise ValueError("NEWS_API_KEY çevre değişkeni ayarlanmamış!")
    
    logger.info("Haber Botu başlanıyor...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("haberler", haberler))
    
    app.run_polling()
