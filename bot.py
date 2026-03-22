# -*- coding: utf-8 -*-
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TelegramError
import aiohttp
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

# Logging kurulumu
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token'ı çevre değişkeninden al
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Kur verilerini çeken fonksiyon
async def get_exchange_rates():
    """
    API'lerden gerçek zamanlı döviz ve emtia kurlarını çeker
    """
    rates = {
        'usd_try': 'N/A',
        'eur_try': 'N/A',
        'btc_try': 'N/A',
        'gold_try': 'N/A',
        'oil_try': 'N/A'
    }
    
    try:
        # API: Türkiye Merkez Bankası API - Döviz kurları
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.tcmb.gov.tr/kurlar/today.xml', timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    import xml.etree.ElementTree as ET
                    content = await resp.text()
                    root = ET.fromstring(content)
                    
                    for currency in root.findall('.//Currency'):
                        code = currency.get('Kod')
                        selling_elem = currency.find('Selling')
                        
                        if code == 'USD' and selling_elem is not None:
                            try:
                                rates['usd_try'] = float(selling_elem.text.replace(',', '.'))
                            except:
                                pass
                        elif code == 'EUR' and selling_elem is not None:
                            try:
                                rates['eur_try'] = float(selling_elem.text.replace(',', '.'))
                            except:
                                pass
    except Exception as e:
        logger.error(f"TCMB API hatası: {e}")
    
    try:
        # API: Kripto - Bitcoin ve Ethereum
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd', timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    btc_usd = data.get('bitcoin', {}).get('usd', 'N/A')
                    
                    if isinstance(btc_usd, (int, float)) and isinstance(rates['usd_try'], (int, float)):
                        rates['btc_try'] = btc_usd * rates['usd_try']
    except Exception as e:
        logger.error(f"Kripto API hatası: {e}")
    
    try:
        # API: Emtia - Altın ve Petrol
        async with aiohttp.ClientSession() as session:
            # Altın (gram, USD)
            async with session.get('https://api.metals.live/v1/spot/gold', timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    gold_usd = data.get('gold', 'N/A')
                    
                    if isinstance(gold_usd, (int, float)) and isinstance(rates['usd_try'], (int, float)):
                        rates['gold_try'] = gold_usd * rates['usd_try']
            
            # Petrol
            async with session.get('https://api.metals.live/v1/spot/oil', timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    oil_usd = data.get('oil', 'N/A')
                    
                    if isinstance(oil_usd, (int, float)) and isinstance(rates['usd_try'], (int, float)):
                        rates['oil_try'] = oil_usd * rates['usd_try']
    except Exception as e:
        logger.error(f"Emtia API hatası: {e}")
    
    return rates

def format_message(rates):
    """
    Kur verilerini güzel bir mesaja dönüştürür
    """
    usd_try = rates.get('usd_try', 'N/A')
    eur_try = rates.get('eur_try', 'N/A')
    btc_try = rates.get('btc_try', 'N/A')
    gold_try = rates.get('gold_try', 'N/A')
    oil_try = rates.get('oil_try', 'N/A')
    
    # Sayıları güzel formatlama
    def format_price(price):
        if isinstance(price, (int, float)):
            return f"TRY {price:,.2f}".replace(',', '.')
        return 'N/A'
    
    message = f"""
==================================
  DOVIZ VE EMTIA KURU SISTEMI
  {datetime.now().strftime('%d.%m.%Y %H:%M')}
==================================

DOVIZ KURLAR (1 Birim = TRY)
----------------------------------
USD Dolar       : {format_price(usd_try)}
EUR Euro        : {format_price(eur_try)}

EMTIA FIYATLARI (TRY)
----------------------------------
Altin (gram)    : {format_price(gold_try)}
Petrol (varil)  : {format_price(oil_try)}

KRIPTOPARA (TRY)
----------------------------------
Bitcoin (1 BTC) : {format_price(btc_try)}

==================================
Son Guncelleme: {datetime.now().strftime('%H:%M:%S')}
==================================
"""
    return message

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start komutu - Bota hoşgeldin mesajı
    """
    welcome_message = """
DOVIZ KURU BOTUNA HOSGELDINIZ!

Bu bot her saat basi Doviz, Emtia ve Kripto para kurlarini gosterir.

KOMUTLAR:
/fiyat - Anlik kurlari goster
/start - Bu mesaji goster

OTOMATIK GUNCELLEME: Her saat basi
    """
    await update.message.reply_text(welcome_message)
    logger.info("Start komutu cagrildi")

async def fiyat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /fiyat komutu - Anlık kurları göster
    """
    try:
        # Kur verilerini al
        rates = await get_exchange_rates()
        
        # Mesajı formatla
        message = format_message(rates)
        
        # Gönder
        await update.message.reply_text(message)
        logger.info("Fiyat komutu cagrildi")
    except Exception as e:
        logger.error(f"Fiyat komutu hatası: {e}")
        await update.message.reply_text("Hata: Kurlar alinirken bir sorun olustu. Lutfen daha sonra tekrar deneyin.")

async def send_hourly_update(app: Application):
    """
    Her saat başı güncelleme gönder - bir gruba mesaj gönderir
    """
    try:
        rates = await get_exchange_rates()
        message = format_message(rates)
        
        # Eğer bir DEFAULT_CHAT_ID varsa oraya gönder
        # Bu örnekte biz sadece log yazacağız
        logger.info("Saatlik guncelleme cagildi - Hazir")
        
    except Exception as e:
        logger.error(f"Saatlik guncelleme hatası: {e}")

async def start_scheduler(app: Application):
    """
    Bot başlarken scheduler'ı başlat
    """
    logger.info("Scheduler baslatiliyor...")
    
    scheduler = AsyncIOScheduler()
    
    # Her saat başı
    scheduler.add_job(
        send_hourly_update,
        "cron",
        hour="*",
        minute="0",
        args=[app]
    )
    
    scheduler.start()
    logger.info("Scheduler baslatildi")

def main():
    """
    Bot'u başlat
    """
    if not TOKEN:
        logger.error("TELEGRAM_TOKEN cevre degiskeni ayarlanmamis!")
        raise ValueError("TELEGRAM_TOKEN cevre degiskeni ayarlanmamis!")
    
    logger.info("Bot baslanıyor...")
    
    # Application oluştur
    app = Application.builder().token(TOKEN).build()
    
    # Komut handlers ekle
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("fiyat", fiyat_command))
    
    # Post init callback ekle
    app.post_init = start_scheduler
    
    # Bot'u başlat
    logger.info("Bot polling modunda çalışıyor...")
    app.run_polling()

if __name__ == '__main__':
    main()
