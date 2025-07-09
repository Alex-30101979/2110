import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

questions = [
    "Как часто ты залипаешь в экран без толку?",
    "Можешь вспомнить, что делал(а) утром?",
    "Сколько задач ты держишь в голове сейчас?",
    "Читаешь ли ты один абзац по нескольку раз?",
    "Как ты себя чувствуешь, когда садишься за работу?",
    "Когда в последний раз ты чувствовал(а) себя умным?"
]

answers = [
    ["Почти каждый день", "Иногда", "Редко"],
    ["Нет", "Да, с трудом", "Да, легко"],
    ["5+", "3–4", "1–2"],
    ["Да, постоянно", "Иногда", "Почти никогда"],
    ["Паника/ступор", "Вялость", "Ясность"],
    ["Даже не помню", "Неделю назад", "Вчера"]
]

results = {
    "overheat": "🔥 Кипящий мозг... (здесь вставить PDF-текст)",
    "defocus": "☁️ Расфокус... (здесь вставить PDF-текст)",
    "slow": "🐢 Тормоз... (здесь вставить PDF-текст)",
    "sabotage": "🎭 Самосаботажник... (здесь вставить PDF-текст)"
}

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {"q": 0, "score": []}
    await send_question(update, context)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    q_index = user_data[user_id]["q"]

    if q_index >= len(questions):
        await show_result(update, context)
        return

    question = questions[q_index]
    options = answers[q_index]

    keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in options]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.message.edit_text(question, reply_markup=reply_markup)
    else:
        await update.message.reply_text(question, reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    answer = query.data
    user_data[user_id]["score"].append(answer)
    user_data[user_id]["q"] += 1
    await send_question(update, context)

async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    answers = user_data[user_id]["score"]

    if answers.count("Почти каждый день") > 1:
        result_text = results["overheat"]
    elif answers.count("Нет") > 1:
        result_text = results["defocus"]
    elif answers.count("Вялость") > 1:
        result_text = results["slow"]
    else:
        result_text = results["sabotage"]

    await update.callback_query.message.edit_text(result_text)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("Бот запущен...")
    app.run_polling()
