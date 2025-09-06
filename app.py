from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import aiohttp
import random
import os
import asyncio

# Токены из переменных окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

async def ask_deepseek(question):
    """Запрос к DeepSeek API"""
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        system_prompt = """Ты мистический оракул и предсказатель. Отвечай на вопросы в стиле таинственного, 
        мудрого предсказателя. Используй образный язык, метафоры, элементы мистики и тайны."""
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Вопрос: {question}"}
            ],
            "max_tokens": 350,
            "temperature": 0.8
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(DEEPSEEK_API_URL, headers=headers, json=data) as response:
                response_data = await response.json()
                
                if 'choices' in response_data and response_data['choices']:
                    return response_data['choices'][0]['message']['content'].strip()
                else:
                    return generate_fallback_prediction()
                    
    except Exception as e:
        print(f"API Error: {e}")
        return generate_fallback_prediction()

def generate_fallback_prediction():
    """Резервные предсказания"""
    predictions = [
        "🔮 Хрустальный шал затуманился... Спросите еще раз при полной луне.",
        "✨ Звезды шепчут, что нужно задать вопрос иначе...",
        "🌙 Силы вселенной советуют вернуться к этому вопросу позже.",
        "🌀 Ветер перемен принес новые возможности... попробуйте снова."
    ]
    return random.choice(predictions)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    welcome_text = """
    🔮 *Добро пожаловать, искатель истины!*

Я — Древний Оракул, хранитель тайн вселенной. Задай мне вопрос, и я приоткрою завесу будущего...

*Как спросить:*
/ask *Ваш вопрос* - получить предсказание
или просто напиши свой вопрос

*Примеры:*
`/ask Ждет ли меня любовь в этом году?`
`/ask Стоит ли менять работу?`

✨ *Приготовься узнать то, что скрыто от глаз простых смертных...*
    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /ask"""
    if not context.args:
        await update.message.reply_text(
            "🔮 *Задай свой вопрос после команды /ask*\n\nПример: `/ask Ждет ли меня успех?`", 
            parse_mode='Markdown'
        )
        return

    user_question = " ".join(context.args)
    await process_question(update, user_question)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка обычных сообщений"""
    if update.message.text and not update.message.text.startswith('/'):
        user_question = update.message.text
        await process_question(update, user_question)

async def process_question(update: Update, question: str):
    """Обработка вопроса"""
    await update.message.reply_chat_action(action="typing")
    await asyncio.sleep(1)
    
    prediction = await ask_deepseek(question)
    
    response = f"""
🔮 *Вопрос:* {question}

✨ *Предсказание Оракула:*
{prediction}

🌙 *Пусть звезды освещают твой путь...*
    """
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    help_text = """
    🌟 *Помощь Оракула*

*Команды:*
/start - начать общение
/ask [вопрос] - получить предсказание
/help - показать помощь

💫 *Просто напиши* любой вопрос!
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

def main():
    """Запуск бота"""
    print("🔮 Starting Oracle Bot...")
    
    if not TELEGRAM_TOKEN or not DEEPSEEK_API_KEY:
        print("❌ ERROR: Missing environment variables!")
        print("Please set TELEGRAM_TOKEN and DEEPSEEK_API_KEY")
        return
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
application.run_polling()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ask", ask_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✨ Oracle Bot is running!")
    

if __name__ == '__main__':

    main()

