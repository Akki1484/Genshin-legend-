import random
import asyncio
from bson import ObjectId
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler
from shivu import application, banners_collection, user_collection

WISH_COST_PRIMOS = 60  # Chrono Crystals per WISH
WISH_COST_TICKET = 1  # WISH Tickets per WISH
MAX_WISHS = 10  # Max WISHs per pull

RARITY_ORDER = [
    "⚪ Common", "🟢 Uncommon", "🔵 Rare", "🟣 Extreme",
    "🟡 Sparking", "🔱 Ultra", "💠 Legends Limited",
    "🔮 Archon ", "🏆 Event-Exclusive"
]  # Defines rarity order for sorting

ANIMATION_FRAMES = [
    "🔮 **WISHing…** 🔮",
    "⚡ **Energy Gathering…** ⚡",
    "🌪 **WISH Portal Opening…** 🌪",
    "💥 **Characters Emerging…** 💥",
    "✨ **WISH Complete!** ✨"
]  # WISH animation frames

async def WISH(update: Update, context: CallbackContext) -> None:
    """Handles user WISH request from a banner with enhanced UI and animations."""
    user_id = update.effective_user.id
    args = context.args

    if len(args) < 2:
        await update.message.reply_text("❌ **Usage:** `/bWISH <banner_id> <1/10> <PRIMOS/ticket>`", parse_mode="Markdown")
        return

    banner_id, WISH_count, currency = args[0], int(args[1]), args[2].lower()
    if WISH_count not in [1, 10] or currency not in ["PRIMOS", "ticket"]:
        await update.message.reply_text("❌ **Invalid arguments!**\nUse: `/bWISH <banner_id> <1/10> <PRIMOS/ticket>`", parse_mode="Markdown")
        return

    try:
        banner = await banners_collection.find_one({"_id": ObjectId(banner_id)})
        if not banner:
            await update.message.reply_text("❌ **No banner found with this ID!**", parse_mode="Markdown")
            return
    except:
        await update.message.reply_text("❌ **Invalid Banner ID!**", parse_mode="Markdown")
        return

    banner_characters = banner.get("characters", [])
    if not banner_characters:
        await update.message.reply_text("❌ **No characters available in this banner!**", parse_mode="Markdown")
        return

    # ✅ Fetch user data
    user = await user_collection.find_one({'id': user_id})
    if not user:
        await update.message.reply_text("❌ **You don't have enough resources to WISH!**", parse_mode="Markdown")
        return

    total_cost = (WISH_COST_PRIMOS if currency == "PRIMOS" else WISH_COST_TICKET) * WISH_count
    balance_key = "chrono_crystals" if currency == "PRIMOS" else "WISH_tickets"

    if user.get(balance_key, 0) < total_cost:
        await update.message.reply_text(f"❌ **Not enough {balance_key.replace('_', ' ').title()}!**\nYou need `{total_cost}`.", parse_mode="Markdown")
        return

    # ✅ Deduct PRIMOS/Tickets
    await user_collection.update_one({'id': user_id}, {'$inc': {balance_key: -total_cost}})

    # ✅ Start WISH Animation
    animation_message = await update.message.reply_text("🔮 **WISHing…**")
    for frame in ANIMATION_FRAMES:
        await asyncio.sleep(1.2)  # Delay between animation frames
        await animation_message.edit_text(frame, parse_mode="Markdown")

    # ✅ Select random characters
    WISHed_characters = random.sample(banner_characters, min(WISH_count, len(banner_characters)))

    # ✅ Add to user's collection
    await user_collection.update_one({'id': user_id}, {'$push': {'characters': {'$each': WISHed_characters}}})

    # ✅ Identify rarest character
    rarest_character = max(WISHed_characters, key=lambda char: RARITY_ORDER.index(char.get('rarity', "⚪ Common")))

    # ✅ Check if rarest character has an image
    rarest_image = rarest_character.get('file_id')
    if not rarest_image:
        rarest_image = "https://example.com/default_image.jpg"  # Set a default image if missing

    # ✅ Create WISH result message with a structured format
    WISH_results = (
        f"🎟 **WISH Results - {banner['name']}** 🎟\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
    )
    
    for char in WISHed_characters:
        WISH_results += f"🔹 **{char['name']}**\n" \
                          f"🎖 **Rarity:** {char['rarity']}\n" \
                          f"🔹 **Category:** {char['category']}\n" \
                          f"━━━━━━━━━━━━━━━━━━━━━━\n"

    keyboard = [[InlineKeyboardButton("📜 View Collection", switch_inline_query_current_chat=f"collection.{user_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # ✅ Send rarest character’s image & results
    await animation_message.delete()
    await update.message.reply_photo(
        photo=rarest_image,
        caption=WISH_results,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# ✅ Add Handlers
application.add_handler(CommandHandler("bWISH", WISH, block=False))
