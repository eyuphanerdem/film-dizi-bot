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
USER_ID = 8162765467  # Senin User ID'n

# 25 Film Verileri
FILMLER = [
    {
        'title': 'Inception',
        'year': 2010,
        'rating': 8.8,
        'description': 'Bir hırsız, insanların rüyalarına girerek fikirler çalmayı öğrenmiştir. Christopher Nolan\'un yönettiği bu başyapıt, katmanlı rüyalar ve gerçeklik arasındaki sınırları sorgulamaktadır. Teknik açıdan inanılmaz görsel efektler ve döngüsel zaman kavramıyla izleyenleri şaşırtır.'
    },
    {
        'title': 'The Dark Knight',
        'year': 2008,
        'rating': 9.0,
        'description': 'Batman, Gotham şehrinin en tehlikeli suçlusuna, Joker\'a karşı savaşır. Heath Ledger\'in ikonik performansı ve karanlık tema ile bu film, süper kahraman türünü yeni bir seviyeye taşımıştır. Ahlak, adalet ve kaosin doğası sorgulanır.'
    },
    {
        'title': 'Forrest Gump',
        'year': 1994,
        'rating': 8.8,
        'description': 'Basit ama iyi niyetli bir adam, 20. yüzyılın önemli tarihsel olaylarına şahitlik eder. Tom Hanks\'in usta performansıyla, dostluk, aşk ve yaşamın anlamı hakkında derin bir yolculuk yapılır. Duygusal ve ilham verici.'
    },
    {
        'title': 'Pulp Fiction',
        'year': 1994,
        'rating': 8.9,
        'description': 'Tarantino\'nun ikonik filmi: suçlular, kumarbazlar ve bir gangsterin karısı. Doğrusal olmayan kurgu ve keskin diyaloglarla, pop kültürü ve şiddetin sınırlarını keşfeder. Kültür ikonu haline gelmiştir.'
    },
    {
        'title': 'The Shawshank Redemption',
        'year': 1994,
        'rating': 9.3,
        'description': 'Bir adam, cezaevinde yaşadığı yıllarda dostluk ve umut bulur. Stephen King\'in hikayesinden uyarlanan bu film, özgürlük ve umudun gücünü gösterir. Sinema tarihinin en sevilen filmlerinden biridir.'
    },
    {
        'title': 'Interstellar',
        'year': 2014,
        'rating': 8.6,
        'description': 'Astronotlar, insanlık için yeni bir ev aramak üzere bir siyah delik içinden seyahat eder. Christopher Nolan\'un ambisiyöz başyapıtı, aşk, sacrifi ve evrenin sınırlarını sorgulamaktadır. Müzik ve görsel tasarım muhteşemdir.'
    },
    {
        'title': 'The Matrix',
        'year': 1999,
        'rating': 8.7,
        'description': 'Bir hacker gerçekliğin doğası ve insan özgürlüğü hakkında hakikat öğrenir. Wachowski kardeşlerinin devrim niteliğindeki filmi, bilim kurgu ve felsefenin birleşmesidir. Kültür fenomeni yaratmıştır.'
    },
    {
        'title': 'Gladiator',
        'year': 2000,
        'rating': 8.5,
        'description': 'Bir Roma generali, çiftçi olarak satılmış ve gladyatör olarak yükselmek için savaşır. Russell Crowe\'un güçlü performansı ve epik sahnelerle, iktidar ve intikamın hikayesi anlatılır. Tarih ve dram görkemlidir.'
    },
    {
        'title': 'Parasite',
        'year': 2019,
        'rating': 8.6,
        'description': 'Fakir bir aile, zengin bir ailenin evine infiltre olmaya çalışır. Bong Joon-ho\'nun ustaca yönettiği bu film, sınıf farkı ve toplumsal eşitsizliği alaycı bir şekilde ortaya koyar. Palme d\'Or kazanmıştır.'
    },
    {
        'title': 'The Usual Suspects',
        'year': 1995,
        'rating': 8.6,
        'description': 'Bir polis sorgulamada, beş şüpheli suçlu hakkında çelişkili hikayeler anlatır. Sürprizle dolu son sahne ve Kevin Spacey\'in değişken performansı, suçlu ve koruma hakkında sorular sorar. Thriller şaheseridir.'
    },
    {
        'title': 'Dune',
        'year': 2021,
        'rating': 8.0,
        'description': 'Denis Villeneuve\'in yönettiği bu destansı bilim kurgu filmi, Frank Herbert\'in klasik romanından uyarlanmıştır. Çöl gezegeninde güç, din ve siyasetin iç içe geçtiği bir hikaye anlatılır. Görsel spektakül dudak kapalı.'
    },
    {
        'title': 'Se7en',
        'year': 1995,
        'rating': 8.6,
        'description': 'İki dedektif, yedi ölümcül günahı kullanan bir seri katili arıyor. David Fincher\'in karanlık sinematografisi ve depresif atmosferi, suç ve cezanın doğası üzerine sorular sorar. Sonuşu dehşet vericidir.'
    },
    {
        'title': 'The Godfather',
        'year': 1972,
        'rating': 9.2,
        'description': 'Bir mafya ailesinin iktidara yükselişi ve çöküşü anlatılır. Francis Ford Coppola\'nın başyapıtı, güç, sadakat ve aile hakkında derin bir inceleme sunar. Sinema tarihinin en etkileyici filmidir.'
    },
    {
        'title': 'The Godfather Part II',
        'year': 1974,
        'rating': 9.0,
        'description': 'Godfather\'ın devamında, Vito Corleone\'un geçmişi ve Michael\'ın geleceği paralel olarak anlatılır. Devam filmi orijinalı kadar başarılı olan nadir örneklerden biridir. Yapı ve karakterler mükemmeldir.'
    },
    {
        'title': 'Fight Club',
        'year': 1999,
        'rating': 8.8,
        'description': 'Bir adamın gizli dövüş kulübü ve radikal hareketi hakkında hikaye. David Fincher\'in agresif yönetmeni ve twist sonu, tüketim kültürünü eleştiri altına alır. Psikolojik ve provokatiftir.'
    },
    {
        'title': 'Goodfellas',
        'year': 1990,
        'rating': 8.7,
        'description': 'Bir genç, mafya dünyasına girerek yüksekliğe ulaşır ve düşer. Martin Scorsese\'nin dinamik yönetmeni ve hızlı kurgusu, suç hayatının çekiciliğini ve sonuçlarını gösterir. Enerji patlamasıdır.'
    },
    {
        'title': 'Saving Private Ryan',
        'year': 1998,
        'rating': 8.6,
        'description': 'II. Dünya Savaşı sırasında, bir asker bulma görevinde bir birlim savaşır. Steven Spielberg\'in savaş sahneleri gerçekçi ve şok edicidir. İnsaniliğin savaşta nasıl kaybolduğu gösterilir.'
    },
    {
        'title': 'The Silence of the Lambs',
        'year': 1991,
        'rating': 8.6,
        'description': 'Bir FBI ajanı, seri bir katili yakalamak için zeka oyunu oynayan bir kanibal doktor ile işbirliği yapar. Anthony Hopkins\'in korkunç performansı ve psikolojik gerilim, thriller türünü yeniden tanımlar.'
    },
    {
        'title': 'Schindler\'s List',
        'year': 1993,
        'rating': 9.0,
        'description': 'Holocaustun karanlığında, bir işadamı binlerce Yahudi\'yi kurtarmak için kendi yaşamını riske atar. Steven Spielberg\'in siyah-beyaz sinematografisi, insanın iyiliğinin gücünü gösterir. Tarihi ve duygusal.'
    },
    {
        'title': 'The Shining',
        'year': 1980,
        'rating': 8.4,
        'description': 'Bir aile, kışlık bir otelinde kalmaya gelen ve sinirlenmeye başlayan baba ve oğlunun hikayesi. Stanley Kubrick\'in psikolojik horroru, izolasyon ve madness temaları keşfeder. Atmosfer ürkütücüdür.'
    },
    {
        'title': 'The Green Mile',
        'year': 1999,
        'rating': 8.6,
        'description': 'Ölüm cezası yatırımındaki mahkumlar, mucize yaratacak güçlere sahip bir adamla tanışır. Frank Darabont\'un duygusal dramı, merhamet ve adalet hakkında sorular sorar. Sonuşu yıkıcıdır.'
    },
    {
        'title': 'American Beauty',
        'year': 1999,
        'rating': 8.3,
        'description': 'Kusursuz görünen bir kırsal aile, gizli kütür ve karanlık sırlarla dolup taşır. Sam Mendes\'in keşif filmi, özgürlük ve kimlik arayışını gösterir. Eleştirisi ve estetik dikkat çekicidir.'
    },
    {
        'title': 'The Truman Show',
        'year': 1998,
        'rating': 8.3,
        'description': 'Bir adamın yaşadığı dünya aslında devasa bir TV programıdır ve o bunu keşfetmeye başlar. Peter Weir\'in yaratıcı filmi, gerçeklik ve manipülasyon hakkında sorular sorar. Düşündürücü ve düşmektir.'
    },
    {
        'title': 'Requiem for a Dream',
        'year': 2000,
        'rating': 8.3,
        'description': 'Farklı karakterlerin bağımlılık ve özlem hikayesi paralel olarak anlatılır. Darren Aronofsky\'nin ezici filmi, bozulma ve umut kaybı hakkında derin bir çalışmadır. Müzik ve görsel dehşet vericidir.'
    }
]

# 25 Dizi Verileri
DIZILER = [
    {
        'title': 'Breaking Bad',
        'year': 2008,
        'rating': 9.5,
        'description': 'Bir kimya öğretmeni kanser teşhisinden sonra uyuşturucu üretim işine girer. Vince Gilligan\'ın yönettiği bu dizi, karakterin ahlaki çöküşünü mükemmel şekilde gösterir. Sürü sahneler ve sonda muhteşemdir.'
    },
    {
        'title': 'Game of Thrones',
        'year': 2011,
        'rating': 9.3,
        'description': 'Düzine krallık, taht için savaşır ve ejderha uyanır. George R.R. Martin\'in eserinden uyarlanan bu dizi, politika, aşk ve ölümün iç içe geçtiği epik bir hikaye sunar. Her sezon sürprizlerle dolup taşır.'
    },
    {
        'title': 'Stranger Things',
        'year': 2016,
        'rating': 8.7,
        'description': 'Bir kasabada garip olaylar meydana gelir ve çocuklar adalet için harekete geçer. Duffer Kardeşlerinin 80\'ler nostalji diyarı, korku ve macerası birleştiren dizisi. Karakterler sevimli ve hikaye çekicidir.'
    },
    {
        'title': 'The Office',
        'year': 2005,
        'rating': 9.0,
        'description': 'Bir kağıt şirketinin ofis çalışanlarının komik ve duygusal hikayeleri. Michael Scott\'un liderliğinde, iş yeri dostlukları ve aşkları keşfedilir. Mockumentary stil eşsizdir ve komedi yerini bulur.'
    },
    {
        'title': 'Sherlock',
        'year': 2010,
        'rating': 9.1,
        'description': 'Modern zamanda efsanevi dedektif Sherlock Holmes\'un heyecanlı macerası. Steven Moffat\'ın yorumunda, teknoloji ve dedektif çalışması birleşir. Benedict Cumberbatch\'in performansı mükemmeldir.'
    },
    {
        'title': 'The Crown',
        'year': 2016,
        'rating': 8.6,
        'description': 'İngiltere Kraliçesi Elizabeth II\'nin tahta çıkışından günümüze kadar yaşamı. Peter Morgan\'ın dramatik dizi, güç, görev ve kişisel çöküşün hikayesini anlatır. Prodüksiyon ve oyunculuk övgüye layıktır.'
    },
    {
        'title': 'Westworld',
        'year': 2016,
        'rating': 8.5,
        'description': 'Yapay akıllı robotların olduğu bir tema parkında insanlar ve makineler çatışır. Jonathan Nolan\'ın kompleks dizisi, bilişim ve bilinç hakkında sorular sorar. Hikaye ve sürprizler ilgi tutabilir.'
    },
    {
        'title': 'The Mandalorian',
        'year': 2019,
        'rating': 8.7,
        'description': 'Star Wars evreninde bir ödül avcısı ve bulmaca bir çocuğun macerası. Jon Favreau\'nun dizisi, orijinal film ruhuyla döner. Görsel ve müzik spektakuler, karakter dinamikleri güzeldir.'
    },
    {
        'title': 'Chernobyl',
        'year': 2019,
        'rating': 9.3,
        'description': 'Çernobil nükleer felaketinin gerçek hikayesi ve sonrasındaki heroik mücadele. Craig Mazin\'in dakik mini-dizisi, tarih ve insani çabukluk gösterir. Her bölüm gerçekçi ve etkileyicidir.'
    },
    {
        'title': 'Mindhunter',
        'year': 2017,
        'rating': 8.8,
        'description': 'FBI ajanları, seri katilleri daha iyi anlamak için psikolojik profil oluşturmaya çalışır. David Fincher\'in dizisi, suç psikolojisini derin bir şekilde araştırır. Gerilim ve karakter analizi başarılıdır.'
    },
    {
        'title': 'The Sopranos',
        'year': 1999,
        'rating': 9.2,
        'description': 'Bir mafya şefi, terapiye giderek kişisel sorunlarıyla yüzleşir. David Chase\'in devrim niteliğindeki dizisi, HBO\'nun dönemini başlattı. Karakter gelişimi ve sonuşu sinema tarihine işlenmiştir.'
    },
    {
        'title': 'Mad Men',
        'year': 2007,
        'rating': 8.6,
        'description': '1960\'larda bir reklam ajansında yaşanan hırsızlık, aşk ve kimlik arayışı. Matthew Weiner\'in stilize dizisi, Amerikan rüyası ve kariyer hırslını sorgulamaktadır. Dönemin atmosferi kusursuzca yansıtılır.'
    },
    {
        'title': 'Peaky Blinders',
        'year': 2013,
        'rating': 8.8,
        'description': 'I. Dünya Savaşı sonrası Birmingham\'da bir organize suç ailesinin yükselişi. Steven Knight\'ın dizisi, şiddet ve ambisyon hakkında derin bir çalışmadır. Cillian Murphy\'nin performansı etkileyicidir.'
    },
    {
        'title': 'Ozark',
        'year': 2017,
        'rating': 8.5,
        'description': 'Bir muhasebeci para aklama planını çökmesiyle suç dünyasına girer. Bill Burr\'in dizisi, desperat durumlarda aile dinamikleri gösterir. Gerilim ve etik sorular ana temadır.'
    },
    {
        'title': 'True Detective',
        'year': 2014,
        'rating': 8.9,
        'description': 'Iki dedektif, Louisiana\'da gizemli bir cinayeti çözmek için mücadele eder. Nic Pizzolatto\'ın dizisi, suçuluk ve bilinç hakkında derin sorular sorar. İlk sezon sinema kalitesindedir.'
    },
    {
        'title': 'The Wire',
        'year': 2002,
        'rating': 9.3,
        'description': 'Baltimore şehrinde polis, uyuşturucu tüccarları ve siyasetçilerin kompleks ağı. David Simon\'ın ambisiyöz dizisi, toplumsal yapı ve sistem başarısızlığını ortaya koyar. Her sezon farklı açıdan bakış sunar.'
    },
    {
        'title': 'Succession',
        'year': 2018,
        'rating': 8.9,
        'description': 'Bir medya imparatorluğunun başındaki yaşlı adamın çocukları, mirası kontrol etmek için savaşır. Jesse Armstrong\'ın dizisi, aile ve güç hakkında keskin eleştiri sunar. Diyaloglar ve karakterler iyi yazılmıştır.'
    },
    {
        'title': 'Hannibal',
        'year': 2013,
        'rating': 8.5,
        'description': 'Bir FBI profilist, seri bir katili yakalamak için korkunç bir doktor ile işbirliği yapar. Bryan Fuller\'ın görsel olarak şık dizisi, psikoloji ve sanat hakkında sorular sorar. Estetik ve karanlıkdır.'
    },
    {
        'title': 'Dexter',
        'year': 2006,
        'rating': 8.6,
        'description': 'Bir seri katili olmayan polis, kendi cinayetlerini gizlerken başka katilatı avlar. Michael C. Hall\'un performansı etkileyicidir. İlk sezonlar mükemmel, sonrası dalgalanır.'
    },
    {
        'title': 'The Marvelous Mrs. Maisel',
        'year': 2017,
        'rating': 8.7,
        'description': '1950\'lerde New York\'ta bir ev hanımı, stand-up komedyacı olmak için hayatını değiştirir. Amy Sherman-Palladino\'ın dizisi, komediye ve feminist temaları birleştirir. Diyaloglar enerji ve nektardır.'
    },
    {
        'title': 'The Handmaid\'s Tale',
        'year': 2017,
        'rating': 8.4,
        'description': 'Distopik bir gelecekte, kadınlar üreme makineleri olarak köle yapılır. Bruce Miller\'ın dizisi, totalitarizm ve direniş hakkında dehşet verici hikaye sunar. Görsel ve tema baskıcıdır.'
    },
    {
        'title': 'Fleabag',
        'year': 2016,
        'rating': 8.7,
        'description': 'Tek bir "Fleabag", aile düşüşünü ve çocuksulluğu navigasyon yaparken kamerada doğrudan konuşur. Phoebe Waller-Bridge\'in yaratıcı dizisi, komedi ve dram kusursuz şekilde birleşir. Karakterin iç diyaloğu entrümanı.'
    },
    {
        'title': 'Atlanta',
        'year': 2016,
        'rating': 8.9,
        'description': 'Atlanta\'da bir müzik menajeri, rapçi arkadaşlarını başarıya taşımaya çalışır. Donald Glover\'ın dizisi, ırk, kültür ve hip-hop sahnesini sorgulamaktadır. Her bölüm ayrı bir sanat eseridir.'
    },
    {
        'title': 'Veep',
        'year': 2012,
        'rating': 8.8,
        'description': 'Bir ABD başkan yardımcısı ve ekibi, siyasal çatışma ve korkak oyunlarıyla uğraşır. Armando Iannucci\'nin komedyası, siyasa ve bürokrasi hakkında keskin eleştiridir. Küfürlü ve hiledir.'
    },
    {
        'title': 'Silicon Valley',
        'year': 2014,
        'rating': 8.5,
        'description': 'Startup işi ve Silikon Vadisi kompanzasyon, teknik ve iş dünyasının absurdites\'leri. Mike Judge\'in dizisi, teknoloji endüstrisini satire eder. Karakter ve durumlar komik ve tanınabilirdir.'
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
    
    # İlk defa çalıştırıldığında scheduler'ı başlat
    if context.job_queue.jobs() == []:
        context.job_queue.run_repeating(
            send_scheduled_recommendation,
            interval=3 * 60 * 60,  # 3 saat = 3 * 60 * 60 saniye
            first=0,
            context=USER_ID
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
        
        # Rastgele film veya dizi seç
        content_type = random.choice(['film', 'dizi'])
        
        if content_type == 'film':
            movie = get_random_film()
            msg = format_movie_message(movie, "Film")
        else:
            show = get_random_dizi()
            msg = format_movie_message(show, "Dizi")
        
        await context.bot.send_message(chat_id=chat_id, text=msg)
        logger.info(f"Otomatik öneri gönderildi! ({content_type})")
    except Exception as e:
        logger.error(f"Scheduled recommendation hatası: {e}")

if __name__ == '__main__':
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN çevre değişkeni ayarlanmamış!")
    
    logger.info("Film/Dizi Botu başlanıyor...")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("film", film_command))
    app.add_handler(CommandHandler("dizi", dizi_command))
    
    app.run_polling()
