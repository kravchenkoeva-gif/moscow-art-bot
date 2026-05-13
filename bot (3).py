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
                "Попробуй на секунду забыть всё что ты знаешь об этом месте — открытки, магниты, учебники. Просто смотри.\n\n"
                "🎨 <b>Картина Манушина «Собор Василия Блаженного. Тихое утро после дождя» (2023)</b>\n\n"
                "Манушин пришёл сюда на рассвете — в пять утра, когда площадь была почти пустой. Брусчатка блестела после ночного дождя, "
                "купола отражались в лужах, и весь этот невероятный силуэт плавал в сером утреннем воздухе. "
                "Не парадный, не туристический — а живой, дышащий, почти хрупкий.\n\n"
                "Именно такой взгляд отличает Манушина: он ищет момент, когда город перестаёт позировать.\n\n"
                "💬 <b>История:</b> Собор строили 6 лет — с 1555 по 1561 год. Его настоящее название — Собор Покрова Пресвятой "
                "Богородицы на Рву. «Василием Блаженным» его называют по имени юродивого, похороненного у его стен — "
                "человека, которого боялся даже Иван Грозный. По легенде, Василий годами собирал деньги и незадолго до смерти "
                "отдал их царю именно на этот храм.\n\n"
                "Архитекторов звали Барма и Постник. По легенде, после завершения строительства царь велел их ослепить — "
                "чтобы не смогли построить ничего краше. Историки считают это красивой выдумкой, но легенда живёт уже 400 лет.\n\n"
                "🧩 <b>Загадка:</b> Сколько куполов у собора? Встань напротив и посчитай сам — не гугли!"
            ),
            "answer": (
                "🧩 Правильный ответ — <b>11 куполов!</b>\n\n"
                "Большинство людей называют 9 или 10 — но их именно 11. Каждый купол уникален: своя форма, свой цвет, "
                "свой характер. Это не случайность — собор строили как архитектурную поэму, где каждая часть является отдельной главой.\n\n"
                "Манушин говорит, что именно это его восхищает: смотришь и не можешь насчитать, сбиваешься, начинаешь снова. "
                "Здание, которое не даёт себя измерить взглядом 😊\n\n"
                "➡️ <b>Следующая остановка — Никольская улица.</b>\n"
                "Иди вдоль Кремлёвской стены направо, поверни налево в арку. 3 минуты пешком."
            ),
        },
        {
            "title": "📍 Точка 2 из 3 — Никольская улица",
            "text": (
                "Добро пожаловать на одну из старейших улиц Москвы. Ей больше шестисот лет — и она помнила опричнину, "
                "Смутное время, Наполеона и революцию. Сейчас выглядит нарядно — но за витринами скрывается очень древний город.\n\n"
                "🎨 <b>Картина Манушина «Выход к Александровскому саду» (2025)</b>\n\n"
                "Манушин написал эту улицу зимой, в солнечный полдень — когда низкое зимнее солнце бьёт прямо вдоль улицы "
                "и золотит всё: фасады, брусчатку, даже воздух между домами. На картине почти нет людей — только свет, "
                "перспектива и ощущение что ты один в огромном красивом городе.\n\n"
                "Встань в середине улицы. Посмотри в сторону Красной площади — видишь как она сужается вдали и упирается в башню? "
                "Именно этот вид писал Манушин.\n\n"
                "💬 <b>История:</b> Здесь в 1563 году Иван Фёдоров основал первый печатный двор России и напечатал первую "
                "русскую книгу — «Апостол». Сейчас на этом месте стоит здание Синодальной типографии — то самое, с готическими "
                "башенками, которое так выбивается из общего ряда. Архитектор намеренно сделал его похожим на средневековый "
                "европейский замок — в память о печатном дворе. Москвичи спорили об уместности, спорили — и привыкли.\n\n"
                "🧩 <b>Загадка:</b> Найди здание с готическими башенками и посмотри внимательно на его фасад — "
                "там спрятан герб. Что на нём изображено?"
            ),
            "answer": (
                "🧩 На гербе Синодальной типографии — <b>двуглавый орёл</b>!\n\n"
                "Это государственный герб Российской империи — типография была официальным государственным издательством. "
                "Именно здесь печатались церковные книги для всей страны.\n\n"
                "Манушин любит именно такие детали — маленькие знаки большой истории, которые большинство людей "
                "проходит мимо не замечая. «Город полон подписей,» — говорит он. — «Надо только научиться их читать.»\n\n"
                "➡️ <b>Последняя точка — Варварка.</b>\n"
                "Иди до конца Никольской, поверни направо на Красную площадь, затем налево мимо Василия Блаженного. "
                "Варварка начинается сразу за ним. 5 минут пешком."
            ),
        },
        {
            "title": "📍 Точка 3 из 3 — Варварка",
            "text": (
                "Ты дошёл до финальной точки — и, возможно, до самого удивительного места в центре Москвы. "
                "Варварка — это улица, на которой пять церквей стоят плечом к плечу, и каждой больше трёхсот лет.\n\n"
                "🎨 <b>Картина Манушина «Вечер на Варварке» (2025)</b>\n\n"
                "Манушин написал эту улицу вечером — когда фонари уже зажглись, а дневная суета ещё не стихла. "
                "Тёплый свет падает на белые стены церквей, купола светятся на фоне тёмного неба. "
                "Манушин поймал момент контраста — старое и новое, тишина и движение, камень и свет.\n\n"
                "Встань в начале улицы и посмотри вдоль неё. Это один из немногих видов в Москве, "
                "который почти не изменился за последние сто лет.\n\n"
                "💬 <b>История:</b> Здесь в 1596 году родился Михаил Фёдорович Романов — первый царь династии, "
                "правившей Россией триста лет. Его родовые палаты стоят до сих пор — небольшое красное здание, "
                "которое легко не заметить среди церквей. Пять храмов на одной улице — не случайность: "
                "в средние века Варварка была главной дорогой из Кремля на восток, и купеческие общины "
                "строили здесь свои церкви одну за другой.\n\n"
                "🧩 <b>Загадка:</b> Сколько церквей на этой улице? Пройди до конца и посчитай все — "
                "включая те, что спрятаны во дворах."
            ),
            "answer": (
                "🧩 На Варварке <b>5 церквей</b>!\n\n"
                "Варварская, Максима Блаженного, Георгия Победоносца, Иоанна Предтечи и Знаменский монастырь — "
                "все в одном ряду. Нигде в Москве больше нет такой концентрации древних храмов на одной улице.\n\n"
                "Манушин говорит, что Варварка — его любимое место в центре Москвы именно потому, что здесь "
                "история не спрятана в музеях, а стоит прямо на улице и смотрит на тебя.\n\n"
                "🎉 <b>Поздравляю — ты прошёл экскурсию «Сердце Москвы»!</b>\n\n"
                "Три места, три картины Манушина, шестьсот лет московской истории — всё это теперь немного твоё. "
                "Надеемся, ты смотришь на этот город чуть иначе, чем час назад 🎨\n\n"
                "Возвращайся в главное меню — там ждут ещё три экскурсии 👇"
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
