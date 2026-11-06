import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

# Берем токен и ID админа из переменных окружения (настроек сервера Railway)
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Словарь для связи: {id_сообщения_у_админа: id_пользователя}
messages_map = {}

@dp.message(CommandStart())
async def cmd_start(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "Привет, Магистроадмин! 👑\n"
            "Я — Аноним Ред. Сюда будут прилетать сообщения от шедевролицеистов.\n"
            "Чтобы ответить, просто нажми «Ответить» (Reply) на сообщение и напиши текст."
        )
    else:
        await message.answer(
            "Привет, шедевролицеист! 👋\n"
            "Я — Аноним Ред. Напиши свой вопрос или сообщение, и я передам его магистроадминам совершенно анонимно.\n"
            "Жди ответа!"
        )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "🤖 <b>Как это работает?</b>\n\n"
        "1. Ты пишешь любой текст (или отправляешь фото).\n"
        "2. Бот скрывает твое имя и пересылает сообщение админам.\n"
        "3. Когда админ ответит, бот перешлет его ответ тебе сюда.\n\n"
        "Никто не узнает, кто именно написал сообщение. Полная анонимность! 🕵️‍♂️",
        parse_mode="HTML"
    )

@dp.message(Command("rules"))
async def cmd_rules(message: Message):
    await message.answer(
        "📜 <b>Правила Аноним Реда:</b>\n\n"
        "1. Никакого спама и флуда.\n"
        "2. Запрещены оскорбления и токсичность.\n"
        "3. Не скидывать запрещенные материалы (18+, экстремизм и т.д.).\n\n"
        "За нарушение правил — вечный бан без права переписки. Будьте адекватны! 🤝",
        parse_mode="HTML"
    )

@dp.message(F.chat.type == "private")
async def handle_messages(message: Message):
    # Если пишет обычный пользователь (Лицеист)
    if message.from_user.id != ADMIN_ID:
        try:
            # Пересылаем сообщение админу (скрывая автора)
            sent_msg = await bot.copy_message(
                chat_id=ADMIN_ID, 
                from_chat_id=message.chat.id, 
                message_id=message.message_id
            )
            # Запоминаем, от кого пришло сообщение, чтобы админ мог ответить
            messages_map[sent_msg.message_id] = message.from_user.id
            
            await message.answer("Твоё сообщение улетело к магистроадминам! 🚀 Жди ответа.")
        except Exception as e:
            print(f"Ошибка: {e}")
            await message.answer("Ошибка отправки. Возможно, админ еще не настроил меня.")
    
    # Если пишет сам Админ (отвечает на сообщение)
    elif message.from_user.id == ADMIN_ID:
        # Проверяем, что админ ответил именно на сообщение
        if message.reply_to_message:
            original_msg_id = message.reply_to_message.message_id
            
            # Ищем пользователя, которому нужно переслать ответ
            if original_msg_id in messages_map:
                target_user_id = messages_map[original_msg_id]
                try:
                    await bot.copy_message(
                        chat_id=target_user_id,
                        from_chat_id=ADMIN_ID,
                        message_id=message.message_id
                    )
                    await message.answer("Ответ отправлен лицеисту! ✅")
                except Exception as e:
                    await message.answer(f"Не удалось отправить ответ: {e}")
            else:
                await message.answer("Я не знаю, кому переслать этот ответ (связь потерялась).")
        else:
            await message.answer("Чтобы ответить лицеисту, нажми «Ответить» (Reply) на его сообщение.")

async def main():
    print("Аноним Ред запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 
