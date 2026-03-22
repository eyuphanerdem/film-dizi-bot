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

async def get_exchange_rates():
    rates = {
        'usd_try': 32.50,  # TEST: Sabit değer
        'eur_try': 35.20,
        'btc_try': 1234567.89,
        'gold_try': 2450.50,
        'oil_try': 89.75
    }
    return rates

def format_message(rates):
    def fmt(price):
        if isinstance(price, (int, float)):
            return f"TRY {price:,.2f}".replace(',', '.')
        return 'N/A'
    
    return f"""
==================================
  DOVIZ VE EMTIA KURU SISTEMI
  {datetime.now().strftime('%d.%m.%Y %H:%M')}
==================================

DOVIZ KURLAR
----------------------------------
USD Dolar    : {fmt(rates.get('usd_try', 'N/A'))}
EUR Euro     : {fmt(rates.get('eur_try', 'N/A'))}

EMTIA
----------------------------------
Altin (gram) : {fmt(rates.get('gold_try', 'N/A'))}
Petrol       : {fmt(rates.get('oil_try', 'N/A'))}

KRIPTO
----------------------------------
Bitcoin      : {fmt(rates.get('btc_try', 'N/A'))}

==================================
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Doviz Botu aktif! /fiyat yazin.")

async def fiyat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        rates = await get_exchange_rates()
        msg = format_message(rates)
        await update.message.reply_text(msg)
    except Exception as e:
        logger.error(f"Hata: {e}")
        await update.message.reply_text("Kurlar alinirken hata!")

if __name__ == '__main__':
    if not TOKEN:
        raise ValueError("TOKEN yok!")
    
    logger.info("Bot basliyor...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("fiyat", fiyat))
    
    app.run_polling()
