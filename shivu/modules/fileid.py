from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext
from shivu import application, banners_collection, OWNER_ID, sudo_users

async def get_file_id(update: Update, context: CallbackContext) -> None:
    """Extracts file_id from a sent image and stores it in the database if needed."""
    user_id = update.effective_user.id

    # ✅ Check if the user is an owner or sudo user
    if user_id not in sudo_users and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You don't have permission to extract file IDs!")
        return

    if not update.message.photo:
        await update.message.reply_text("❌ Please send an image to get its file_id!")
        return

    # ✅ Get the highest quality file_id
    file_id = update.message.photo[-1].file_id

    await update.message.reply_text(f"📂 **File ID Extracted:**\n`{file_id}`", parse_mode="Markdown")

async def get_file_id_cmd(update: Update, context: CallbackContext) -> None:
    """Extracts file_id from a replied image message."""
    user_id = update.effective_user.id

    # ✅ Check permissions
    if user_id not in sudo_users and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You don't have permission to extract file IDs!")
        return

    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text("❌ Reply to an image with `/getfileid` to extract the file_id!")
        return

    # ✅ Get the highest quality file_id
    file_id = update.message.reply_to_message.photo[-1].file_id

    await update.message.reply_text(f"📂 **File ID Extracted:**\n`{file_id}`", parse_mode="Markdown")

# ✅ Add Handlers
application.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, get_file_id))
application.add_handler(CommandHandler("fileid", get_file_id_cmd, block=False))
