import datetime
import logging
import aiohttp


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv


load_dotenv()


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


TELEGRAM_TOKEN = '7955745574:AAE4r3CJ7cjA87xWytXOESINi4I6kgIRKd8'
MUSEUM_API_URL = "https://www.tretyakovgallery.ru/api/content/events/"
MUSEUM_URL = "https://www.tretyakovgallery.ru"
MUSEUM_API_URL_EX = 'https://www.tretyakovgallery.ru/api/content/exhibitions'


alt_counter_allv = 0
alt_counter_postoyan = 0
alt_counter_vnesh = 0
alt_counter_bud = 0
count = 0
comunnist_counter = 0


# ========== API ФУНКЦИИ ==========

async def get_events(page_size: int = 5):
    """Асинхронное получение событий из API"""
    try:
        params = {
            'order': 'startDate',
            'hashtagId': '0',
            'page': '1',
            'section': 'tekushchie-vystavki',
            'page_size': str(page_size),
            'archive': 'n',
            'lang': 'ru'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(MUSEUM_API_URL, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API error: {response.status}")
                    return None

    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        return None


async def get_all_events():
    """Получение всех событий"""
    try:
        params = {
            'hashtagId': '0',
            'page_size': '500',
            'archive': 'n',
            'main': 'Y',
            'sort': 'timeStart',
            'sort_param': 'asc',
            'lang': 'ru'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(MUSEUM_API_URL, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API error: {response.status}")
                    return None

    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        return None


async def get_vnesh_events(page_size: int = 5):
    """Получение внешних событий"""
    try:
        params = {
            'order': 'startDate',
            'hashtagId': '0',
            'section': 'vneshnie-vystavki',
            'page_size': str(page_size),
            'archive': 'n',
            'lang': 'ru'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(MUSEUM_API_URL_EX, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API error: {response.status}")
                    return None

    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        return None

async def get_bud_events(page_size: int = 5):
    """Получение будущих событий"""
    try:
        params = {
            'order': 'startDate',
            'hashtagId': '0',
            'section': 'budushchie-vystavki',
            'page_size': str(page_size),
            'archive': 'n',
            'lang': 'ru'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(MUSEUM_API_URL_EX, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API error: {response.status}")
                    return None


    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        return None



async def get_postoyan_events(page_size: int = 5):
    """Получение всех ПОСТОЯННЫХ событий"""
    try:
        params = {
            'section':'postoyannye-ekspozitsii',
            #'hashtagId': '0',
            'page_size': str(page_size),
            'archive': 'n',
            #'main': 'Y',
            'sort': 'timeStart',
            'sort_param': 'asc',
            'lang': 'ru'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(MUSEUM_API_URL, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API error: {response.status}")
                    return None

    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        return None

# ========== КОМАНДЫ ==========

async def events_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать ближайшие события (команда /events)"""
    chat_id = update.effective_chat.id
    events_data = await get_events(10)

    if not events_data or 'data' not in events_data or 'items' not in events_data['data']:
        await update.message.reply_text("На данный момент событий нет.")
        return

    items = events_data['data']['items'][:10]  # Берем первые 5

    for i, event in enumerate(items, 1):
        try:
            title = event.get('name', 'Без названия')
            museum = event.get('place', {}).get('name', 'Не указано')

            start_date_unix = event.get('startDateUnix')
            end_date_unix = event.get('endDateUnix')

            start_date = datetime.datetime.fromtimestamp(start_date_unix).strftime('%d.%m.%Y') if start_date_unix else 'Не указано'
            end_date = datetime.datetime.fromtimestamp(end_date_unix).strftime('%d.%m.%Y') if end_date_unix else 'Не указано'

            temp_url = event.get('url', '')
            url = f"{MUSEUM_URL}{temp_url}" if temp_url else MUSEUM_URL

            message = (
                f"{i}. **{title}**\n"
                f"🏛 {museum}\n"
                f"📅 Проходит с {start_date}\n"
                f"по {end_date}\n"
                f"🔗 [Подробнее]({url})\n"
            )

            await update.message.reply_text(message, parse_mode='Markdown')


        except Exception as e:
            logger.error(f"Error processing event {i}: {e}")
            continue

    await context.bot.send_message(
        chat_id,
        text="Чтобы посмотреть меню нажмите /start"
    )


#===============Получение списка всех выставок==============
async def allv_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Все события (команда /allv)"""
    global alt_counter_allv
    if alt_counter_allv > 0:
        alt_counter_allv = 0

    events_data = await get_events(5)

    if not events_data or 'data' not in events_data or 'items' not in events_data['data']:
        await update.message.reply_text("На данный момент событий нет.")
        return

    items = events_data['data']['items'][:5]

    for i, event in enumerate(items, 1):
        try:
            title = event.get('name', 'Без названия')
            museum = event.get('place', {}).get('name', 'Не указано')

            start_date_unix = event.get('startDateUnix')
            end_date_unix = event.get('endDateUnix')

            start_date = datetime.datetime.fromtimestamp(start_date_unix).strftime('%d.%m.%Y') if start_date_unix else 'Не указано'
            end_date = datetime.datetime.fromtimestamp(end_date_unix).strftime('%d.%m.%Y') if end_date_unix else 'Не указано'

            hashtag = event.get('hashtag', 'Не указано')

            temp_url = event.get('url', '')
            url = f"{MUSEUM_URL}{temp_url}" if temp_url else MUSEUM_URL

            message = (
                f"{i}. **{title}**\n"
                f"🏛 {museum}\n"
                f"📅 Проходит с {start_date}\n"
                f"по {end_date}\n"
                f"тип события: {hashtag}\n"
                f"🔗 [Подробнее]({url})\n"
            )

            await update.message.reply_text(message, parse_mode='Markdown')
            alt_counter_allv += 1

        except Exception as e:
            logger.error(f"Error processing event {i}: {e}")
            continue

    await update.message.reply_text("Увидеть больше /more")


async def more_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать еще события (команда /more)"""
    global alt_counter_allv, count

    events_data = await get_all_events()

    if not events_data or 'data' not in events_data or 'items' not in events_data['data']:
        await update.message.reply_text("Больше событий нет.")
        return

    items = events_data['data']['items']

    start_index = alt_counter_allv
    end_index = min(start_index + 5, len(items))

    if start_index >= len(items):
        await update.message.reply_text("Вы просмотрели все события! \n Для просмотра меню нажмите /start")
        return

    for i in range(start_index, end_index):
        try:
            event = items[i]
            title = event.get('name', 'Без названия')
            museum = event.get('place', {}).get('name', 'Не указано')

            start_date_unix = event.get('startDateUnix')
            end_date_unix = event.get('endDateUnix')

            start_date = datetime.datetime.fromtimestamp(start_date_unix).strftime('%d.%m.%Y') if start_date_unix else 'Не указано'
            end_date = datetime.datetime.fromtimestamp(end_date_unix).strftime('%d.%m.%Y') if end_date_unix else 'Не указано'

            hashtag = event.get('hashtag', 'Не указано')

            temp_url = event.get('url', '')
            url = f"{MUSEUM_URL}{temp_url}" if temp_url else MUSEUM_URL

            message = (
                f"{i + 1}. **{title}**\n"
                f"🏛 {museum}\n"
                f"📅 Проходит с {start_date}\n"
                f"по {end_date}\n"
                f"тип события: {hashtag}\n"
                f"🔗 [Подробнее]({url})\n"
            )

            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error processing event {i + 1}: {e}")
            continue

    alt_counter_allv = end_index
    count += 5

    if alt_counter_allv < len(items):
        await update.message.reply_text("Увидеть больше /more")
    else:
        await update.message.reply_text("Вы просмотрели все события!  \n Для просмотра меню нажмите /start")


#===========ПОЛУЧЕНИЕ СПИСКА ВНЕШНИХ ВЫСТАВОК============


async def vnesh_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Внешние выставки (команда /vnesh)"""
    global alt_counter_vnesh
    if alt_counter_vnesh > 0:
        alt_counter_vnesh = 0

    events_data = await get_vnesh_events(5)

    if not events_data or 'data' not in events_data or 'items' not in events_data['data']:
        await update.message.reply_text("На данный момент событий нет.")
        return

    items = events_data['data']['items'][:5]

    for i, event in enumerate(items, 1):
        try:
            title = event.get('name', 'Без названия')
            museum = event.get('place', {}).get('name', 'Не указано')

            start_date_unix = event.get('startDateUnix')
            end_date_unix = event.get('endDateUnix')

            start_date = datetime.datetime.fromtimestamp(start_date_unix).strftime('%d.%m.%Y') if start_date_unix else 'Не указано'
            end_date = datetime.datetime.fromtimestamp(end_date_unix).strftime('%d.%m.%Y') if end_date_unix else 'Не указано'

            temp_url = event.get('url', '')
            url = f"{MUSEUM_URL}{temp_url}" if temp_url else MUSEUM_URL

            message = (
                f"{i}. **{title}**\n"
                f"🏛 {museum}\n"
                f"📅 Проходит с {start_date}\n"
                f"по {end_date}\n"
                f"🔗 [Подробнее]({url})\n"
            )

            await update.message.reply_text(message, parse_mode='Markdown')
            alt_counter_vnesh += 1

        except Exception as e:
            logger.error(f"Error processing event {i}: {e}")
            continue

    await update.message.reply_text("Увидеть больше /more")

async def more_vnesh_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать еще события (команда /more_vnesh)"""
    global alt_counter_vnesh, count

    events_data = await get_vnesh_events()

    if not events_data or 'data' not in events_data or 'items' not in events_data['data']:
        await update.message.reply_text("Больше событий нет.")
        return

    items = events_data['data']['items']

    # Показываем по 5 событий за раз
    start_index = alt_counter_vnesh
    end_index = min(start_index + 5, len(items))

    if start_index >= len(items):
        await update.message.reply_text("Вы просмотрели все события!  \n Для просмотра меню нажмите /start")
        return

    for i in range(start_index, end_index):
        try:
            event = items[i]
            title = event.get('name', 'Без названия')
            museum = event.get('place', {}).get('name', 'Не указано')

            start_date_unix = event.get('startDateUnix')
            end_date_unix = event.get('endDateUnix')

            start_date = datetime.datetime.fromtimestamp(start_date_unix).strftime('%d.%m.%Y') if start_date_unix else 'Не указано'
            end_date = datetime.datetime.fromtimestamp(end_date_unix).strftime('%d.%m.%Y') if end_date_unix else 'Не указано'

            temp_url = event.get('url', '')
            url = f"{MUSEUM_URL}{temp_url}" if temp_url else MUSEUM_URL

            message = (
                f"{i + 1}. **{title}**\n"
                f"🏛 {museum}\n"
                f"📅 Проходит с {start_date}\n"
                f"по {end_date}\n"
                f"🔗 [Подробнее]({url})\n"
            )

            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error processing event {i + 1}: {e}")
            continue

    alt_counter_vnesh = end_index
    count += 5

    if alt_counter_vnesh < len(items):
        await update.message.reply_text("Увидеть больше /more_vnesh")
    else:
        await update.message.reply_text("Вы просмотрели все события!  \n Для просмотра меню нажмите /start")





#===========ПОЛУЧЕНИЕ СПИСКА БУДУЩИХ ВЫСТАВОК============

async def bud_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Внешние выставки (команда /vnesh)"""
    global alt_counter_bud
    if alt_counter_bud > 0:
        alt_counter_bud = 0

    events_data = await get_bud_events(5)

    if not events_data or 'data' not in events_data or 'items' not in events_data['data']:
        await update.message.reply_text("На данный момент событий нет.")
        return

    items = events_data['data']['items'][:5]

    for i, event in enumerate(items, 1):
        try:
            title = event.get('name', 'Без названия')
            museum = event.get('place', {}).get('name', 'Не указано')

            start_date_unix = event.get('startDateUnix')
            end_date_unix = event.get('endDateUnix')

            start_date = datetime.datetime.fromtimestamp(start_date_unix).strftime('%d.%m.%Y') if start_date_unix else 'Не указано'
            end_date = datetime.datetime.fromtimestamp(end_date_unix).strftime('%d.%m.%Y') if end_date_unix else 'Не указано'

            temp_url = event.get('url', '')
            url = f"{MUSEUM_URL}{temp_url}" if temp_url else MUSEUM_URL

            message = (
                f"{i}. **{title}**\n"
                f"🏛 {museum}\n"
                f"📅 Проходит с {start_date}\n"
                f"по {end_date}\n"
                f"🔗 [Подробнее]({url})\n"
            )

            await update.message.reply_text(message, parse_mode='Markdown')
            alt_counter_bud += 1

        except Exception as e:
            logger.error(f"Error processing event {i}: {e}")
            continue

    await update.message.reply_text("Увидеть больше /more_bud")


async def more_bud_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать еще события (команда /more_bud)"""
    global alt_counter_bud, count

    events_data = await get_bud_events()

    if not events_data or 'data' not in events_data or 'items' not in events_data['data']:
        await update.message.reply_text("Больше событий нет.")
        return

    items = events_data['data']['items']

    start_index = alt_counter_bud
    end_index = min(start_index + 5, len(items))

    if start_index >= len(items):
        await update.message.reply_text("Вы просмотрели все события!  \n Для просмотра меню нажмите /start")
        return

    for i in range(start_index, end_index):
        try:
            event = items[i]
            title = event.get('name', 'Без названия')
            museum = event.get('place', {}).get('name', 'Не указано')

            start_date_unix = event.get('startDateUnix')
            end_date_unix = event.get('endDateUnix')

            start_date = datetime.datetime.fromtimestamp(start_date_unix).strftime('%d.%m.%Y') if start_date_unix else 'Не указано'
            end_date = datetime.datetime.fromtimestamp(end_date_unix).strftime('%d.%m.%Y') if end_date_unix else 'Не указано'

            temp_url = event.get('url', '')
            url = f"{MUSEUM_URL}{temp_url}" if temp_url else MUSEUM_URL

            message = (
                f"{i + 1}. **{title}**\n"
                f"🏛 {museum}\n"
                f"📅 Проходит с {start_date}\n"
                f"по {end_date}\n"
                f"🔗 [Подробнее]({url})\n"
            )

            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error processing event {i + 1}: {e}")
            continue

    alt_counter_bud = end_index
    count += 5

    if alt_counter_vnesh < len(items):
        await update.message.reply_text("Увидеть больше /more_bud")
    else:
        await update.message.reply_text("Вы просмотрели все события!  \n Для просмотра меню нажмите /start")

#============Получение списка постоянных экспозиций и больше========
async def postoyan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Все постоянные события (команда /postoyan)"""
    global alt_counter_postoyan
    if alt_counter_postoyan > 0:
        alt_counter_postoyan = 0

    events_data = await get_postoyan_events(5)

    if not events_data or 'data' not in events_data or 'items' not in events_data['data']:
        await update.message.reply_text("На данный момент событий нет.")
        return

    items = events_data['data']['items'][:5]

    for i, event in enumerate(items, 1):
        try:
            title = event.get('name', 'Без названия')
            museum = event.get('place', {}).get('name', 'Не указано')

            start_date_unix = event.get('startDateUnix')
            end_date_unix = event.get('endDateUnix')

            start_date = datetime.datetime.fromtimestamp(start_date_unix).strftime('%d.%m.%Y') if start_date_unix else 'Не указано'
            end_date = datetime.datetime.fromtimestamp(end_date_unix).strftime('%d.%m.%Y') if end_date_unix else 'Не указано'


            temp_url = event.get('url', '')
            url = f"{MUSEUM_URL}{temp_url}" if temp_url else MUSEUM_URL

            message = (
                f"{i}. **{title}**\n"
                f"🏛 {museum}\n"
                f"📅 Проходит с {start_date}\n"
                f"по {end_date}\n"
                #f"тип события: {hashtag}\n"
                f"🔗 [Подробнее]({url})\n"
            )

            await update.message.reply_text(message, parse_mode='Markdown')
            alt_counter_postoyan += 1

        except Exception as e:
            logger.error(f"Error processing event {i}: {e}")
            continue

    await update.message.reply_text("Увидеть больше /more_postoyan")


async def more_postoyan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать еще постоянные события (команда /more_postoyan)"""
    global alt_counter_postoyan, count

    events_data = await get_postoyan_events()

    if not events_data or 'data' not in events_data or 'items' not in events_data['data']:
        await update.message.reply_text("Больше событий нет.")
        return

    items = events_data['data']['items']

    start_index = alt_counter_postoyan
    end_index = min(start_index + 5, len(items))

    if start_index >= len(items):
        await update.message.reply_text("Вы просмотрели все события! \n Для просмотра меню нажмите /start")
        return

    for i in range(start_index, end_index):
        try:
            event = items[i]
            title = event.get('name', 'Без названия')
            museum = event.get('place', {}).get('name', 'Не указано')

            start_date_unix = event.get('startDateUnix')
            end_date_unix = event.get('endDateUnix')

            start_date = datetime.datetime.fromtimestamp(start_date_unix).strftime('%d.%m.%Y') if start_date_unix else 'Не указано'
            end_date = datetime.datetime.fromtimestamp(end_date_unix).strftime('%d.%m.%Y') if end_date_unix else 'Не указано'


            temp_url = event.get('url', '')
            url = f"{MUSEUM_URL}{temp_url}" if temp_url else MUSEUM_URL

            message = (
                f"{i + 1}. **{title}**\n"
                f"🏛 {museum}\n"
                f"📅 Проходит с {start_date}\n"
                f"по {end_date}\n"
                #f"тип события: {hashtag}\n"
                f"🔗 [Подробнее]({url})\n"
            )

            await update.message.reply_text(message, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error processing event {i + 1}: {e}")
            continue

    alt_counter_postoyan = end_index
    count += 5

    if alt_counter_postoyan < len(items):
        await update.message.reply_text("Увидеть больше /more_postoyan")
    else:
        await update.message.reply_text("Вы просмотрели все события!  \n Для просмотра меню нажмите /start")




# ========== ОБРАБОТЧИКИ КНОПОК ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user

    keyboard = [
        [
            InlineKeyboardButton("Ближайшие события", callback_data='events')
        ],
        [
            InlineKeyboardButton("Все события", callback_data='allv'),
            InlineKeyboardButton("Внешние выставки", callback_data='vnesh')
        ],
        [
            InlineKeyboardButton("Будущие выставки", callback_data='bud'),
            InlineKeyboardButton("Постоянные экспозиции", callback_data='postoyan')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = f"""
Привет, {user.first_name}! 🎨

Я помогу вам отслеживать события Третьяковской галереи:
- Выставки
- Экскурсии

Доступные команды:
/events - Ближайшие события
/allv - Все события
/vnesh - Внешние выставки
/bud - Будущие события
/postoyan - Постоянные экспозиции"""

    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query

    if not query:
        return

    await query.answer()

    if query.data == 'events':
        original_message = query.message.text

        await query.edit_message_text(
            text="🔄 Загружаю ближайшие события...",
            parse_mode='Markdown'
        )

        try:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="🎭 **Ближайшие события:**"
            )

            events_data = await get_events(5)

            if events_data and 'data' in events_data and 'items' in events_data['data']:
                items = events_data['data']['items'][:5]

                for i, event in enumerate(items, 1):
                    try:
                        title = event.get('name', 'Без названия')
                        museum = event.get('place', {}).get('name', 'Не указано')

                        start_date_unix = event.get('startDateUnix')
                        end_date_unix = event.get('endDateUnix')

                        start_date = datetime.datetime.fromtimestamp(start_date_unix).strftime('%d.%m.%Y') if start_date_unix else 'Не указано'
                        end_date = datetime.datetime.fromtimestamp(end_date_unix).strftime('%d.%m.%Y') if end_date_unix else 'Не указано'

                        temp_url = event.get('url', '')
                        url = f"{MUSEUM_URL}{temp_url}" if temp_url else MUSEUM_URL

                        message = (
                            f"{i}. **{title}**\n"
                            f"🏛 {museum}\n"
                            f"📅 Проходит с {start_date}\n"
                            f"по {end_date}\n"
                            f"🔗 [Подробнее]({url})\n"
                        )

                        await context.bot.send_message(
                            chat_id=query.message.chat_id,
                            text=message,
                            parse_mode='Markdown'
                        )

                    except Exception as e:
                        logger.error(f"Error in button handler: {e}")
                        continue


            else:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="На данный момент событий нет. \n Нажмите, чтобы открыть меню /start"
                )

            keyboard = [
                [
                    InlineKeyboardButton("Ближайшие события", callback_data='events')
                ],
                [
                    InlineKeyboardButton("Все события", callback_data='allv'),
                    InlineKeyboardButton("Внешние выставки", callback_data='vnesh')
                ],
                [
                    InlineKeyboardButton("Будущие выставки", callback_data='bud'),
                    InlineKeyboardButton("Постоянные экспозиции", callback_data='postoyan')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text=original_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error in events button: {e}")
            await query.edit_message_text(
                text=f"Ошибка при получении событий: {e}",
                parse_mode='Markdown'
            )

    elif query.data == 'allv':
        await query.edit_message_text(
            text="🔄 Загружаю Все события...",
            parse_mode='Markdown'
        )

        try:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="🎭 **Все события:**"
            )

            await allv_command_simulated(context, query.message.chat_id)

            keyboard = [
                [
                    InlineKeyboardButton("Ближайшие события", callback_data='events')
                ],
                [
                    InlineKeyboardButton("Все события", callback_data='allv'),
                    InlineKeyboardButton("Внешние выставки", callback_data='vnesh')
                ],
                [
                    InlineKeyboardButton("Будущие выставки", callback_data='bud'),
                    InlineKeyboardButton("Постоянные экспозиции", callback_data='postoyan')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text="Выберите действие:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error in allv button: {e}")
            await query.edit_message_text(
                text=f"Ошибка: {e}",
                parse_mode='Markdown'
            )
#========================
#==

    elif query.data == 'vnesh':
        await query.edit_message_text(
            text="🔄 Загружаю внешние выставки...",
            parse_mode='Markdown'
        )

        try:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="🎭 **Внешние выставки:**"
            )

            await vnesh_command_simulated(context, query.message.chat_id)

            keyboard = [
                [
                    InlineKeyboardButton("Ближайшие события", callback_data='events')
                ],
                [
                    InlineKeyboardButton("Все события", callback_data='allv'),
                    InlineKeyboardButton("Внешние выставки", callback_data='vnesh')
                ],
                [
                    InlineKeyboardButton("Будущие выставки", callback_data='bud'),
                    InlineKeyboardButton("Постоянные экспозиции", callback_data='postoyan')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text="Выберите действие:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error in vnesh button: {e}")
            await query.edit_message_text(
                text=f"Ошибка: {e}",
                parse_mode='Markdown'
            )


    elif query.data == 'bud':
        await query.edit_message_text(
            text="🔄 Загружаю будущие выставки...",
            parse_mode='Markdown'
        )

        try:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="🎭 **Будущие выставки:**"
            )

            await bud_command_simulated(context, query.message.chat_id)

            keyboard = [
                [
                    InlineKeyboardButton("Ближайшие события", callback_data='events')
                ],
                [
                    InlineKeyboardButton("Все события", callback_data='allv'),
                    InlineKeyboardButton("Внешние выставки", callback_data='vnesh')
                ],
                [
                    InlineKeyboardButton("Будущие выставки", callback_data='bud'),
                    InlineKeyboardButton("Постоянные экспозиции", callback_data='postoyan')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text="Выберите действие:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error in vnesh button: {e}")
            await query.edit_message_text(
                text=f"Ошибка: {e}",
                parse_mode='Markdown'
            )
#===
#========================
    elif query.data == 'postoyan':
        await query.edit_message_text(
            text="🔄 Загружаю постоянные экспозиции...",
            parse_mode='Markdown'
        )

        try:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="🎭 **Постоянные экспозиции:**"
            )

            await postoyan_command_simulated(context, query.message.chat_id)

            keyboard = [
                [
                    InlineKeyboardButton("Ближайшие события", callback_data='events')
                ],
                [
                    InlineKeyboardButton("Все события", callback_data='allv'),
                    InlineKeyboardButton("Внешние выставки", callback_data='vnesh')
                ],
                [
                    InlineKeyboardButton("Будущие выставки", callback_data='bud'),
                    InlineKeyboardButton("Постоянные экспозиции", callback_data='postoyan')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text="Выберите действие:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error in postoyan button: {e}")
            await query.edit_message_text(
                text=f"Ошибка: {e}",
                parse_mode='Markdown'
            )

async def allv_command_simulated(context, chat_id):
    """Упрощенная версия allv_command для вызова из button_handler"""
    events_data = await get_events(5)
    global alt_counter_allv

    if not events_data or 'data' not in events_data or 'items' not in events_data['data']:
        await context.bot.send_message(chat_id, "На данный момент событий нет.")
        return

    items = events_data['data']['items'][:5]

    for i, event in enumerate(items, 1):
        try:
            title = event.get('name', 'Без названия')
            museum = event.get('place', {}).get('name', 'Не указано')

            start_date_unix = event.get('startDateUnix')
            end_date_unix = event.get('endDateUnix')

            start_date = datetime.datetime.fromtimestamp(start_date_unix).strftime('%d.%m.%Y') if start_date_unix else 'Не указано'
            end_date = datetime.datetime.fromtimestamp(end_date_unix).strftime('%d.%m.%Y') if end_date_unix else 'Не указано'

            hashtag = event.get('hashtag', 'Не указано')

            temp_url = event.get('url', '')
            url = f"{MUSEUM_URL}{temp_url}" if temp_url else MUSEUM_URL

            message = (
                f"{i}. **{title}**\n"
                f"🏛 {museum}\n"
                f"📅 Проходит с {start_date}\n"
                f"по {end_date}\n"
                f"тип события: {hashtag}\n"
                f"🔗 [Подробнее]({url})\n"
            )

            alt_counter_allv += 1
            await context.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error in allv_simulated: {e}")
            continue

    await context.bot.send_message(chat_id, "Увидеть больше /more")

    return alt_counter_allv

#============================
#=

async def vnesh_command_simulated(context, chat_id):
    """Упрощенная версия vnesh_command для вызова из button_handler"""
    events_data = await get_vnesh_events(5)
    global alt_counter_vnesh

    if not events_data or 'data' not in events_data or 'items' not in events_data['data']:
        await context.bot.send_message(chat_id, "На данный момент событий нет.")
        return

    items = events_data['data']['items'][:5]

    for i, event in enumerate(items, 1):
        try:
            title = event.get('name', 'Без названия')
            museum = event.get('place', {}).get('name', 'Не указано')

            start_date_unix = event.get('startDateUnix')
            end_date_unix = event.get('endDateUnix')

            start_date = datetime.datetime.fromtimestamp(start_date_unix).strftime('%d.%m.%Y') if start_date_unix else 'Не указано'
            end_date = datetime.datetime.fromtimestamp(end_date_unix).strftime('%d.%m.%Y') if end_date_unix else 'Не указано'

            temp_url = event.get('url', '')
            url = f"{MUSEUM_URL}{temp_url}" if temp_url else MUSEUM_URL

            message = (
                f"{i}. **{title}**\n"
                f"🏛 {museum}\n"
                f"📅 Проходит с {start_date}\n"
                f"по {end_date}\n"
                f"🔗 [Подробнее]({url})\n"
            )

            alt_counter_vnesh += 1
            await context.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error in vnesh_simulated: {e}")
            continue

    await context.bot.send_message(chat_id, "Увидеть больше /more_vnesh")

    return alt_counter_vnesh



async def bud_command_simulated(context, chat_id):
    """Упрощенная версия bud_command для вызова из button_handler"""
    events_data = await get_bud_events(5)
    global alt_counter_bud

    if not events_data or 'data' not in events_data or 'items' not in events_data['data']:
        await context.bot.send_message(chat_id, "На данный момент событий нет.")
        return

    items = events_data['data']['items'][:5]

    for i, event in enumerate(items, 1):
        try:
            title = event.get('name', 'Без названия')
            museum = event.get('place', {}).get('name', 'Не указано')

            start_date_unix = event.get('startDateUnix')
            end_date_unix = event.get('endDateUnix')

            start_date = datetime.datetime.fromtimestamp(start_date_unix).strftime('%d.%m.%Y') if start_date_unix else 'Не указано'
            end_date = datetime.datetime.fromtimestamp(end_date_unix).strftime('%d.%m.%Y') if end_date_unix else 'Не указано'

            temp_url = event.get('url', '')
            url = f"{MUSEUM_URL}{temp_url}" if temp_url else MUSEUM_URL

            message = (
                f"{i}. **{title}**\n"
                f"🏛 {museum}\n"
                f"📅 Проходит с {start_date}\n"
                f"по {end_date}\n"
                f"🔗 [Подробнее]({url})\n"
            )

            alt_counter_bud += 1
            await context.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error in vnesh_simulated: {e}")
            continue

    await context.bot.send_message(chat_id, "Увидеть больше /more_bud")

    return alt_counter_bud

#===========================
async def postoyan_command_simulated(context, chat_id):
    """Упрощенная версия postoyan_command для вызова из button_handler"""
    events_data = await get_postoyan_events(5)
    global alt_counter_postoyan

    if not events_data or 'data' not in events_data or 'items' not in events_data['data']:
        await context.bot.send_message(chat_id, "На данный момент событий нет.")
        return

    items = events_data['data']['items'][:5]

    for i, event in enumerate(items, 1):
        try:
            title = event.get('name', 'Без названия')
            museum = event.get('place', {}).get('name', 'Не указано')

            start_date_unix = event.get('startDateUnix')
            end_date_unix = event.get('endDateUnix')

            start_date = datetime.datetime.fromtimestamp(start_date_unix).strftime('%d.%m.%Y') if start_date_unix else 'Не указано'
            end_date = datetime.datetime.fromtimestamp(end_date_unix).strftime('%d.%m.%Y') if end_date_unix else 'Не указано'

            temp_url = event.get('url', '')
            url = f"{MUSEUM_URL}{temp_url}" if temp_url else MUSEUM_URL

            message = (
                f"{i}. **{title}**\n"
                f"🏛 {museum}\n"
                f"📅 Проходит с {start_date}\n"
                f"по {end_date}\n"
                f"🔗 [Подробнее]({url})\n"
            )

            alt_counter_postoyan += 1
            await context.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error in postoyan_simulated: {e}")
            continue

    await context.bot.send_message(chat_id, "Увидеть больше /more_postoyan")

    return alt_counter_postoyan
# ========== ЗАПУСК БОТА ==========

def main():
    """Запуск бота"""
    if not TELEGRAM_TOKEN:
        raise ValueError("Не задан TELEGRAM_TOKEN")

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("events", events_command))
    application.add_handler(CommandHandler("allv", allv_command))
    application.add_handler(CommandHandler("more", more_command))
    application.add_handler(CommandHandler("vnesh", vnesh_command))
    application.add_handler(CommandHandler("more_vnesh", more_vnesh_command))
    application.add_handler(CommandHandler("bud", bud_command))
    application.add_handler(CommandHandler("more_bud", more_bud_command))
    application.add_handler(CommandHandler("postoyan", postoyan_command))
    application.add_handler(CommandHandler("more_postoyan", more_postoyan_command))

    application.add_handler(CallbackQueryHandler(button_handler))

    logger.info("🤖 Бот запущен...")

    try:
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")


if __name__ == '__main__':
    main()