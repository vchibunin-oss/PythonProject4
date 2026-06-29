import requests
import time
import math
import json
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
CRYPTO_PAY_TOKEN = os.getenv("CRYPTO_PAY_TOKEN")

if not BOT_TOKEN or not ADMIN_CHAT_ID or not CRYPTO_PAY_TOKEN:
    raise ValueError("Не заполнены токены в .env файле!")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
CRYPTO_API_URL = "https://pay.crypt.bot/api"

# ============================================================
# ADMIN ID — вставь свой Telegram ID (узнать: написать @userinfobot)
# ============================================================
ADMIN_ID = 8392767443

# ============================================================
# СТАТИСТИКА — хранится в файле stats.json
# ============================================================
import datetime

STATS_FILE = "stats.json"

def load_stats():
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "users": {},        # chat_id: {first_seen, source}
            "orders": [],       # список всех заказов
            "paid_orders": [],  # оплаченные заказы
        }

def save_stats(stats):
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения stats: {e}")

def track_user(chat_id, source="organic"):
    """Регистрируем нового пользователя с источником"""
    stats = load_stats()
    uid = str(chat_id)
    if uid not in stats["users"]:
        stats["users"][uid] = {
            "first_seen": datetime.datetime.now().isoformat(),
            "source": source,
        }
        save_stats(stats)

def track_order_start(chat_id, social, service):
    """Фиксируем начало заказа"""
    stats = load_stats()
    uid = str(chat_id)
    source = stats["users"].get(uid, {}).get("source", "organic")
    stats["orders"].append({
        "chat_id": chat_id,
        "social": social,
        "service": service,
        "source": source,
        "date": datetime.datetime.now().isoformat(),
        "status": "started",
    })
    save_stats(stats)

def track_payment_start(chat_id):
    """Фиксируем переход к оплате"""
    stats = load_stats()
    for order in reversed(stats["orders"]):
        if order["chat_id"] == chat_id and order["status"] == "started":
            order["status"] = "payment"
            break
    save_stats(stats)

def track_paid(chat_id, social, service, quantity, link, amount_rub, source):
    """Фиксируем успешную оплату"""
    stats = load_stats()
    stats["paid_orders"].append({
        "chat_id": chat_id,
        "social": social,
        "service": service,
        "quantity": quantity,
        "link": link,
        "amount": amount_rub,
        "source": source,
        "date": datetime.datetime.now().isoformat(),
    })
    # Обновляем статус в orders
    for order in reversed(stats["orders"]):
        if order["chat_id"] == chat_id and order["status"] == "payment":
            order["status"] = "paid"
            order["amount"] = amount_rub
            break
    save_stats(stats)

def get_stats_report():
    """Формируем отчёт статистики"""
    stats = load_stats()
    now = datetime.datetime.now()
    today = now.date().isoformat()
    week_ago = (now - datetime.timedelta(days=7)).isoformat()
    month_ago = (now - datetime.timedelta(days=30)).isoformat()

    users = stats["users"]
    orders = stats["orders"]
    paid = stats["paid_orders"]

    total_users = len(users)
    new_today = sum(1 for u in users.values() if u["first_seen"][:10] == today)
    new_week = sum(1 for u in users.values() if u["first_seen"] >= week_ago)
    new_month = sum(1 for u in users.values() if u["first_seen"] >= month_ago)

    total_orders = len(orders)
    to_payment = sum(1 for o in orders if o["status"] in ("payment", "paid"))
    total_paid = len(paid)
    total_sum = sum(o.get("amount", 0) for o in paid)
    avg_check = round(total_sum / total_paid) if total_paid else 0

    # Популярная услуга
    from collections import Counter
    service_counter = Counter(o["service"] for o in paid)
    top_service = service_counter.most_common(1)[0][0] if service_counter else "—"

    # Источники трафика
    sources = {}
    for uid, u in users.items():
        src = u.get("source", "organic")
        if src not in sources:
            sources[src] = {"users": 0, "orders": 0, "paid": 0, "sum": 0}
        sources[src]["users"] += 1

    for o in orders:
        src = o.get("source", "organic")
        if src not in sources:
            sources[src] = {"users": 0, "orders": 0, "paid": 0, "sum": 0}
        sources[src]["orders"] += 1

    for o in paid:
        src = o.get("source", "organic")
        if src not in sources:
            sources[src] = {"users": 0, "orders": 0, "paid": 0, "sum": 0}
        sources[src]["paid"] += 1
        sources[src]["sum"] += o.get("amount", 0)

    sources_text = ""
    for src, data in sorted(sources.items(), key=lambda x: x[1]["users"], reverse=True):
        line = "  " + src + " — " + str(data["users"]) + " польз. / " + str(data["orders"]) + " заказов / " + str(data["paid"]) + " оплат / " + str(data["sum"]) + " ₽"
        sources_text += line + chr(10)

    # Последние 10 оплат
    last_paid = paid[-10:][::-1]
    last_text = ""
    for o in last_paid:
        line = "  " + o["social"] + " / " + o["service"] + " / " + str(o["quantity"]) + " / " + str(o["amount"]) + " ₽ / " + o.get("source", "organic")
        last_text += line + chr(10)

    report = (
        "📊 Статистика бота" + chr(10) + chr(10) +
        "👥 Всего пользователей: " + str(total_users) + chr(10) +
        "🆕 Новых сегодня: " + str(new_today) + chr(10) +
        "📅 За 7 дней: " + str(new_week) + chr(10) +
        "📆 За 30 дней: " + str(new_month) + chr(10) + chr(10) +
        "🛒 Всего заказов: " + str(total_orders) + chr(10) +
        "💳 Перешли к оплате: " + str(to_payment) + chr(10) +
        "✅ Оплаченных заказов: " + str(total_paid) + chr(10) +
        "💰 Общая сумма: " + str(total_sum) + " ₽" + chr(10) +
        "💵 Средний чек: " + str(avg_check) + " ₽" + chr(10) +
        "🔥 Популярная услуга: " + top_service + chr(10) + chr(10) +
        "📢 Источники трафика:" + chr(10) + sources_text + chr(10) +
        "🧾 Последние 10 оплат:" + chr(10) + last_text
    )
    return report

RECIPIENT_NAME = "Чибунин В.А."
SBER_CARD      = "2202 2080 5539 1073"
TINKOFF_CARD   = "2200 7010 9459 5540"
SBP_PHONE      = "+7 952 843 16 12"

# ============================================================
# ПЕРЕВОДЫ
# ============================================================
TEXTS = {
    "ru": {
        "choose_social":      "Выберите социальную сеть:",
        "choose_service":     "Вы выбрали {social}\n\nТеперь выберите услугу:",
        "service_menu":       "Выберите услугу из меню.",
        "enter_qty":          "Вы выбрали:\n\n{service}\n\n💰 Цена: {price} ₽ за 1000\n\nВведите количество от {mn} до {mx}:",
        "qty_not_digit":      "Введите количество цифрами, например: 1000",
        "qty_out_range":      "Количество должно быть от {mn} до {mx}",
        "enter_link":         "✅ Заказ #{oid}\n\nУслуга: {service}\nКоличество: {qty}\n\nОтправьте ссылку:\n\n⚠️ Проверьте что ссылка скопирована правильно.\nПрофиль/пост/канал должен быть открыт.\n\nЗа неправильную ссылку ответственность несёт клиент.",
        "choose_payment":     "✅ Заказ оформлен\n\nСоцсеть: {social}\nУслуга: {service}\nКоличество: {qty}\nСсылка: {link}\nСумма: {price} ₽\n\nВыберите способ оплаты:",
        "payment_menu":       "Выберите способ оплаты из меню.",
        "usdt_pay":           "₮ Оплата USDT\n\n💰 Сумма: {amount} USDT\n\n🔗 Ссылка:\n{url}\n\nПосле оплаты средства зачислятся автоматически.",
        "ton_pay":            "💎 Оплата TON\n\n💰 Сумма: {amount} TON\n\n🔗 Ссылка:\n{url}\n\nПосле оплаты средства зачислятся автоматически.",
        "invoice_error":      "Не удалось создать счёт. Попробуйте позже.",
        "screenshot_prompt":  "Отправьте скриншот чека как фото.",
        "screenshot_ok":      "✅ Скриншот получен!\n\nАдминистратор проверит оплату.\nОбычно до 15 минут.",
        "order_done":         "✅ Ваш заказ принят в работу!\n\nЗаказ будет выполнен в течение 15 минут.\n\nНадеемся, вам всё понравится. Ждём вас снова! 😊",
        "order_rejected":     "❌ Оплата не прошла.\n\nПожалуйста, проверьте ваш счёт и попробуйте снова.\n\nЕсли вы уверены что оплатили — нажмите 🆘 Поддержка.",
        "crypto_paid":        "✅ Оплата получена! Ваш заказ принят в работу.\n\nМы уведомим вас о выполнении.",
        "sber":               "🟢 Оплата Сбербанк\n\n💳 Карта:\n<code>{card}</code>\n\n👤 Получатель: {name}\n💰 Сумма: {price} ₽\n\n📸 Отправьте скриншот чека.",
        "tinkoff":            "🟡 Оплата Тинькофф\n\n💳 Карта:\n<code>{card}</code>\n\n👤 Получатель: {name}\n💰 Сумма: {price} ₽\n\n📸 Отправьте скриншот чека.",
        "sbp":                "📱 Оплата через СБП\n\n📞 Телефон:\n<code>{phone}</code>\n\n🏦 Банки: Сбербанк / Т-Банк (Тинькофф)\n👤 Получатель: {name}\n💰 Сумма: {price} ₽\n\n📸 Отправьте скриншот чека.",
        "error":              "Произошла ошибка. Попробуйте ещё раз или нажмите /start",
        "support_prompt":     "📩 Опишите вашу проблему и мы свяжемся с вами:",
        "support_ok":         "✅ Ваше обращение принято! Ожидайте ответа. Обычно отвечаем в течение 15 минут.",
        "btn_support":        "🆘 Поддержка",
        "back":               "⬅️ Назад",
        "cancel":             "❌ Отмена",
        "start":              "🚀 Старт",
    },
    "en": {
        "choose_social":      "Choose a social network:",
        "choose_service":     "You chose {social}\n\nNow select a service:",
        "service_menu":       "Please choose a service from the menu.",
        "enter_qty":          "You selected:\n\n{service}\n\n💰 Price: {price} ₽ per 1000\n\nEnter quantity from {mn} to {mx}:",
        "qty_not_digit":      "Please enter a number, e.g.: 1000",
        "qty_out_range":      "Quantity must be between {mn} and {mx}",
        "enter_link":         "✅ Order #{oid}\n\nService: {service}\nQuantity: {qty}\n\nSend the link:\n\n⚠️ Make sure the link is correct.\nThe profile/post/channel must be public.\n\nThe client is responsible for incorrect links.",
        "choose_payment":     "✅ Order placed\n\nNetwork: {social}\nService: {service}\nQuantity: {qty}\nLink: {link}\nTotal: {price} ₽\n\nChoose payment method:",
        "payment_menu":       "Please choose a payment method from the menu.",
        "usdt_pay":           "₮ USDT Payment\n\n💰 Amount: {amount} USDT\n\n🔗 Link:\n{url}\n\nFunds will be credited automatically after payment.",
        "ton_pay":            "💎 TON Payment\n\n💰 Amount: {amount} TON\n\n🔗 Link:\n{url}\n\nFunds will be credited automatically after payment.",
        "invoice_error":      "Failed to create invoice. Please try again later.",
        "screenshot_prompt":  "Please send a screenshot of your receipt as a photo.",
        "screenshot_ok":      "✅ Screenshot received!\n\nThe admin will verify your payment.\nUsually within 15 minutes.",
        "order_done":         "✅ Your order is in progress!\n\nIt will be completed within 15 minutes.\n\nWe hope you enjoy it. See you again! 😊",
        "order_rejected":     "❌ Payment failed.\n\nPlease check your balance and try again.\n\nIf you are sure you paid — press 🆘 Support.",
        "crypto_paid":        "✅ Payment received! Your order is now in progress.\n\nWe will notify you upon completion.",
        "sber":               "🟢 Sberbank Payment\n\n💳 Card:\n<code>{card}</code>\n\n👤 Recipient: {name}\n💰 Amount: {price} ₽\n\n📸 Send a screenshot after payment.",
        "tinkoff":            "🟡 Tinkoff Payment\n\n💳 Card:\n<code>{card}</code>\n\n👤 Recipient: {name}\n💰 Amount: {price} ₽\n\n📸 Send a screenshot after payment.",
        "sbp":                "📱 SBP Payment\n\n📞 Phone:\n<code>{phone}</code>\n\n🏦 Banks: Sberbank / T-Bank (Tinkoff)\n👤 Recipient: {name}\n💰 Amount: {price} ₽\n\n📸 Send a screenshot after payment.",
        "error":              "An error occurred. Please try again or press /start",
        "support_prompt":     "📩 Describe your issue and we will get back to you:",
        "support_ok":         "✅ Your request has been received! Please wait. We usually reply within 15 minutes.",
        "btn_support":        "🆘 Support",
        "back":               "⬅️ Back",
        "cancel":             "❌ Cancel",
        "start":              "🚀 Start",
    }
}

def lang(chat_id):
    return users.get(chat_id, {}).get("lang", "ru")

def t(chat_id, key, **kw):
    text = TEXTS.get(lang(chat_id), TEXTS["ru"]).get(key, key)
    return text.format(**kw) if kw else text

def detect_lang(update):
    lc = update.get("message", {}).get("from", {}).get("language_code", "ru")
    return "en" if lc and lc.startswith("en") else "ru"

# ============================================================
# ПРАЙС-ЛИСТ
# ============================================================
PRICE_LIST = {
    "📸 Instagram": {
        "❤️ Лайки стандарт": 49, "🚀 Лайки турбо": 99, "⚡ Лайки супер турбо": 178,
        "👀 Просмотры": 49, "📊 Просмотры с охватом": 69, "📈 Просмотры со статистикой": 89,
        "💬 Комментарии эмоджи": 1299, "🇷🇺 Комментарии RU": 1799, "🎯 Комментарии RU по теме": 8888,
        "📢 Показы / охваты": 49, "🔄 Репост + статистика": 99,
        "👥 Подписчики": 99, "⚡ Подписчики быстрые": 149, "📖 Просмотры сторис": 49,
    },
    "🟦 VK": {
        "❤️ Лайки": 99, "⚡ Лайки быстрые": 199, "👤 Лайки живые": 599,
        "👀 Просмотры": 49, "📄 Просмотры постов": 59,
        "🎥 Просмотры видео": 49, "🎬 Просмотры видео / клипов": 69,
        "🐢 Подписчики медленные": 111, "👥 Подписчики живые": 1699,
    },
    "📱 Telegram": {
        "👥 Подписчики": 159, "🇷🇺 Подписчики RU": 199, "👤 Подписчики RU живые": 5799,
        "👍 Реакции положительные": 39, "👀 Просмотры": 29, "📊 Просмотры RU со статистикой": 49,
    },
    "▶️ YouTube": {
        "❤️ Лайки": 199, "🚀 Лайки турбо": 499, "👍 Лайк на комментарий": 59,
        "👀 Просмотры": 200, "⚡ Просмотры быстрые": 269,
        "🐢 Подписчики медленные": 2999, "👥 Подписчики стандарт": 4999,
    },
}

MIN_QTY = 100
MAX_QTY = 1_000_000

# ============================================================
# СОСТОЯНИЕ
# ============================================================
users = {}
last_update_id = 0

def load_order_id():
    try:
        with open("order_id.txt") as f:
            return int(f.read().strip())
    except:
        return 1000

def save_order_id(oid):
    try:
        with open("order_id.txt", "w") as f:
            f.write(str(oid))
    except Exception as e:
        print(f"Ошибка сохранения order_id: {e}")

def save_users():
    try:
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in users.items()}, f, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка сохранения users: {e}")

def load_users():
    try:
        with open("users.json", "r", encoding="utf-8") as f:
            return {int(k): v for k, v in json.load(f).items()}
    except:
        return {}

order_id = load_order_id()
# Загружаем сохранённые состояния пользователей
_loaded = load_users()
if _loaded:
    users.update(_loaded)
    print(f"Загружено {len(_loaded)} пользователей из файла")

# ============================================================
# КЛАВИАТУРЫ
# ============================================================
def make_keyboard(buttons):
    return {"keyboard": buttons, "resize_keyboard": True}

def start_kb(chat_id):
    return make_keyboard([[t(chat_id, "start")]])

def back_kb(chat_id):
    return make_keyboard([[t(chat_id, "back")]])

def cancel_kb(chat_id):
    return make_keyboard([[t(chat_id, "cancel")]])

social_keyboard = make_keyboard([
    ["📱 Telegram", "📸 Instagram"],
    ["🟦 VK", "▶️ YouTube"],
    ["🆘 Поддержка / Support"],
])

def payment_kb(chat_id):
    return make_keyboard([
        ["🟢 Сбербанк", "🟡 Тинькофф"],
        ["📱 СБП", "₮ USDT"],
        ["💎 TON"],
        [t(chat_id, "back"), t(chat_id, "cancel")],
    ])

def services_kb(chat_id, social):
    services = list(PRICE_LIST[social].keys())
    rows = [services[i:i+2] for i in range(0, len(services), 2)]
    rows.append([t(chat_id, "back")])
    return make_keyboard(rows)

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================
def calculate_price(qty, price_per_1000):
    return math.ceil((qty / 1000) * price_per_1000)

def send_inline_keyboard(chat_id, text, client_id):
    """Отправляет сообщение с inline кнопками Выполнен / Отклонить"""
    keyboard = {
        "inline_keyboard": [[
            {"text": "✅ Выполнен", "callback_data": f"done_{client_id}"},
            {"text": "❌ Отклонить", "callback_data": f"reject_{client_id}"},
        ]]
    }
    data = {"chat_id": chat_id, "text": text, "reply_markup": json.dumps(keyboard)}
    try:
        requests.post(f"{API_URL}/sendMessage", json=data, timeout=10)
    except Exception as e:
        print(f"Ошибка send_inline_keyboard: {e}")

def answer_callback(callback_query_id, text):
    """Отвечаем на нажатие кнопки чтобы убрать загрузку"""
    try:
        requests.post(f"{API_URL}/answerCallbackQuery", json={
            "callback_query_id": callback_query_id,
            "text": text,
        }, timeout=10)
    except Exception as e:
        print(f"Ошибка answer_callback: {e}")

def edit_message_text(chat_id, message_id, text):
    """Редактируем сообщение после нажатия кнопки"""
    try:
        requests.post(f"{API_URL}/editMessageText", json={
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
        }, timeout=10)
    except Exception as e:
        print(f"Ошибка edit_message_text: {e}")

def send_message(chat_id, text, keyboard=None, parse_mode=None):
    data = {"chat_id": chat_id, "text": text}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    if parse_mode:
        data["parse_mode"] = parse_mode
    try:
        requests.post(f"{API_URL}/sendMessage", json=data, timeout=10)
    except Exception as e:
        print(f"Ошибка send_message: {e}")

def forward_message(to_chat_id, from_chat_id, message_id):
    try:
        requests.post(f"{API_URL}/forwardMessage", json={
            "chat_id": to_chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id,
        }, timeout=10)
    except Exception as e:
        print(f"Ошибка forward_message: {e}")

def send_photo_file(chat_id, photo_path, keyboard=None):
    data = {"chat_id": chat_id}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    try:
        if os.path.exists(photo_path):
            with open(photo_path, "rb") as photo:
                requests.post(f"{API_URL}/sendPhoto", data=data, files={"photo": photo}, timeout=10)
        else:
            send_message(chat_id, t(chat_id, "choose_social"), keyboard)
    except Exception as e:
        print(f"Ошибка send_photo_file: {e}")
        send_message(chat_id, t(chat_id, "choose_social"), keyboard)

def get_updates(offset=0):
    try:
        response = requests.get(
            f"{API_URL}/getUpdates",
            params={"offset": offset, "timeout": 30},
            timeout=35,
        )
        return response.json()
    except Exception as e:
        print(f"Ошибка get_updates: {e}")
        return {"ok": False}

def create_crypto_invoice(amount, asset, description):
    headers = {"Crypto-Pay-API-Token": CRYPTO_PAY_TOKEN}
    try:
        r = requests.post(f"{CRYPTO_API_URL}/createInvoice", headers=headers,
                          json={"asset": asset, "amount": str(amount), "description": description}, timeout=10)
        return r.json()
    except Exception as e:
        print(f"Ошибка create_crypto_invoice: {e}")
        return {"ok": False}

def check_crypto_invoice(invoice_id):
    headers = {"Crypto-Pay-API-Token": CRYPTO_PAY_TOKEN}
    try:
        r = requests.get(f"{CRYPTO_API_URL}/getInvoices", headers=headers,
                         params={"invoice_ids": str(invoice_id)}, timeout=10)
        return r.json()
    except Exception as e:
        print(f"Ошибка check_crypto_invoice: {e}")
        return {"ok": False}

# ============================================================
# СТАРТОВОЕ МЕНЮ
# ============================================================
def send_start(chat_id):
    saved_lang = users.get(chat_id, {}).get("lang", "ru")
    users[chat_id] = {"lang": saved_lang}
    send_photo_file(chat_id, "promo.jpg", social_keyboard)

# ============================================================
# РЕКВИЗИТЫ БАНКА
# ============================================================
def send_bank_details(chat_id, bank, total_price):
    if bank == "sber":
        text = t(chat_id, "sber", card=SBER_CARD, name=RECIPIENT_NAME, price=total_price)
    elif bank == "tinkoff":
        text = t(chat_id, "tinkoff", card=TINKOFF_CARD, name=RECIPIENT_NAME, price=total_price)
    elif bank == "sbp":
        text = t(chat_id, "sbp", phone=SBP_PHONE, name=RECIPIENT_NAME, price=total_price)
    send_message(chat_id, text, cancel_kb(chat_id), parse_mode="HTML")

# ============================================================
# ОБРАБОТКА СООБЩЕНИЙ
# ============================================================
def handle_message(chat_id, update):
    global order_id

    message = update.get("message", {})
    text = message.get("text", "")
    photo = message.get("photo")
    message_id = message.get("message_id")

    # Определяем язык клиента и сохраняем username
    detected = detect_lang(update)
    username = message.get("from", {}).get("username", "")
    if chat_id not in users:
        users[chat_id] = {"lang": detected}
    elif "lang" not in users[chat_id]:
        users[chat_id]["lang"] = detected
    if username:
        users[chat_id]["username"] = username

    user = users.get(chat_id, {})
    step = user.get("step")
    lg = lang(chat_id)

    print(f"[{chat_id}] lang={lg} step={step} text={repr(text)}", flush=True)

    # ----------------------------------------------------------
    # СТАРТ / ОТМЕНА
    # ----------------------------------------------------------
    if text in ("🚀 Старт", "🚀 Start", "❌ Отмена", "❌ Cancel"):
        track_user(chat_id)
        send_start(chat_id)
        return

    if text.startswith("/start"):
        parts = text.strip().split()
        source = parts[1] if len(parts) > 1 else "organic"
        track_user(chat_id, source)
        send_start(chat_id)
        return

    # ----------------------------------------------------------
    # СТАТИСТИКА (скрытая)
    # ----------------------------------------------------------
    if text == "/stats":
        # Только для админа в личке
        if chat_id == ADMIN_ID:
            send_message(chat_id, get_stats_report())
        return

    if text.lower() == "статистика бота":
        # Только в группе заказов и только от админа
        msg_chat_id = str(message.get("chat", {}).get("id", ""))
        sender_id = message.get("from", {}).get("id", 0)
        if msg_chat_id == str(ADMIN_CHAT_ID) and sender_id == ADMIN_ID:
            send_message(ADMIN_CHAT_ID, get_stats_report())
        return

    # ----------------------------------------------------------
    # КНОПКА НАЗАД
    # ----------------------------------------------------------
    if text in ("⬅️ Назад", "⬅️ Back"):
        if step == "service":
            send_start(chat_id)
        elif step == "quantity":
            social = user.get("social")
            users[chat_id] = {"lang": lg, "social": social, "step": "service"}
            send_message(chat_id, t(chat_id, "choose_service", social=social), services_kb(chat_id, social))
        elif step == "link":
            users[chat_id]["step"] = "quantity"
            send_message(chat_id, t(chat_id, "enter_qty", service=user.get("service",""), price=user.get("price",""), mn=MIN_QTY, mx=f"{MAX_QTY:,}"), back_kb(chat_id))
        elif step == "payment":
            users[chat_id]["step"] = "link"
            send_message(chat_id, "Отправьте ссылку:" if lg == "ru" else "Send the link:", back_kb(chat_id))
        else:
            send_start(chat_id)
        return

    # ----------------------------------------------------------
    # КОМАНДЫ АДМИНА
    # ----------------------------------------------------------
    if text.lower().startswith("готово") or text.lower().startswith("done"):
        parts = text.strip().split()
        if len(parts) > 1 and parts[1].isdigit():
            client_id = int(parts[1])
        else:
            waiting = [uid for uid, u in users.items() if u.get("step") in ("wait_confirm", "wait_payment")]
            client_id = waiting[0] if waiting else None

        if client_id:
            try:
                send_message(client_id, t(client_id, "order_done"), start_kb(client_id))
                send_message(chat_id, f"✅ Клиенту {client_id} отправлено уведомление.")
                users.pop(client_id, None)
            except Exception as e:
                print(f"Ошибка: {e}")
                send_message(chat_id, "❌ Не удалось отправить сообщение.")
        else:
            send_message(chat_id, "Нет ожидающих клиентов. Укажи ID: готово 123456789")
        return

    if text.lower().startswith("отклонить") or text.lower().startswith("reject"):
        parts = text.strip().split()
        client_id = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
        if client_id:
            try:
                send_message(client_id, t(client_id, "order_rejected"), start_kb(client_id))
                send_message(chat_id, f"❌ Клиенту {client_id} отправлено уведомление об отклонении.")
                users.pop(client_id, None)
            except Exception as e:
                print(f"Ошибка: {e}")
        return

    # ----------------------------------------------------------
    # ПОДДЕРЖКА
    # ----------------------------------------------------------
    if text in ("🆘 Поддержка / Support", "🆘 Поддержка", "🆘 Support"):
        users[chat_id]["step"] = "support"
        send_message(chat_id, t(chat_id, "support_prompt"), cancel_kb(chat_id))
        return

    if step == "support":
        # Отправляем обращение в группу
        client_username = users.get(chat_id, {}).get("username", "")
        client_link = f"@{client_username}" if client_username else f"ID: {chat_id} (username не указан)"
        admin_text = "📩 ОБРАЩЕНИЕ В ПОДДЕРЖКУ" + "\n\n" + f"👤 Клиент: {chat_id}" + "\n" + f"🔗 Клиент в Telegram: {client_link}" + "\n" + "✏️ Написать от себя: @Supervova01" + "\n\n" + f"💬 Сообщение:\n{text}"
        send_message(ADMIN_CHAT_ID, admin_text)
        send_message(chat_id, t(chat_id, "support_ok"), start_kb(chat_id))
        users[chat_id]["step"] = None
        return

    # ----------------------------------------------------------
    # ШАГ 1 — выбор соцсети
    # ----------------------------------------------------------
    if text in PRICE_LIST:
        users[chat_id]["social"] = text
        users[chat_id]["step"] = "service"
        send_message(chat_id, t(chat_id, "choose_service", social=text), services_kb(chat_id, text))
        return

    # ----------------------------------------------------------
    # ШАГ 2 — выбор услуги
    # ----------------------------------------------------------
    if step == "service":
        social = user.get("social")
        if social and text in PRICE_LIST.get(social, {}):
            price = PRICE_LIST[social][text]
            users[chat_id].update({"service": text, "price": price, "step": "quantity"})
            track_order_start(chat_id, users[chat_id].get("social", ""), text)
            send_message(chat_id, t(chat_id, "enter_qty", service=text, price=price, mn=MIN_QTY, mx=f"{MAX_QTY:,}"), back_kb(chat_id))
        else:
            send_message(chat_id, t(chat_id, "service_menu"))
        return

    # ----------------------------------------------------------
    # ШАГ 3 — ввод количества
    # ----------------------------------------------------------
    if step == "quantity":
        if not text.isdigit():
            send_message(chat_id, t(chat_id, "qty_not_digit"), back_kb(chat_id))
            return
        qty = int(text)
        if qty < MIN_QTY or qty > MAX_QTY:
            send_message(chat_id, t(chat_id, "qty_out_range", mn=MIN_QTY, mx=f"{MAX_QTY:,}"), back_kb(chat_id))
            return
        order_id += 1
        save_order_id(order_id)
        users[chat_id].update({"quantity": qty, "order_id": order_id, "step": "link"})
        send_message(chat_id, t(chat_id, "enter_link", oid=order_id, service=user["service"], qty=f"{qty:,}"), back_kb(chat_id))
        return

    # ----------------------------------------------------------
    # ШАГ 4 — ввод ссылки
    # ----------------------------------------------------------
    if step == "link":
        users[chat_id]["link"] = text
        users[chat_id]["step"] = "payment"
        total_price = calculate_price(user["quantity"], user["price"])
        track_payment_start(chat_id)
        send_message(chat_id, t(chat_id, "choose_payment", social=user["social"], service=user["service"],
                                qty=f"{user['quantity']:,}", link=text, price=total_price), payment_kb(chat_id))
        return

    # ----------------------------------------------------------
    # ШАГ 5 — выбор оплаты
    # ----------------------------------------------------------
    if step == "payment":
        total_price = calculate_price(user["quantity"], user["price"])

        if text == "🟢 Сбербанк":
            users[chat_id].update({"payment_method": "Сбербанк", "step": "wait_screenshot"})
            save_users()
            send_bank_details(chat_id, "sber", total_price)
            return

        if text == "🟡 Тинькофф":
            users[chat_id].update({"payment_method": "Тинькофф", "step": "wait_screenshot"})
            save_users()
            send_bank_details(chat_id, "tinkoff", total_price)
            return

        if text == "📱 СБП":
            users[chat_id].update({"payment_method": "СБП", "step": "wait_screenshot"})
            save_users()
            send_bank_details(chat_id, "sbp", total_price)
            return

        if text == "₮ USDT":
            amount = round(total_price / 80, 2)
            invoice = create_crypto_invoice(amount, "USDT", f"Order {chat_id}")
            if not invoice.get("ok"):
                send_message(chat_id, t(chat_id, "invoice_error"))
                return
            users[chat_id].update({"invoice_id": invoice["result"]["invoice_id"],
                                    "amount_crypto": amount, "payment_method": "USDT", "step": "wait_payment"})
            send_message(chat_id, t(chat_id, "usdt_pay", amount=amount, url=invoice["result"]["pay_url"]), cancel_kb(chat_id))
            return

        if text == "💎 TON":
            amount = round(total_price / 350, 2)
            invoice = create_crypto_invoice(amount, "TON", f"Order {chat_id}")
            if not invoice.get("ok"):
                send_message(chat_id, t(chat_id, "invoice_error"))
                return
            users[chat_id].update({"invoice_id": invoice["result"]["invoice_id"],
                                    "amount_crypto": amount, "payment_method": "TON", "step": "wait_payment"})
            send_message(chat_id, t(chat_id, "ton_pay", amount=amount, url=invoice["result"]["pay_url"]), cancel_kb(chat_id))
            return

        send_message(chat_id, t(chat_id, "payment_menu"))
        return

    # ----------------------------------------------------------
    # ШАГ 6 — ожидание скриншота
    # ----------------------------------------------------------
    if step == "wait_screenshot":
        if photo:
            total_price = calculate_price(user["quantity"], user["price"])
            forward_message(ADMIN_CHAT_ID, chat_id, message_id)
            send_inline_keyboard(
                ADMIN_CHAT_ID,
                f"🔔 НОВЫЙ ЗАКАЗ (проверь оплату)\n\n"
                f"🌐 Соцсеть: {user['social']}\n"
                f"📦 Услуга: {user['service']}\n"
                f"🔢 Количество: {user['quantity']:,}\n"
                f"🔗 Ссылка: {user['link']}\n"
                f"💰 Сумма: {total_price} ₽\n"
                f"💳 Способ: {user['payment_method']}\n\n"
                f"👤 ID клиента: {chat_id}",
                chat_id,
            )
            send_message(chat_id, t(chat_id, "screenshot_ok"), start_kb(chat_id))
            users[chat_id]["step"] = "wait_confirm"
            save_users()
        else:
            send_message(chat_id, t(chat_id, "screenshot_prompt"), cancel_kb(chat_id))
        return

# ============================================================
# ПРОВЕРКА КРИПТО-ПЛАТЕЖЕЙ
# ============================================================
def check_pending_payments():
    for user_id in list(users.keys()):
        user = users.get(user_id)
        if not user or user.get("step") != "wait_payment":
            continue
        invoice = check_crypto_invoice(user["invoice_id"])
        if not invoice.get("ok"):
            continue
        items = invoice.get("result", {}).get("items", [])
        if not items or items[0]["status"] != "paid":
            continue

        total_price = calculate_price(user["quantity"], user["price"])
        method = user.get("payment_method", "Крипта")
        amount = user.get("amount_crypto", "—")

        send_inline_keyboard(
            ADMIN_CHAT_ID,
            f"✅ НОВЫЙ ОПЛАЧЕННЫЙ ЗАКАЗ\n\n"
            f"🌐 Соцсеть: {user['social']}\n"
            f"📦 Услуга: {user['service']}\n"
            f"🔢 Количество: {user['quantity']:,}\n"
            f"🔗 Ссылка: {user['link']}\n"
            f"💰 Сумма: {total_price} ₽ ({amount} {method})\n\n"
            f"👤 ID клиента: {user_id}",
            user_id,
        )
        source = load_stats()["users"].get(str(user_id), {}).get("source", "organic")
        track_paid(user_id, user["social"], user["service"], user["quantity"], user["link"], total_price, source)
        send_message(user_id, t(user_id, "crypto_paid"), start_kb(user_id))
        users.pop(user_id, None)

# ============================================================
# ГЛАВНЫЙ ЦИКЛ
# ============================================================
print("✅ Бот запущен...", flush=True)

while True:
    check_pending_payments()

    updates = get_updates(offset=last_update_id + 1)
    if not updates.get("ok"):
        time.sleep(2)
        continue

    for update in updates["result"]:
        last_update_id = update["update_id"]
        if "message" not in update:
            continue

        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        photo = update["message"].get("photo")

        if not text and not photo:
            continue

        print(f"[{chat_id}] {repr(text)}", flush=True)

        try:
            handle_message(chat_id, update)
        except Exception as e:
            print(f"Ошибка от {chat_id}: {e}")
            send_message(chat_id, t(chat_id, "error"))

    # Обрабатываем нажатия inline кнопок
    for update in updates["result"]:
        if "callback_query" not in update:
            continue

        cb = update["callback_query"]
        cb_id = cb["id"]
        data = cb.get("data", "")
        msg_id = cb["message"]["message_id"]
        admin_chat = cb["message"]["chat"]["id"]

        if data.startswith("done_"):
            client_id = int(data.replace("done_", ""))
            try:
                # Фиксируем оплату при подтверждении скриншота
                u = users.get(client_id, {})
                if u.get("social") and u.get("service"):
                    total = calculate_price(u.get("quantity", 0), u.get("price", 0))
                    src = load_stats()["users"].get(str(client_id), {}).get("source", "organic")
                    track_paid(client_id, u["social"], u["service"], u.get("quantity", 0), u.get("link", ""), total, src)
                send_message(client_id, t(client_id, "order_done"), start_kb(client_id))
                edit_message_text(admin_chat, msg_id,
                    cb["message"]["text"] + "\n\n✅ ВЫПОЛНЕН")
                answer_callback(cb_id, "✅ Уведомление отправлено клиенту")
                users.pop(client_id, None)
            except Exception as e:
                print(f"Ошибка done callback: {e}")
                answer_callback(cb_id, "❌ Ошибка")

        elif data.startswith("reject_"):
            client_id = int(data.replace("reject_", ""))
            try:
                send_message(client_id, t(client_id, "order_rejected"), start_kb(client_id))
                edit_message_text(admin_chat, msg_id,
                    cb["message"]["text"] + "\n\n❌ ОТКЛОНЁН")
                answer_callback(cb_id, "❌ Клиент уведомлён об отклонении")
                users.pop(client_id, None)
            except Exception as e:
                print(f"Ошибка reject callback: {e}")
                answer_callback(cb_id, "❌ Ошибка")