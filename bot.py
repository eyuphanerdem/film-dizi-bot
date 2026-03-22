import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TelegramError
import aiohttp
from datetime import datetime
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

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
    rates = {}
    
    try:
        # API 1: Döviz kurları - exchangerate-api.com
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.exchangerate-api.com/v4/latest/USD') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    rates['usd_try'] = data['rates'].get('TRY', 'N/A')
    except Exception as e:
        logger.error(f"API hatası (Döviz): {e}")
    
    try:
        # API 2: Türkiye Merkez Bankası API - Döviz kurları
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.tcmb.gov.tr/kurlar/today.xml') as resp:
                if resp.status == 200:
                    import xml.etree.ElementTree as ET
                    content = await resp.text()
                    root = ET.fromstring(content)
                    
                    for currency in root.findall('.//Currency'):
                        code = currency.get('Kod')
                        unit_elem = currency.find('Unit')
                        selling_elem = currency.find('Selling')
                        
                        if code == 'USD' and selling_elem is not None:
                            rates['usd_try'] = float(selling_elem.text.replace(',', '.'))
                        elif code == 'EUR' and selling_elem is not None:
                            rates['eur_try'] = float(selling_elem.text.replace(',', '.'))
    except Exception as e:
        logger.error(f"TCMB API hatası: {e}")
    
    try:
        # API 3: Kripto - Bitcoin ve Ethereum
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    rates['btc_usd'] = data.get('bitcoin', {}).get('usd', 'N/A')
                    rates['eth_usd'] = data.get('ethereum', {}).get('usd', 'N/A')
                    
                    # USD'den TRY'ye çevirme
                    if 'usd_try' in rates and isinstance(rates['btc_usd'], (int, float)):
                        rates['btc_try'] = rates['btc_usd'] * rates['usd_try']
                    if 'usd_try' in rates and isinstance(rates['eth_usd'], (int, float)):
                        rates['eth_try'] = rates['eth_usd'] * rates['usd_try']
    except Exception as e:
        logger.error(f"Kripto API hatası: {e}")
    
    try:
        # API 4: Emtia - Altın ve Petrol
        async with aiohttp.ClientSession() as session:
            # Metals.live API - Altın (gram, USD)
            async with session.get('https://api.metals.live/v1/spot/gold') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    gold_usd = data.get('gold', 'N/A')
                    rates['gold_usd'] = gold_usd
                    
                    if 'usd_try' in rates and isinstance(gold_usd, (int, float)):
                        rates['gold_try'] = gold_usd * rates['usd_try']
            
            # Petrol API
            async with session.get('https://api.metals.live/v1/spot/oil') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    oil_usd = data.get('oil', 'N/A')
                    rates['oil_usd'] = oil_usd
                    
                    if 'usd_try' in rates and isinstance(oil_usd, (int, float)):
                        rates['oil_try'] = oil_usd * rates['usd_try']
    except Exception as e:
        logger.error(f"Emtia API hatası: {e}")
    
    return rates

def format_message(rates):
    """
    Kur verilerini güzel ve emojili bir mesaja dönüştürür
    """
    usd_try = rates.get('usd_try', 'N/A')
    eur_try = rates.get('eur_try', 'N/A')
    btc_try = rates.get('btc_try', 'N/A')
    gold_try = rates.get('gold_try', 'N/A')
    oil_try = rates.get('oil_try', 'N/A')
    
    # Sayıları güzel formatlama
    def format_price(price):
        if isinstance(price, (int, float)):
            return f"₺{price:,.2f}".replace(',', '.')
        return 'N/A'
    
    message = f"""
╔═══════════════════════════════════╗
║  💰 DÖVIZ & EMTİA KURU SİSTEMİ 💰  ║
║      {datetime.now().strftime('%d.%m.%Y %H:%M')}        ║
╚═══════════════════════════════════╝

📈 DÖVİZ KURLAR (1 Birim = TRY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🇺🇸 Dolar (USD)     → {format_price(usd_try)}
🇪🇺 Euro (EUR)      → {format_price(eur_try)}

💎 EMTİA FIYATLARI (TRY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 Altın (gram)     → {format_price(gold_try)}
⛽ Petrol (varil)   → {format_price(oil_try)}

🪙 KRİPTOPARALAR (TRY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
₿ Bitcoin (1 BTC)   → {format_price(btc_try)}

═════════════════════════════════════
✨ Son Güncelleme: {datetime.now().strftime('%H:%M:%S')} ✨
═════════════════════════════════════
"""
    return message

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start komutu - Bota hoşgeldin mesajı
    """
    welcome_message = """
🤖 Döviz Kuru Botu'na Hoşgeldiniz!

Bu bot her saat başı Döviz, Emtia ve Kripto para kurlarını gösterir.

📋 Komutlar:
/fiyat - Anlık kurları göster
/start - Bu mesajı göster

⏰ Otomatik Güncelleme: Her saat başı
    """
    await update.message.reply_text(welcome_message)

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
    except Exception as e:
        logger.error(f"Komut hatası: {e}")
        await update.message.reply_text("❌ Kurlar alınırken bir hata oluştu. Lütfen daha sonra tekrar deneyin.")

async def send_hourly_message(context: ContextTypes.DEFAULT_TYPE):
    """
    Her saat başı tüm sohbetlere mesaj gönder
    """
    try:
        # Kur verilerini al
        rates = await get_exchange_rates()
        
        # Mesajı formatla
        message = format_message(rates)
        
        # context.job.chat_id'den grup ID'si al ve mesaj gönder
        chat_id = context.job.chat_id
        await context.bot.send_message(chat_id=chat_id, text=message)
        logger.info(f"Saatlik mesaj gönderildi - Chat ID: {chat_id}")
    except TelegramError as e:
        logger.error(f"Telegram mesaj gönderme hatası: {e}")
    except Exception as e:
        logger.error(f"Saatlik mesaj hatası: {e}")

async def post_init(application: Application):
    """
    Bot başladığında scheduler'ı kur
    """
    scheduler = AsyncIOScheduler()
    
    # Her saat başı mesaj gönder
    scheduler.add_job(
        send_hourly_message,
        "cron",
        hour="*",
        minute="0",
        args=[application.context_types.context_class(application)]
    )
    
    scheduler.start()
    logger.info("Scheduler başlatıldı - Her saat başı mesaj gönderilecek")

def main():
    """
    Bot'u başlat
    """
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN çevre değişkeni ayarlanmamış!")
    
    # Application oluştur
    application = Application.builder().token(TOKEN).build()
    
    # Komut handlers ekle
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("fiyat", fiyat_command))
    
    # Post init ekle
    application.post_init = post_init
    
    # Bot'u başlat
    logger.info("Bot başlanıyor...")
    application.run_polling()

if __name__ == '__main__':
    main()
```

**Adım 6:** En altta **"Commit new file"** butonuna tıkla ✅

---

## **DOSYA 2: requirements.txt** 📦

**Adım 1:** Tekrar **"Add file"** → **"Create new file"** tıkla

**Adım 2:** Dosya adını yaz:
```
requirements.txt
```

**Adım 3:** Aşağıdaki kodu KOPYALA VE YAPIŞTUR:
```
python-telegram-bot==21.1
aiohttp==3.9.1
APScheduler==3.10.4
```

**Adım 4:** **"Commit new file"** tıkla ✅

---

## **DOSYA 3: Procfile** 🚀

**Adım 1:** Tekrar **"Add file"** → **"Create new file"** tıkla

**Adım 2:** Dosya adını yaz:
```
Procfile
```

**Adım 3:** Aşağıdaki kodu KOPYALA VE YAPIŞTUR:
```
worker: python bot.py
```

**Adım 4:** **"Commit new file"** tıkla ✅

---

## **DOSYA 4: .gitignore** 🔒

**Adım 1:** Tekrar **"Add file"** → **"Create new file"** tıkla

**Adım 2:** Dosya adını yaz:
```
.gitignore
```

**Adım 3:** Aşağıdaki kodu KOPYALA VE YAPIŞTUR:
```
.env
__pycache__/
*.pyc
*.pyo
venv/
.DS_Store
