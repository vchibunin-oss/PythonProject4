import requests
import time
import math
import json
import os

# ============================================================
# КОНФИГУРАЦИЯ — вынеси в .env файл для безопасности
# ============================================================
BOT_TOKEN = "8774291467:AAHjf286TTxqI0vJMvbrPgOesNGeMz4QD2I"
ADMIN_CHAT_ID = "-5456746235"
CRYPTO_PAY_TOKEN = "600156:AARtempRLQZhvxHR3EdZiSDhAxW9D52Yp3L"

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
CRYPTO_API_URL = "https://pay.crypt.bot/api"

# ============================================================
# ПРАЙС-ЛИСТ
# ============================================================
PRICE_LIST = {
    "📸 Instagram": {
        "❤️ Лайки стандарт": 49,
        "🚀 Лайки турбо": 99,
        "⚡ Лайки супер турбо": 178,
        "👀 Просмотры": 49,
        "📊 Просмотры с охватом": 69,
        "📈 Просмотры со статистикой": 89,
        "💬 Комментарии эмоджи": 1299,
        "🇷🇺 Комментарии RU": 1799,
        "🎯 Комментарии RU по теме": 8888,
        "📢 Показы / охваты": 49,
        "🔄 Репост + статистика": 99,
        "👥 Подписчики": 99,
        "⚡ Подписчики быстрые": 149,
        "📖 Просмотры сторис": 49,
    },
    "🟦 VK": {
        "❤️ Лайки": 99,
        "⚡ Лайки быстрые": 199,
        "👤 Лайки живые": 599,
        "👀 Просмотры": 49,
        "📄 Просмотры постов": 59,
        "🎥 Просмотры видео": 49,
        "🎬 Просмотры видео / клипов": 69,
        "🐢 Подписчики медленные": 111,
        "👥 Подписчики живые": 1699,
    },
    "📱 Telegram": {
        "👥 Подписчики": 159,
        "🇷🇺 Подписчики RU": 199,
        "👤 Подписчики RU живые": 5799,
        "👍 Реакции положительные": 39,
        "👀 Просмотры": 29,
        "📊 Просмотры RU со статистикой": 49,
    },
    "▶️ YouTube": {
        "❤️ Лайки": 199,
        "🚀 Лайки турбо": 499,
        "👍 Лайк на комментарий": 59,
        "👀 Просмотры": 200,
        "⚡ Просмотры быстрые": 269,
        "🐢 Подписчики медленные": 2999,
        "👥 Подписчики стандарт": 4999,
    },
}


MIN_QTY = 100
MAX_QTY = 1_000_000

# ============================================================
# СОСТОЯНИЕ
# ============================================================
users = {}
last_update_id = 0
order_id = 1000

# ============================================================
# КЛАВИАТУРЫ
# ============================================================
def make_keyboard(buttons):
    return {"keyboard": buttons, "resize_keyboard": True}


main_keyboard = make_keyboard([["🚀 Старт"]])

social_keyboard = make_keyboard([
    ["📱 Telegram", "📸 Instagram"],
    ["🟦 VK", "▶️ YouTube"],
])

back_keyboard = make_keyboard([["⬅️ Назад"]])

payment_keyboard = make_keyboard([
    ["💳 Карта РФ", "₮ USDT"],
    ["❌ Отмена"],
])




def services_keyboard(social):
    services = list(PRICE_LIST[social].keys())
    rows = [services[i:i + 2] for i in range(0, len(services), 2)]
    rows.append(["⬅️ Назад"])
    return make_keyboard(rows)


# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================
def calculate_price(qty, price_per_1000):
    return math.ceil((qty / 1000) * price_per_1000)


def send_message(chat_id, text, keyboard=None):
    data = {"chat_id": chat_id, "text": text}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    try:
        requests.post(f"{API_URL}/sendMessage", json=data, timeout=10)
    except Exception as e:
        print(f"Ошибка send_message: {e}")


def send_photo(chat_id, photo_path, keyboard=None):
    data = {"chat_id": chat_id}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    try:
        if os.path.exists(photo_path):
            with open(photo_path, "rb") as photo:
                requests.post(f"{API_URL}/sendPhoto", data=data, files={"photo": photo}, timeout=10)
        else:
            # Если фото нет — просто показываем главное меню текстом
            send_message(chat_id, "👋 Выберите социальную сеть:", keyboard)
    except Exception as e:
        print(f"Ошибка send_photo: {e}")
        send_message(chat_id, "👋 Выберите социальную сеть:", keyboard)


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


def create_crypto_invoice(amount_usd, description):
    headers = {"Crypto-Pay-API-Token": CRYPTO_PAY_TOKEN}
    data = {"asset": "USDT", "amount": str(amount_usd), "description": description}
    try:
        response = requests.post(
            f"{CRYPTO_API_URL}/createInvoice", headers=headers, json=data, timeout=10
        )
        return response.json()
    except Exception as e:
        print(f"Ошибка create_crypto_invoice: {e}")
        return {"ok": False}


def check_crypto_invoice(invoice_id):
    headers = {"Crypto-Pay-API-Token": CRYPTO_PAY_TOKEN}
    params = {"invoice_ids": str(invoice_id)}
    try:
        response = requests.get(
            f"{CRYPTO_API_URL}/getInvoices", headers=headers, params=params, timeout=10
        )
        return response.json()
    except Exception as e:
        print(f"Ошибка check_crypto_invoice: {e}")
        return {"ok": False}


# ============================================================
# ОБРАБОТКА СООБЩЕНИЙ
# ============================================================
def send_start(chat_id):
    send_photo(chat_id, "promo.jpg", social_keyboard)


def handle_message(chat_id, text):
    global order_id
    print(repr(text))
    user = users.get(chat_id, {})
    step = user.get("step")

    # --- Отмена / старт ---
    if text in ("/start", "🚀 Старт", "❌ Отмена"):
        users.pop(chat_id, None)
        send_start(chat_id)
        return

        # --- Назад ---
        if text == "⬅️ Назад":
            if step == "service":
                users.pop(chat_id, None)
                send_start(chat_id)
            elif step == "quantity":
                social = user.get("social")
                users[chat_id]["step"] = "service"
                send_message(chat_id, f"Выберите услугу:", services_keyboard(social))
            elif step == "link":
                social = user.get("social")
                users[chat_id]["step"] = "quantity"
                send_message(chat_id, "Введите количество от 100 до 1 000 000:")
            elif step == "payment":
                users[chat_id]["step"] = "link"
                send_message(chat_id, "Отправьте ссылку:", back_keyboard)
            else:
                users.pop(chat_id, None)
                send_start(chat_id)
            return

    # --- Команда админа: ГОТОВО <chat_id> ---
    if text.lower().startswith("готово "):
        client_id = text.lower().replace("готово", "", 1).strip()
        if client_id.isdigit():
            try:
                send_message(int(client_id), "✅ Ваш заказ выполнен.\n\nСпасибо за обращение!")
                send_message(chat_id, "✅ Клиенту отправлено сообщение.")
            except Exception as e:
                print(f"Ошибка отправки клиенту: {e}")
                send_message(chat_id, "❌ Не удалось отправить клиенту сообщение.")
        return

    # --- Выбор соцсети ---
    if text in PRICE_LIST:
        users[chat_id] = {"social": text, "step": "service"}
        send_message(
            chat_id,
            f"Вы выбрали {text}\n\nТеперь выберите услугу:",
            services_keyboard(text),
        )
        return

    # --- Выбор услуги ---
    # Берём соцсеть из состояния пользователя, чтобы не перепутать одинаковые
    # названия услуг в разных соцсетях (например "Просмотры" есть везде)
    if step == "service":
        social = user.get("social")
        if social and text in PRICE_LIST.get(social, {}):
            price = PRICE_LIST[social][text]
            users[chat_id] = {
                "social": social,
                "service": text,
                "price": price,
                "step": "quantity",
            }
            send_message(
                chat_id,
                f"Вы выбрали:\n\n{text}\n\n💰 Цена: {price} ₽ за 1000\n\nВведите количество от {MIN_QTY} до {MAX_QTY:,}:",
            )
            return

    # --- Ввод количества ---
    if step == "quantity":
        if not text.isdigit():
            send_message(chat_id, "⚠️ Введите количество цифрами, например: 1000")
            return

        qty = int(text)
        if qty < MIN_QTY or qty > MAX_QTY:
            send_message(chat_id, f"⚠️ Количество должно быть от {MIN_QTY} до {MAX_QTY:,}")
            return

        order_id += 1
        users[chat_id]["quantity"] = qty
        users[chat_id]["order_id"] = order_id
        users[chat_id]["step"] = "link"

        send_message(
            chat_id,
            f"✅ Заказ #{order_id}\n\n"
            f"Услуга: {user['service']}\n"
            f"Количество: {qty:,}\n\n"
            f"Отправьте ссылку:\n\n"
            f"⚠️ Проверьте, что ссылка скопирована правильно.\n"
            f"Профиль/пост/канал должен быть открыт для просмотра.\n\n"
            f"За неправильно отправленную ссылку ответственность несёт клиент.",
            keyboard=back_keyboard,
        )
        return

    # --- Ввод ссылки ---
    if step == "link":
        users[chat_id]["link"] = text
        users[chat_id]["step"] = "payment"

        total_price = calculate_price(user["quantity"], user["price"])

        send_message(
            chat_id,
            f"✅ Заказ оформлен\n\n"
            f"Соцсеть: {user['social']}\n"
            f"Услуга: {user['service']}\n"
            f"Количество: {user['quantity']:,}\n"
            f"Ссылка: {text}\n"
            f"Сумма: {total_price} ₽\n\n"
            f"Выберите способ оплаты:",
            keyboard=payment_keyboard,
        )
        return

    # --- Выбор способа оплаты ---
    if step == "payment":
        if text == "₮ USDT":
            total_rub = calculate_price(user["quantity"], user["price"])
            amount_usd = round(total_rub / 80, 2)  # TODO: заменить на реальный курс API

            invoice = create_crypto_invoice(amount_usd, f"Заказ от {chat_id}")
            if not invoice.get("ok"):
                send_message(chat_id, f"❌ Не удалось создать счёт. Попробуйте позже.")
                return

            pay_url = invoice["result"]["pay_url"]
            users[chat_id]["invoice_id"] = invoice["result"]["invoice_id"]
            users[chat_id]["amount_usd"] = amount_usd
            users[chat_id]["step"] = "wait_payment"

            send_message(
                chat_id,
                f"₮ Оплата USDT\n\n"
                f"💰 Сумма: {amount_usd} USDT\n\n"
                f"🔗 Ссылка на оплату:\n{pay_url}\n\n"
                f"После оплаты деньги будут зачислены автоматически.",
            )
            return

        if text == "💳 Карта РФ":
            total_price = calculate_price(user["quantity"], user["price"])
            send_message(
                chat_id,
                f"💳 Оплата картой\n\n"
                f"Номер карты:\nВСТАВЬ_СВОЙ_НОМЕР_КАРТЫ\n\n"
                f"Сумма к оплате: {total_price} ₽\n\n"
                f"После перевода администратор проверит оплату и выполнит заказ.",
                keyboard=main_keyboard,
            )
            send_message(
                ADMIN_CHAT_ID,
                f"🔔 Новый заказ (оплата картой)\n\n"
                f"Соцсеть: {user['social']}\n"
                f"Услуга: {user['service']}\n"
                f"Количество: {user['quantity']:,}\n"
                f"Ссылка: {user['link']}\n"
                f"Сумма: {total_price} ₽\n\n"
                f"Пользователь: {chat_id}\n\n"
                f"Чтобы отметить выполненным: готово {chat_id}",
            )
            users.pop(chat_id, None)
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
        if not items:
            continue

        status = items[0]["status"]
        if status == "paid":
            total_price = calculate_price(user["quantity"], user["price"])
            send_message(
                ADMIN_CHAT_ID,
                f"✅ НОВЫЙ ОПЛАЧЕННЫЙ ЗАКАЗ\n\n"
                f"🌐 Соцсеть: {user['social']}\n"
                f"📦 Услуга: {user['service']}\n"
                f"🔢 Количество: {user['quantity']:,}\n"
                f"🔗 Ссылка: {user['link']}\n"
                f"💰 Сумма: {total_price} ₽ ({user['amount_usd']} USDT)\n"
                f"👤 Пользователь: {user_id}\n\n"
                f"✅ Статус: Оплачено\n\n"
                f"Чтобы отметить выполненным: готово {user_id}",
            )
            send_message(
                user_id,
                "✅ Оплата получена! Ваш заказ принят в работу.\n\nМы уведомим вас о выполнении.",
                keyboard=main_keyboard,
            )
            users.pop(user_id, None)


# ============================================================
# ГЛАВНЫЙ ЦИКЛ
# ============================================================
print("Бот запущен...", flush=True)

while True:
    # 1. Проверяем USDT-платежи
    check_pending_payments()

    # 2. Получаем новые сообщения
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

        if not text:
            continue

        print(f"[{chat_id}] {text}", flush=True)

        try:
            handle_message(chat_id, text)
        except Exception as e:
            print(f"Ошибка обработки сообщения от {chat_id}: {e}")
            send_message(chat_id, "❌ Произошла ошибка. Попробуйте ещё раз или нажмите /start")