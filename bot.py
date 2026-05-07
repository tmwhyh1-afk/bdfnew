
import os
import difflib
import fitz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
user_files = {}

def extract_text(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    return text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل ملف PDF الأول ثم الملف الثاني.")

async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    document = update.message.document

    file = await context.bot.get_file(document.file_id)
    save_path = f"{document.file_unique_id}.pdf"
    await file.download_to_drive(save_path)

    if user_id not in user_files:
        user_files[user_id] = [save_path]
        await update.message.reply_text("تم حفظ الملف الأول.")
    else:
        user_files[user_id].append(save_path)

        pdf1 = user_files[user_id][0]
        pdf2 = user_files[user_id][1]

        text1 = extract_text(pdf1)
        text2 = extract_text(pdf2)

        diff = difflib.unified_diff(
            text1.splitlines(),
            text2.splitlines(),
            lineterm=''
        )

        result = "\n".join(diff)

        if not result.strip():
            result = "لا توجد اختلافات."

        with open("result.txt", "w", encoding="utf-8") as f:
            f.write(result[:4000])

        await update.message.reply_document(document=open("result.txt", "rb"))

        user_files[user_id] = []

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))

    app.run_polling()

if __name__ == "__main__":
    main()
