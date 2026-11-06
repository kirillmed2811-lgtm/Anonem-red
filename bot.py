import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ChatMemberUpdated

# Настройки из Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID", "0"))
# Секретный пароль (берем из переменной или ставим дефолтный)
SECRET_PASSWORD = os.getenv("BOT_PASSWORD", "кузбас28рищван3чечня;")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

messages_map = {}
authorized_users = set() # Здесь храним тех, кто ввел пароль
authorized_groups = set() # Здесь храним ID групп, которые ввели пароль

# --- 1. ПРОВЕРКА ПАРОЛЯ ПРИ ДОБАВЛЕНИИ В ГРУППУ ---
@dp.my_chat_member()
async def bot_added_to_group(event: ChatMemberUpdated):
    if event.chat.type in ["group", "supergroup"]:
        if event.new_chat_member.status == "member":
            await bot.send_message(
                event.chat.id, 
                "🛡 <b>Система защиты!</b>\nЧтобы активировать бота, напишите команду:\n<code>/auth ВАШ_ПАРОЛЬ</code>",
                parse_mode="HTML"
            )

# --- 2. КОМАНДА АВТОРИЗАЦИИ ---
@dp.message(Command("auth"))
async def cmd_auth(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.answer("Напиши пароль после команды: /auth твой_пароль")
    
    password = args[1].strip()
    
    if password == SECRET_PASSWORD:
        if message.chat.type == "private":
            authorized_users.add(message.from_user.id)
            await message.answer("✅ Пароль верный! Доступ разрешен. Теперь ты можешь писать анонимно.")
        else:
            authorized_groups.add(message.chat.id)
            await message.answer("✅ Группа авторизована! Теперь сюда будут приходить сообщения.")
    else:
        await message.answer("❌ Неверный пароль. Попробуй еще раз.")

# --- 3. СТАРТ БОТА ---
@dp.message(CommandStart())
async def cmd_start(message: Message):
    if message.chat.type != "private": return
    
    if message.from_user.id not in authorized_users:
        await message.answer(
            "🛑 <b>Это закрытый бот.</b>\n"
            "Для доступа отправь команду: <code>/auth твой_пароль</code>",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            "Привет, шедевролицеист! 👋\n"
            "Ты в системе Аноним Ред. Напиши свой вопрос, и я передам его анонимно.",
            parse_mode="HTML"
        )

# --- 4. ОБРАБОТКА ЛИЦЕИСТОВ (только если авторизован) ---
@dp.message(F.chat.type == "private")
async def handle_user_messages(message: Message):
    # Если человек не ввел пароль — не пускаем дальше
    if message.from_user.id not in authorized_users:
        return await message.answer("Сначала введи пароль: /auth твой_пароль")

    try:
        sent_msg = await bot.copy_message(
            chat_id=GROUP_ID, 
            from_chat_id=message.chat.id, 
            message_id=message.message_id
        )
        messages_map[sent_msg.message_id] = message.from_user.id
        await message.answer("Твоё сообщение улетело к магистроадминам! 🚀")
    except Exception as e:
        print(f"Ошибка: {e}")
        await message.answer("Ошибка отправки. Админы еще не настроили группу.")

# --- 5. ОБРАБОТКА ОТВЕТОВ В ГРУППЕ ---
@dp.message(F.chat.id == GROUP_ID)
async def handle_admin_replies(message: Message):
    if message.reply_to_message:
        original_msg_id = message.reply_to_message.message_id
        if original_msg_id in messages_map:
            target_user_id = messages_map[original_msg_id]
            try:
                await bot.copy_message(
                    chat_id=target_user_id,
                    from_chat_id=GROUP_ID,
                    message_id=message.message_id
                )
                await message.answer("Ответ отправлен лицеисту! ✅")
            except Exception as e:
                await message.answer(f"Не удалось отправить ответ: {e}")

async def main():
    print("Аноним Ред (с паролем) запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
