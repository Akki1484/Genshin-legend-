import requests
from pymongo import ReturnDocument
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from shivu import application, sudo_users, OWNER_ID, collection, db, CHARA_CHANNEL_ID, SUPPORT_CHAT, user_collection

# ✅ Correct command usage instructions
WRONG_FORMAT_TEXT = """❌ Incorrect Format!
Use: `/upload <file_id> <character-name> <rarity-number> <category-number>`

🎖️ **Rarity Guide:**  
1️⃣ Common  
2️⃣ Standard 
3️⃣ Rare  
4️⃣ Extreme  
5️⃣ Sparking  
6️⃣ Ultra  
7️⃣ Teyvat Limited 
8️⃣ Archon  
9️⃣ Event-Exclusive  

🔹 **Category Guide:**  
1. Lore accurate  
2. Pyro 5 star  
3. Hydro 5 star
4. Cryo 5 star
5. Anemo 5 star
6. Electro 5 star
7. Dendro 5 star
8. Geo 5 star
9. Pyro 4 star
10. Hydro 4 star
11. Cryo 4 star
12. Anemo 4 star
13. Electro 4 star
14. Dendro 4 star
15. Geo 4 star
16. Sword 5 star
17. Polearm 5 star
18. Bow 5 star
19. Catalyst 5 star
20. Claymore 5 star
21. Sword 4 star
22. Polearm 4 star
23. Bow 4 star
24. Catalyst 4 star
25. Claymore 4 star
26. Fatui Harbinger 
"""

async def get_next_sequence_number(sequence_name):
    sequence_collection = db.sequences
    sequence_document = await sequence_collection.find_one_and_update(
        {'_id': sequence_name}, 
        {'$inc': {'sequence_value': 1}}, 
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    return sequence_document['sequence_value']


async def upload(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    # 🔒 Check if user has permission
    if user_id not in sudo_users and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You don't have permission to upload characters!")
        return

    try:
        args = context.args
        if len(args) < 4:  # Minimum required arguments
            await update.message.reply_text(WRONG_FORMAT_TEXT)
            return

        file_id = args[0]  # First argument is file_id
        rarity_input = args[-2]  # Second-last argument is rarity
        category_input = args[-1]  # Last argument is category
        character_name = ' '.join(args[1:-2]).replace('-', ' ').title()  # Everything in between is the name

        # ✅ Check if character is exclusive
        is_exclusive = "exclusive" in args
        if is_exclusive:
            category_input += " (Exclusive)"  # Append to category for database clarity

        # ✅ Validate file_id by checking if it exists using Telegram's API
        try:
            await context.bot.get_file(file_id)  # Attempt to get the file from Telegram servers
        except Exception:
            await update.message.reply_text("❌ Invalid File ID. Please provide correct file id.")
            return


        rarity_map = {
            "1": "⚪ Common",
            "2": "🟢 Standard",
            "3": "🔵 Rare",
            "4": "🟣 Extreme",
            "5": "🟡 Sparking",
            "6": "🔱 Ultra",
            "7": "💠 Teyvat Limited",
            "8": "🔮 Archon",
            "9": "🏆 Event-Exclusive"
        }
        rarity = rarity_map.get(rarity_input)
        if not rarity:
            await update.message.reply_text("❌ Invalid Rarity. Use numbers: 1-9.")
            return

        category_map = {
            "1": "🏆 Lore accurate",
            "2": "🔥 Pyro ⭐⭐⭐⭐⭐",
            "3": "🌊 Hydro ⭐⭐⭐⭐⭐",
            "4": "❄️ Cryo ⭐⭐⭐⭐⭐",
            "5": "💨 Anemo ⭐⭐⭐⭐⭐",
            "6": "⚡ Electro ⭐⭐⭐⭐⭐",
            "7": "☘️ Dendro ⭐⭐⭐⭐⭐",
            "8": "🗿 Geo ⭐⭐⭐⭐⭐",
            "9": "🔥 Pyro ⭐⭐⭐⭐",
            "10": "🌊 Hydro ⭐⭐⭐⭐",
            "11": "❄️ Cryo ⭐⭐⭐⭐",
            "12": "💨 Anemo ⭐⭐⭐⭐",
            "13": "⚡ Electro ⭐⭐⭐⭐",
            "14": "☘️ Dendro ⭐⭐⭐⭐",
            "15": "🗿 Geo ⭐⭐⭐⭐",
            "16": "⚔️ Sword ⭐⭐⭐⭐⭐",
            "17": "🔱 Polearm ⭐⭐⭐⭐⭐",
            "18": "🏹 Bow ⭐⭐⭐⭐⭐",
            "19": "📖 Catalyst ⭐⭐⭐⭐⭐",
            "20": "🗡️ Claymore ⭐⭐⭐⭐⭐",
            "21": "⚔️ Sword ⭐⭐⭐⭐",
            "22": "🔱 Polearm ⭐⭐⭐⭐",
            "23": "🏹 Bow ⭐⭐⭐⭐",
            "24": "📖 Catalyst ⭐⭐⭐⭐",
            "25": "🗡️ Claymore ⭐⭐⭐⭐", 
            "26": "🎭 Fatui Harbinger"
        }
        category = category_map.get(category_input)
        if not category:
            await update.message.reply_text("❌ Invalid Category. Use numbers: 1-9.")
            return

        char_id = str(await get_next_sequence_number("character_id")).zfill(3)

        character = {
            'file_id': file_id,
            'name': character_name,
            'rarity': rarity,
            'category': category,
            'id': char_id,
            'exclusive': is_exclusive  # Mark as exclusive if applicable
        }

        try:
            caption_text = (
                f"🏆 **New Character Added!**\n\n"
                f"🔥 **Character:** {character_name}\n"
                f"🎖️ **Rarity:** {rarity}\n"
                f"🔹 **Category:** {category}\n"
                f"🆔 **ID:** {char_id}\n\n"
                f"👤 Added by [{update.effective_user.first_name}](tg://user?id={user_id})"
            )

            if is_exclusive:
                caption_text += "\n🚀 **Exclusive Character** 🚀"

            message = await context.bot.send_photo(
                chat_id=CHARA_CHANNEL_ID,
                photo=file_id,
                caption=caption_text,
                parse_mode='Markdown'
            )

            character["message_id"] = message.message_id
            await collection.insert_one(character)
            await update.message.reply_text(f"✅ `{character_name}` successfully added!")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Character added, but couldn't send image. Error: {str(e)}")

    except Exception as e:
        await update.message.reply_text(f"❌ Upload failed! Error: {str(e)}")

# ✅ Function to delete a character
async def delete(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id not in sudo_users and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("🚫 Only bot owners can delete characters!")
        return

    try:
        args = context.args
        if len(args) != 1:
            await update.message.reply_text("❌ Incorrect format! Use: `/delete <Character ID>`")
            return

        character_id = args[0]

        # Find the character in the database
        character = await collection.find_one({"id": character_id})
        if not character:
            await update.message.reply_text("⚠️ Character not found in the database.")
            return

        # Delete the character from the main collection
        await collection.delete_one({"id": character_id})

        # Delete from users' collections
        await user_collection.update_many(
            {}, 
            {"$pull": {"characters": {"id": character_id}}}  # Remove character from all users' collections
        )

        # Try deleting the character's message from the character channel
        try:
            await context.bot.delete_message(chat_id=CHARA_CHANNEL_ID, message_id=character["message_id"])
        except:
            pass  # Ignore if the message doesn't exist

        await update.message.reply_text(f"✅ Character `{character_id}` deleted successfully from database & user collections!")

    except Exception as e:
        await update.message.reply_text(f"❌ Error deleting character: {str(e)}")

# ✅ Function to update character details
async def update(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    if user_id not in sudo_users and user_id != OWNER_ID:
        await update.message.reply_text("🚫 You do not have permission to update characters!")
        return

    try:
        args = context.args
        if len(args) != 3:
            await update.message.reply_text("❌ Incorrect format! Use: `/update <ID> <field> <new_value>`")
            return

        character = await collection.find_one({'id': args[0]})
        if not character:
            await update.message.reply_text("❌ Character not found.")
            return

        valid_fields = ["file_id", "name", "rarity", "category"]
        if args[1] not in valid_fields:
            await update.message.reply_text(f"❌ Invalid field! Use one of: {', '.join(valid_fields)}")
            return

        # ✅ Handle rarity update
        if args[1] == "rarity":
            if args[2] not in rarity_map:
                await update.message.reply_text("❌ Invalid rarity. Use 1-9.")
                return
            new_value = rarity_map[args[2]]
        else:
            new_value = args[2]

        # ✅ Update the database
        await collection.find_one_and_update({'id': args[0]}, {'$set': {args[1]: new_value}})

        await update.message.reply_text(f"✅ Character `{args[0]}` updated successfully!")

    except Exception as e:
        await update.message.reply_text("❌ Update failed! Make sure the bot has channel permissions.")

# ✅ Add command handlers
application.add_handler(CommandHandler("upload", upload, block=False))
application.add_handler(CommandHandler("delete", delete, block=False))
application.add_handler(CommandHandler("update", update, block=False))
