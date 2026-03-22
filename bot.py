# -*- coding: utf-8 -*-
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import aiohttp
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_TOKEN')

async def get_exchange_rates():
    """Gerçek API'lerden kur verisi çek"""
    rates = {
        'usd_try': 'N/A',
        'eur_try': 'N/A',
        'btc_try': 'N/A',
        'gold_try': 'N/A',
        'oil_try': 'N/A'
    }
    
    try:
        # ExchangeRate-API - Döviz (USD bazında)
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    usd_try = data.get('rates', {}).get('TRY')
                    eur_usd = data.get('rates', {}).get('EUR')
                    
                    if usd_try:
                        rates['usd_try'] = usd_try
                    if eur_usd and usd_try:
                        rates['eur_try'] = eur_usd * usd_try
    except Exception as e:
        logger.error(f"Döviz API hatası: {e}")
    
    try:
        # CoinGecko - Bitcoin
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd', timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    btc_usd = data.get('bitcoin', {}).get('usd')
                    if isinstance(btc_usd, (int, float)) and isinstance(rates['usd_try'], (int, float)):
                        rates['btc_try'] = btc_usd * rates['usd_try']
    except Exception as e:
        logger.error(f"Bitcoin API hatası: {e}")
    
    try:
        # Metals.live - Altın & Petrol
        async with aiohttp.ClientSession() as session:
            # Altın (USD/oz olarak, grama çevireceğiz: 1 oz = 31.1035 gram)
            async with session.get('https://api.metals.live/v1/spot/gold', timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    gold_oz = data.get('gold')  # USD/oz
                    if isinstance(gold_oz, (int, float)) and isinstance(rates['usd_try'], (int, float)):
                        gold_gram_usd = gold_oz / 31.1035
                        rates['gold_try'] = gold_gram_usd * rates['usd_try']
            
            # Petrol (Brent Crude - USD/barrel)
            async with session.get('https://api.metals.live/v1/spot/oil', timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    oil_usd = data.get('oil')
                    if isinstance(oil_usd, (int, float)) and isinstance(rates['usd_try'], (int, float)):
                        rates['oil_try'] = oil_usd * rates['usd_try']
    except Exception as e:
        logger.error(f"Metals API hatası: {e}")
    
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
