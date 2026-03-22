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
    """Gerçek API'lerden kur verisi çek"""
    rates = {
        'usd_try': 'N/A',
        'eur_try': 'N/A',
        'btc_try': 'N/A',
        'gold_try': 'N/A',
        'oil_try': 'N/A'
    }
    
    try:
        # TCMB API - Döviz Kurları
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.tcmb.gov.tr/kurlar/today.xml', timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    import xml.etree.ElementTree as ET
                    content = await resp.text()
                    root = ET.fromstring(content)
                    
                    for currency in root.findall('.//Currency'):
                        code = currency.get('Kod')
                        selling = currency.find('Selling')
                        if code == 'USD' and selling is not None:
                            rates['usd_try'] = float(selling.text.replace(',', '.'))
                        elif code == 'EUR' and selling is not None:
                            rates['eur_try'] = float(selling.text.replace(',', '.'))
    except Exception as e:
        logger.error(f"TCMB API hatası: {e}")
    
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
            async with session.get('https://api.metals.live/v1/spot/gold', timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    gold_usd = data.get('gold')
                    if isinstance(gold_usd, (int, float)) and isinstance(rates['usd_try'], (int, float)):
                        rates['gold_try'] = gold_usd * rates['usd_try']
            
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
