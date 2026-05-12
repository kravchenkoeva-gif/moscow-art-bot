import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, PreCheckoutQueryHandler
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN", "8901098556:AAFoxXjoq1rBObcUQNLB6rChd6I_EsQpDv8")

# Цены в рублях (в копейках для Telegram)
PRICES = {
    "tour1": 39900,   # 399 ₽
    "tour2": 49900,   # 499 ₽
    "tour3": 69900,   # 699 ₽
    "tour4": 99900,   # 999 ₽
}

TOUR_NAMES = {
    "tour1": "⚡ «Сердце Москвы» · 30 мин · 3 точки",
    "tour2": "🎨 «Замоскворечье» · 1 час · 4 точки",
    "tour3": "🏛 «Арбат и переулки» · 1.5 часа · 5 точек",
    "tour4": "🌆 «Большая Москва» · 2.5 часа · 7 точек",
}

# Контент экскурсий — список точек для каждой
TOURS = {
    "tour1": [
        {
            "title": "📍 Точка 1 из 3 — Собор Василия Блаженного",
            "text": (
                "Встань прямо напротив собора и найди глазами самый высокий купол.\n\n"
                "🎨 <b>Картина Манушина «Собор Василия Блаженного. Тихое утро после дождя» (2023)</b>\n\n"
                "Художник пришёл сюда рано утром — когда туристов ещё нет, брусчатка мокрая, и собор отражается в лужах. "
                "Он писал не парадный открыточный вид, а живой город — тихий и немного сонный.\n\n"
                "💬 <b>Факт:</b> Собор построили в 1561 году по приказу Ивана Грозного. По легенде, царь приказал ослепить "
                "архитекторов, чтобы они не смогли построить ничего красивее. Историки считают это выдумкой — но легенда живёт.\n\n"
                "🧩 <b>Загадка:</b> Сколько куполов у собора? Посчитай сам стоя перед ним. Не гугли!"
            ),
            "answer": (
                "🧩 Правильный ответ — <b>11 куполов!</b>\n\n"
                "Многие думают что 9 или 10 — но их именно 11. Каждый уникален по форме и цвету, ни один не повторяет другой.\n\n"
                "Манушин на своей картине передал именно это ощущение — смотришь и не можешь насчитать, сбиваешься 😊\n\n"
                "➡️ <b>Следующая остановка — Никольская улица.</b>\n"
                "Иди вдоль Кремлёвской стены направо, потом поверни налево в арку. 3 минуты пешком."
            ),
        },
        {
            "title": "📍 Точка 2 из 3 — Никольская улица",
            "text": (
                "Остановись в середине улицы и посмотри вдоль неё в сторону Красной площади.\n\n"
                "🎨 <b>Картина Манушина «Выход к Александровскому саду» (2025)</b>\n\n"
                "Художник поймал момент когда зимнее солнце бьёт вдоль улицы и всё золотится — фасады, брусчатка, даже воздух. "
                "Посмотри — видишь этот свет прямо сейчас?\n\n"
                "💬 <b>Факт:</b> Никольской улице больше 600 лет. Здесь находился первый печатный двор России — "
                "в 1564 году Иван Фёдоров напечатал здесь первую русскую книгу.\n\n"
                "🧩 <b>Загадка:</b> Найди на этой улице здание с готическими башенками — оно явно выбивается из общего стиля. "
                "Что это за здание?"
            ),
            "answer": (
                "🧩 Это <b>Никольские торговые ряды</b>!\n\n"
                "Построены в 1893 году в псевдоготическом стиле — архитектор намеренно сделал их похожими на средневековый "
                "европейский замок. В то время это был настоящий архитектурный скандал среди москвичей.\n\n"
                "Манушин любит именно такие контрасты — старое и новое, русское и европейское рядом. Это и есть настоящая Москва.\n\n"
                "➡️ <b>Последняя точка — Варварка.</b>\n"
                "Иди до конца Никольской, поверни направо на Красную площадь, затем налево мимо Василия Блаженного. "
                "Варварка начинается сразу за ним. 5 минут пешком."
            ),
        },
        {
            "title": "📍 Точка 3 из 3 — Варварка",
            "text": (
                "Встань в начале улицы и посмотри вдоль неё — перед тобой пять церквей XVI-XVII века.\n\n"
                "🎨 <b>Картина Манушина «Вечер на Варварке» (2025)</b>\n\n"
                "Манушин написал эту улицу вечером, когда фонари уже зажглись, а дневная суета стихла. "
                "Купола церквей светятся тёплым золотом на фоне тёмного неба.\n\n"
                "💬 <b>Факт:</b> Варварка — одна из древнейших улиц Москвы. Здесь стоят палаты Романовых — "
                "дом, где родился первый царь династии Романовых Михаил Фёдорович в 1596 году.\n\n"
                "🧩 <b>Загадка:</b> Сколько церквей ты видишь на этой улице? Пройди до конца и посчитай."
            ),
            "answer": (
                "🧩 На Варварке <b>5 церквей</b>!\n\n"
                "Варварская, Максима Блаженного, Георгия Победоносца, Иоанна Предтечи и Знаменский монастырь — "
                "все в одном ряду, плечом к плечу. Нигде в Москве больше нет такой концентрации древних храмов.\n\n"
                "🎉 <b>Поздравляю — ты прошёл экскурсию «Сердце Москвы»!</b>\n\n"
                "Ты увидел три места, которые Манушин написал с любовью и вниманием к деталям. "
                "Надеемся, теперь ты смотришь на них немного иначе 🎨\n\n"
                "Хочешь продолжить? Возвращайся в главное меню 👇"
            ),
        },
    ],
    "tour2": [
        {
            "title": "📍 Точка 1 из 4 — Климентовская церковь на Пятницкой",
            "text": (
                "Встань напротив церкви и посмотри на её барочный фасад.\n\n"
                "🎨 <b>Картина Манушина «Климентовская церковь на Пятницкой» (2023)</b>\n\n"
                "Манушин написал её в зимний день — белая церковь на фоне серого неба, голые деревья. "
                "Никакой лишней красивости — просто честный московский февраль.\n\n"
                "💬 <b>Факт:</b> Церковь Климента Папы Римского — один из лучших образцов барокко в Москве. "
                "Строили её 44 года — с 1742 по 1786 год. Внутри сохранился уникальный иконостас.\n\n"
                "🧩 <b>Загадка:</b> Сколько колонн на главном фасаде церкви? Посчитай."
            ),
            "answer": (
                "🧩 На фасаде <b>8 колонн</b>!\n\n"
                "Это классический барочный приём — чётное число колонн создаёт ощущение симметрии и торжественности.\n\n"
                "➡️ <b>Следующая точка — Третьяковская галерея.</b>\n"
                "Иди по Пятницкой до Климентовского переулка, поверни направо. "
                "Лаврушинский переулок будет слева. 7 минут пешком."
            ),
        },
        {
            "title": "📍 Точка 2 из 4 — Третьяковская галерея",
            "text": (
                "Встань у главного входа с знаменитым фасадом в русском стиле.\n\n"
                "🎨 <b>Картина Манушина «Третьяковка» (2024)</b>\n\n"
                "Художник написал вечерний Лаврушинский переулок — когда музей уже закрыт, "
                "туристы разошлись и переулок стал тихим и почти домашним.\n\n"
                "💬 <b>Факт:</b> Павел Третьяков начал собирать картины в 1856 году и в итоге подарил "
                "всю коллекцию городу Москве. Сегодня здесь более 180 000 экспонатов.\n\n"
                "🧩 <b>Загадка:</b> Кто изображён на главном фасаде галереи над входом?"
            ),
            "answer": (
                "🧩 Над входом — <b>герб Москвы</b> с Георгием Победоносцем!\n\n"
                "Фасад галереи в 1902 году спроектировал художник Виктор Васнецов — тот самый, "
                "что написал «Алёнушку» и «Богатырей», которые висят внутри.\n\n"
                "➡️ <b>Следующая точка — Большая Ордынка.</b>\n"
                "Выйди из переулка на Большую Ордынку и иди направо. 5 минут пешком."
            ),
        },
        {
            "title": "📍 Точка 3 из 4 — Большая Ордынка",
            "text": (
                "Остановись и посмотри вдоль улицы — это главная улица Замоскворечья.\n\n"
                "🎨 <b>Картина Манушина «Вечер на Большой Ордынке» (2024)</b>\n\n"
                "Манушин написал эту улицу осенним вечером — жёлтые фонари, мокрый асфальт, "
                "редкие прохожие. Узнаёшь это настроение?\n\n"
                "💬 <b>Факт:</b> Название улицы происходит от слова «Орда» — по ней шли послы "
                "из Золотой Орды в Кремль. Улице более 600 лет.\n\n"
                "🧩 <b>Загадка:</b> Найди на этой улице дом с необычным эркером — "
                "выступающим балконом угловой формы. На каком номере дома он находится?"
            ),
            "answer": (
                "🧩 Это доходный дом — таких на Ордынке несколько!\n\n"
                "Замоскворечье было купеческим районом — здесь строили добротные "
                "доходные дома с красивыми фасадами. Каждый дом здесь — отдельная история.\n\n"
                "➡️ <b>Последняя точка — Марфо-Мариинская обитель.</b>\n"
                "Продолжай идти по Ордынке — обитель будет справа, дом 34. 3 минуты."
            ),
        },
        {
            "title": "📍 Точка 4 из 4 — Марфо-Мариинская обитель",
            "text": (
                "Войди во двор обители и остановись у белого собора.\n\n"
                "🎨 <b>Картина Манушина «Марфо-Мариинская обитель» (2024)</b>\n\n"
                "Манушин написал её в тихий зимний день — белые стены, белый снег, "
                "тишина посреди шумного города. Оазис покоя.\n\n"
                "💬 <b>Факт:</b> Обитель основала великая княгиня Елизавета Фёдоровна в 1909 году "
                "после гибели мужа. Она отказалась от придворной жизни и посвятила себя помощи бедным. "
                "Собор построил архитектор Щусев — тот же, что позже построил Мавзолей Ленина.\n\n"
                "🧩 <b>Загадка:</b> Найди на стенах собора необычные украшения — "
                "они отличаются от типичных православных церквей. Что ты видишь?"
            ),
            "answer": (
                "🧩 Это <b>романский орнамент</b> — редкость для русской архитектуры!\n\n"
                "Щусев намеренно смешал древнерусский стиль с романским — получилось что-то "
                "совершенно уникальное. Именно поэтому обитель так непохожа на другие московские церкви.\n\n"
                "🎉 <b>Поздравляю — ты прошёл экскурсию «Замоскворечье»!</b>\n\n"
                "Ты прошёл по самому живописному району Москвы глазами художника Манушина. "
                "Надеемся, эти места теперь будут значить для тебя чуть больше 🎨\n\n"
                "Хочешь продолжить? Возвращайся в главное меню 👇"
            ),
        },
    ],
}

# База данных пользователей (в памяти, для продакшена нужна БД)
user_data = {}

def get_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {"purchased": [], "progress": {}}
    return user_data[user_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🗺 Смотреть экскурсии", callback_data="show_tours")],
        [InlineKeyboardButton("🎫 Мои экскурсии", callback_data="my_tours")],
    ]
    await update.message.reply_text(
        "👋 Добро пожаловать в «Москва глазами художника»!\n\n"
        "Это прогулки по Москве через картины художника Андрея Манушина — "
        "человека, который видит город таким, каким его не замечают в спешке.\n\n"
        "Каждая экскурсия — маршрут с историями, фактами и загадками прямо на месте. "
        "Ты идёшь по городу, а бот рассказывает.\n\n"
        "Выбери что хочешь сделать 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_tours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = get_user(query.from_user.id)

    keyboard = []
    for tour_id, name in TOUR_NAMES.items():
        price = PRICES[tour_id] // 100
        purchased = "✅ " if tour_id in user["purchased"] else ""
        keyboard.append([InlineKeyboardButton(
            f"{purchased}{name} — {price} ₽",
            callback_data=f"tour_info_{tour_id}"
        )])
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_start")])

    await query.edit_message_text(
        "🗺 <b>Наши экскурсии</b>\n\n"
        "Выбери экскурсию чтобы узнать подробнее:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def tour_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tour_id = query.data.replace("tour_info_", "")
    user = get_user(query.from_user.id)
    price = PRICES[tour_id] // 100

    descriptions = {
        "tour1": "📍 3 точки: Собор Василия Блаженного → Никольская улица → Варварка\n⏱ 30 минут пешком\n🎨 3 картины Манушина",
        "tour2": "📍 4 точки: Климентовская церковь → Третьяковка → Большая Ордынка → Марфо-Мариинская обитель\n⏱ 1 час пешком\n🎨 4 картины Манушина",
        "tour3": "📍 5 точек: Арбат → Сивцев Вражек → Церковь на Вражке → Дом Пашкова → Петровский переулок\n⏱ 1.5 часа пешком\n🎨 5 картин Манушина",
        "tour4": "📍 7 точек: Новодевичий монастырь → МГУ → Котельническая → Хитровка → Яузские ворота → Курский вокзал → Комсомольская площадь\n⏱ 2.5 часа пешком\n🎨 7 картин Манушина",
    }

    if tour_id in user["purchased"]:
        keyboard = [
            [InlineKeyboardButton("▶️ Продолжить экскурсию", callback_data=f"continue_{tour_id}")],
            [InlineKeyboardButton("🔄 Начать заново", callback_data=f"restart_{tour_id}")],
            [InlineKeyboardButton("◀️ Назад", callback_data="show_tours")],
        ]
        status = "✅ <b>Куплено</b>\n\n"
    else:
        keyboard = [
            [InlineKeyboardButton(f"💳 Купить за {price} ₽", callback_data=f"buy_{tour_id}")],
            [InlineKeyboardButton("◀️ Назад", callback_data="show_tours")],
        ]
        status = ""

    await query.edit_message_text(
        f"{status}<b>{TOUR_NAMES[tour_id]}</b>\n\n"
        f"{descriptions[tour_id]}\n\n"
        f"💰 Стоимость: <b>{price} ₽</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def buy_tour(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tour_id = query.data.replace("buy_", "")
    price = PRICES[tour_id]

    # Для теста — сразу даём доступ без реальной оплаты
    # Когда подключишь ЮKassa — раскомментируй блок ниже
    user = get_user(query.from_user.id)
    if tour_id not in user["purchased"]:
        user["purchased"].append(tour_id)
        user["progress"][tour_id] = {"point": 0, "waiting_answer": False}

    keyboard = [[InlineKeyboardButton("▶️ Начать экскурсию", callback_data=f"continue_{tour_id}")]]
    await query.edit_message_text(
        "✅ <b>Доступ открыт!</b>\n\n"
        f"Экскурсия {TOUR_NAMES[tour_id]} теперь доступна.\n\n"
        "Нажми кнопку ниже чтобы начать 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def continue_tour(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tour_id = query.data.replace("continue_", "")
    user = get_user(query.from_user.id)

    if tour_id not in user["purchased"]:
        await query.answer("❌ Сначала купи экскурсию!", show_alert=True)
        return

    if tour_id not in user["progress"]:
        user["progress"][tour_id] = {"point": 0, "waiting_answer": False}

    await send_point(query, tour_id, user)

async def restart_tour(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tour_id = query.data.replace("restart_", "")
    user = get_user(query.from_user.id)
    user["progress"][tour_id] = {"point": 0, "waiting_answer": False}
    await send_point(query, tour_id, user)

async def send_point(query, tour_id, user):
    if tour_id not in TOURS:
        await query.edit_message_text("⚠️ Эта экскурсия пока в разработке. Скоро будет!")
        return

    points = TOURS[tour_id]
    progress = user["progress"][tour_id]
    point_idx = progress["point"]
    waiting = progress["waiting_answer"]

    if point_idx >= len(points):
        keyboard = [[InlineKeyboardButton("🗺 К экскурсиям", callback_data="show_tours")]]
        await query.edit_message_text(
            "🎉 Экскурсия завершена! Спасибо что прошёл с нами.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    point = points[point_idx]

    if not waiting:
        # Показываем точку
        progress["waiting_answer"] = True
        keyboard = [[InlineKeyboardButton("💡 Показать ответ", callback_data=f"answer_{tour_id}")]]
        await query.edit_message_text(
            f"<b>{point['title']}</b>\n\n{point['text']}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
    else:
        # Показываем ответ и переходим дальше
        progress["waiting_answer"] = False
        progress["point"] += 1
        next_idx = progress["point"]

        if next_idx >= len(points):
            keyboard = [[InlineKeyboardButton("🗺 К экскурсиям", callback_data="show_tours")]]
        else:
            keyboard = [[InlineKeyboardButton("➡️ Следующая точка", callback_data=f"continue_{tour_id}")]]

        await query.edit_message_text(
            point["answer"],
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

async def answer_point(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    tour_id = query.data.replace("answer_", "")
    user = get_user(query.from_user.id)
    await send_point(query, tour_id, user)

async def my_tours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = get_user(query.from_user.id)

    if not user["purchased"]:
        keyboard = [
            [InlineKeyboardButton("🗺 Смотреть экскурсии", callback_data="show_tours")],
        ]
        await query.edit_message_text(
            "У тебя пока нет купленных экскурсий.\n\nПосмотри что есть 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    keyboard = []
    for tour_id in user["purchased"]:
        keyboard.append([InlineKeyboardButton(
            TOUR_NAMES[tour_id],
            callback_data=f"tour_info_{tour_id}"
        )])
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_start")])

    await query.edit_message_text(
        "🎫 <b>Твои экскурсии:</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def back_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🗺 Смотреть экскурсии", callback_data="show_tours")],
        [InlineKeyboardButton("🎫 Мои экскурсии", callback_data="my_tours")],
    ]
    await query.edit_message_text(
        "👋 Добро пожаловать в «Москва глазами художника»!\n\n"
        "Прогулки по Москве через картины Андрея Манушина.\n\n"
        "Выбери что хочешь сделать 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_tours, pattern="^show_tours$"))
    app.add_handler(CallbackQueryHandler(my_tours, pattern="^my_tours$"))
    app.add_handler(CallbackQueryHandler(back_start, pattern="^back_start$"))
    app.add_handler(CallbackQueryHandler(tour_info, pattern="^tour_info_"))
    app.add_handler(CallbackQueryHandler(buy_tour, pattern="^buy_"))
    app.add_handler(CallbackQueryHandler(continue_tour, pattern="^continue_"))
    app.add_handler(CallbackQueryHandler(restart_tour, pattern="^restart_"))
    app.add_handler(CallbackQueryHandler(answer_point, pattern="^answer_"))
    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
