from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.user_settings_helper import get_user_settings, update_user_settings


# Store user input states
user_input_states = {}


def get_settings_status_text(settings):
    """Generate formatted status display with emojis"""
    status = "⚙️ **Forward Settings**\n\n"
    status += "Configure how your downloaded files are forwarded.\n\n"
    status += "**Current Settings:**\n"
    
    # Upload type
    upload_type = "📄 Document" if settings['upload_as_document'] else "📷 Media"
    status += f"📤 Upload Type: {upload_type}\n"
    
    # Caption
    caption_status = "✅ Set" if settings['custom_caption'] else "❌ Not Set"
    status += f"✏️ Custom Caption: {caption_status}\n"
    
    # Thumbnail
    thumb_status = "✅ Set" if settings['thumbnail'] else "❌ Not Set"
    status += f"🖼️ Custom Thumbnail: {thumb_status}\n"
    
    # Prefix/Suffix
    prefix_status = "✅ Set" if settings['filename_prefix'] else "❌ Not Set"
    suffix_status = "✅ Set" if settings['filename_suffix'] else "❌ Not Set"
    status += f"📝 Filename Prefix: {prefix_status}\n"
    status += f"📝 Filename Suffix: {suffix_status}\n"
    
    # Replacements - count rules by splitting on pipe
    caption_rules = [r.strip() for r in settings.get('caption_replacements', '').split('|') if r.strip()]
    filename_rules = [r.strip() for r in settings.get('filename_replacements', '').split('|') if r.strip()]
    
    caption_replace_status = f"✅ Set ({len(caption_rules)} rules)" if caption_rules else "❌ Not Set"
    filename_replace_status = f"✅ Set ({len(filename_rules)} rules)" if filename_rules else "❌ Not Set"
    status += f"🔄 Replace Caption Words: {caption_replace_status}\n"
    status += f"🔄 Replace Filename Words: {filename_replace_status}\n"
    
    status += "\n**Click a button below to configure:**"
    return status


def get_main_menu_keyboard():
    """Get main settings menu keyboard"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚙️ Upload Type", callback_data="settings_upload_type"),
            InlineKeyboardButton("✏️ Set Caption", callback_data="settings_caption")
        ],
        [
            InlineKeyboardButton("🖼️ Set Thumbnail", callback_data="settings_thumbnail"),
            InlineKeyboardButton("📝 Prefix/Suffix", callback_data="settings_prefix_suffix")
        ],
        [
            InlineKeyboardButton("🔄 Replace Words", callback_data="settings_replace_words")
        ],
        [
            InlineKeyboardButton("🔙 Close", callback_data="settings_close")
        ]
    ])


@Client.on_message(filters.command("settings") & filters.private)
async def settings_command(client: Client, message: Message):
    """Show settings menu"""
    try:
        user_id = message.from_user.id
        
        # Clear any existing input state
        if user_id in user_input_states:
            del user_input_states[user_id]
        
        # Get user settings
        settings = get_user_settings(user_id)
        
        # Show menu
        await message.reply_text(
            get_settings_status_text(settings),
            reply_markup=get_main_menu_keyboard()
        )
    except Exception as e:
        await message.reply_text(f"❌ Error loading settings: {str(e)}")


@Client.on_callback_query(filters.regex("^settings_"))
async def settings_callback_handler(client: Client, callback_query: CallbackQuery):
    """Handle all settings callbacks"""
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    # Get current settings
    settings = get_user_settings(user_id)
    
    if data == "settings_close":
        await callback_query.message.delete()
        await callback_query.answer("Settings closed")
        return
    
    elif data == "settings_main":
        # Return to main menu
        await callback_query.message.edit_text(
            get_settings_status_text(settings),
            reply_markup=get_main_menu_keyboard()
        )
        await callback_query.answer()
        return
    
    elif data == "settings_upload_type":
        await show_upload_type_menu(callback_query, settings)
    
    elif data == "settings_upload_document":
        update_user_settings(user_id, {"upload_as_document": True})
        settings = get_user_settings(user_id)
        await callback_query.message.edit_text(
            get_settings_status_text(settings),
            reply_markup=get_main_menu_keyboard()
        )
        await callback_query.answer("✅ Upload type set to Document")
    
    elif data == "settings_upload_media":
        update_user_settings(user_id, {"upload_as_document": False})
        settings = get_user_settings(user_id)
        await callback_query.message.edit_text(
            get_settings_status_text(settings),
            reply_markup=get_main_menu_keyboard()
        )
        await callback_query.answer("✅ Upload type set to Media")
    
    elif data == "settings_caption":
        await show_caption_menu(callback_query, settings)
    
    elif data == "settings_caption_set":
        # Set state to wait for caption input
        user_input_states[user_id] = {"waiting_for": "caption"}
        await callback_query.message.edit_text(
            "✏️ **Set Custom Caption**\n\n"
            "Send me your custom caption with formatting (bold, italic, code, etc.).\n\n"
            "**Available variables:**\n"
            "• `{filename}` - File name (after transformations)\n"
            "• `{size}` - File size\n"
            "• `{extension}` - File extension\n"
            "• `{caption}` - Original caption\n\n"
            "**Example:**\n"
            "**📁 File:** `{filename}`\n"
            "__💾 Size:__ {size}\n\n"
            "Send /cancel to abort."
        )
        await callback_query.answer()
    
    elif data == "settings_caption_clear":
        update_user_settings(user_id, {"custom_caption": None, "caption_entities": None})
        settings = get_user_settings(user_id)
        await callback_query.message.edit_text(
            get_settings_status_text(settings),
            reply_markup=get_main_menu_keyboard()
        )
        await callback_query.answer("✅ Custom caption cleared")
    
    elif data == "settings_thumbnail":
        await show_thumbnail_menu(callback_query, settings)
    
    elif data == "settings_thumbnail_set":
        user_input_states[user_id] = {"waiting_for": "thumbnail"}
        await callback_query.message.edit_text(
            "🖼️ **Set Custom Thumbnail**\n\n"
            "Send me a photo or image file to use as thumbnail.\n\n"
            "Send /cancel to abort."
        )
        await callback_query.answer()
    
    elif data == "settings_thumbnail_remove":
        update_user_settings(user_id, {"thumbnail": None})
        settings = get_user_settings(user_id)
        await callback_query.message.edit_text(
            get_settings_status_text(settings),
            reply_markup=get_main_menu_keyboard()
        )
        await callback_query.answer("✅ Thumbnail removed")
    
    elif data == "settings_prefix_suffix":
        await show_prefix_suffix_menu(callback_query, settings)
    
    elif data == "settings_prefix_set":
        user_input_states[user_id] = {"waiting_for": "prefix"}
        await callback_query.message.edit_text(
            "📝 **Set Filename Prefix**\n\n"
            "Send me the prefix to add before filenames.\n"
            "A space will be added automatically after the prefix.\n\n"
            "**Example:** `[VIP]`\n"
            "**Result:** `[VIP] filename.pdf`\n\n"
            "Send /cancel to abort."
        )
        await callback_query.answer()
    
    elif data == "settings_suffix_set":
        user_input_states[user_id] = {"waiting_for": "suffix"}
        await callback_query.message.edit_text(
            "📝 **Set Filename Suffix**\n\n"
            "Send me the suffix to add after filenames.\n"
            "A space will be added automatically before the suffix.\n\n"
            "**Example:** `HD`\n"
            "**Result:** `filename HD.pdf`\n\n"
            "Send /cancel to abort."
        )
        await callback_query.answer()
    
    elif data == "settings_prefix_clear":
        update_user_settings(user_id, {"filename_prefix": None})
        settings = get_user_settings(user_id)
        await show_prefix_suffix_menu(callback_query, settings)
        await callback_query.answer("✅ Prefix cleared")
    
    elif data == "settings_suffix_clear":
        update_user_settings(user_id, {"filename_suffix": None})
        settings = get_user_settings(user_id)
        await show_prefix_suffix_menu(callback_query, settings)
        await callback_query.answer("✅ Suffix cleared")
    
    elif data == "settings_replace_words":
        await show_replace_words_menu(callback_query, settings)
    
    elif data == "settings_replace_caption":
        await show_caption_replace_menu(callback_query, settings)
    
    elif data == "settings_replace_filename":
        await show_filename_replace_menu(callback_query, settings)
    
    elif data == "settings_caption_replace_set":
        user_input_states[user_id] = {"waiting_for": "caption_replacements"}
        await callback_query.message.edit_text(
            "🔄 **Set Caption Word Replacements**\n\n"
            "Send me replacement rules in this format:\n"
            "`old:new | old2:new2 | remove_word`\n\n"
            "**Examples:**\n"
            "• `Uploaded:📤 Uploaded | Size:💾 Size`\n"
            "• `|:•` (replace pipe with bullet)\n"
            "• `test:TEST | temp` (replace 'test' and remove 'temp')\n\n"
            "Send /cancel to abort."
        )
        await callback_query.answer()
    
    elif data == "settings_filename_replace_set":
        user_input_states[user_id] = {"waiting_for": "filename_replacements"}
        await callback_query.message.edit_text(
            "🔄 **Set Filename Word Replacements**\n\n"
            "Send me replacement rules in this format:\n"
            "`old:new | old2:new2 | remove_word`\n\n"
            "**Examples:**\n"
            "• `test:TEST | file:FILE` (replacements)\n"
            "• `_backup | _temp` (remove words)\n"
            "• `python:Python | _old` (mixed)\n\n"
            "Send /cancel to abort."
        )
        await callback_query.answer()
    
    elif data == "settings_caption_replace_clear":
        update_user_settings(user_id, {"caption_replacements": ""})
        settings = get_user_settings(user_id)
        await show_caption_replace_menu(callback_query, settings)
        await callback_query.answer("✅ Caption replacements cleared")
    
    elif data == "settings_filename_replace_clear":
        update_user_settings(user_id, {"filename_replacements": ""})
        settings = get_user_settings(user_id)
        await show_filename_replace_menu(callback_query, settings)
        await callback_query.answer("✅ Filename replacements cleared")


async def show_upload_type_menu(callback_query, settings):
    """Show upload type selection menu"""
    current = "Document" if settings['upload_as_document'] else "Media"
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"{'✓ ' if settings['upload_as_document'] else ''}📄 Document",
                callback_data="settings_upload_document"
            )
        ],
        [
            InlineKeyboardButton(
                f"{'✓ ' if not settings['upload_as_document'] else ''}📷 Send as Media",
                callback_data="settings_upload_media"
            )
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="settings_main")]
    ])
    
    await callback_query.message.edit_text(
        f"⚙️ **Upload Type**\n\n"
        f"Current: **{current}**\n\n"
        f"**Document:** Files sent as documents (all file types)\n"
        f"**Media:** Photos/videos sent as media (better preview)\n\n"
        f"Select upload type:",
        reply_markup=keyboard
    )
    await callback_query.answer()


async def show_caption_menu(callback_query, settings):
    """Show caption configuration menu"""
    caption_preview = settings.get('custom_caption', 'Not set')
    if caption_preview and len(caption_preview) > 100:
        caption_preview = caption_preview[:100] + "..."
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Set Caption", callback_data="settings_caption_set")],
        [InlineKeyboardButton("❌ Clear Caption", callback_data="settings_caption_clear")] if settings.get('custom_caption') else [],
        [InlineKeyboardButton("🔙 Back", callback_data="settings_main")]
    ])
    
    await callback_query.message.edit_text(
        f"✏️ **Custom Caption**\n\n"
        f"**Current Caption:**\n{caption_preview}\n\n"
        f"Variables: `{{filename}}`, `{{size}}`, `{{extension}}`, `{{caption}}`",
        reply_markup=keyboard
    )
    await callback_query.answer()


async def show_thumbnail_menu(callback_query, settings):
    """Show thumbnail configuration menu"""
    has_thumb = bool(settings.get('thumbnail'))
    
    buttons = [[InlineKeyboardButton("🖼️ Upload Thumbnail", callback_data="settings_thumbnail_set")]]
    
    if has_thumb:
        buttons.append([InlineKeyboardButton("❌ Remove Thumbnail", callback_data="settings_thumbnail_remove")])
    
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="settings_main")])
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    status = "✅ Set" if has_thumb else "❌ Not Set"
    
    await callback_query.message.edit_text(
        f"🖼️ **Custom Thumbnail**\n\n"
        f"**Status:** {status}\n\n"
        f"Thumbnails are shown on documents and videos.",
        reply_markup=keyboard
    )
    await callback_query.answer()


async def show_prefix_suffix_menu(callback_query, settings):
    """Show prefix/suffix configuration menu"""
    prefix = settings.get('filename_prefix', 'Not set')
    suffix = settings.get('filename_suffix', 'Not set')
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Set Prefix", callback_data="settings_prefix_set"),
            InlineKeyboardButton("➕ Set Suffix", callback_data="settings_suffix_set")
        ],
        [
            InlineKeyboardButton("❌ Clear Prefix", callback_data="settings_prefix_clear") if settings.get('filename_prefix') else InlineKeyboardButton("", callback_data="none"),
            InlineKeyboardButton("❌ Clear Suffix", callback_data="settings_suffix_clear") if settings.get('filename_suffix') else InlineKeyboardButton("", callback_data="none")
        ],
        [InlineKeyboardButton("🔙 Back", callback_data="settings_main")]
    ])
    
    # Filter out empty buttons
    keyboard.inline_keyboard[1] = [btn for btn in keyboard.inline_keyboard[1] if btn.text]
    if not keyboard.inline_keyboard[1]:
        keyboard.inline_keyboard.pop(1)
    
    await callback_query.message.edit_text(
        f"📝 **Filename Prefix & Suffix**\n\n"
        f"**Prefix:** `{prefix}`\n"
        f"**Suffix:** `{suffix}`\n\n"
        f"Spaces are added automatically.\n"
        f"Example: `[VIP] filename HD.pdf`",
        reply_markup=keyboard
    )
    await callback_query.answer()


async def show_replace_words_menu(callback_query, settings):
    """Show word replacement main menu"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Caption Replacements", callback_data="settings_replace_caption")],
        [InlineKeyboardButton("📄 Filename Replacements", callback_data="settings_replace_filename")],
        [InlineKeyboardButton("🔙 Back", callback_data="settings_main")]
    ])
    
    await callback_query.message.edit_text(
        "🔄 **Replace Words**\n\n"
        "Configure word replacements for captions and filenames separately.",
        reply_markup=keyboard
    )
    await callback_query.answer()


async def show_caption_replace_menu(callback_query, settings):
    """Show caption replacement configuration"""
    rules = settings.get('caption_replacements', 'Not set')
    if rules and len(rules) > 100:
        rules = rules[:100] + "..."
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Set Rules", callback_data="settings_caption_replace_set")],
        [InlineKeyboardButton("❌ Clear Rules", callback_data="settings_caption_replace_clear")] if settings.get('caption_replacements') else [],
        [InlineKeyboardButton("🔙 Back", callback_data="settings_replace_words")]
    ])
    
    await callback_query.message.edit_text(
        f"🔄 **Caption Word Replacements**\n\n"
        f"**Current Rules:**\n`{rules}`\n\n"
        f"Format: `old:new | old2:new2 | remove`",
        reply_markup=keyboard
    )
    await callback_query.answer()


async def show_filename_replace_menu(callback_query, settings):
    """Show filename replacement configuration"""
    rules = settings.get('filename_replacements', 'Not set')
    if rules and len(rules) > 100:
        rules = rules[:100] + "..."
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Set Rules", callback_data="settings_filename_replace_set")],
        [InlineKeyboardButton("❌ Clear Rules", callback_data="settings_filename_replace_clear")] if settings.get('filename_replacements') else [],
        [InlineKeyboardButton("🔙 Back", callback_data="settings_replace_words")]
    ])
    
    await callback_query.message.edit_text(
        f"🔄 **Filename Word Replacements**\n\n"
        f"**Current Rules:**\n`{rules}`\n\n"
        f"Format: `old:new | old2:new2 | remove`",
        reply_markup=keyboard
    )
    await callback_query.answer()


@Client.on_message(filters.private & filters.text & ~filters.command(["settings", "cancel", "start", "help", "unzip", "myplan", "premium", "redeem"]), group=10)
async def handle_user_input(client: Client, message: Message):
    """Handle user text input for settings configuration"""
    user_id = message.from_user.id
    
    # Check if user is in input state
    if user_id not in user_input_states:
        return
    
    state = user_input_states[user_id]
    waiting_for = state.get("waiting_for")
    
    if waiting_for == "caption":
        # Save caption with formatting entities
        caption = message.text or message.caption
        entities = message.entities or message.caption_entities or []
        
        # Convert entities to dict format for storage
        entities_dict = [
            {
                "type": entity.type,
                "offset": entity.offset,
                "length": entity.length
            }
            for entity in entities
        ] if entities else None
        
        update_user_settings(user_id, {
            "custom_caption": caption,
            "caption_entities": entities_dict
        })
        
        del user_input_states[user_id]
        
        settings = get_user_settings(user_id)
        await message.reply_text(
            get_settings_status_text(settings),
            reply_markup=get_main_menu_keyboard()
        )
    
    elif waiting_for == "prefix":
        prefix = message.text.strip()
        update_user_settings(user_id, {"filename_prefix": prefix})
        del user_input_states[user_id]
        
        await message.reply_text(f"✅ Prefix set to: `{prefix}`\n\nA space will be added after it automatically.")
        
        settings = get_user_settings(user_id)
        await message.reply_text(
            get_settings_status_text(settings),
            reply_markup=get_main_menu_keyboard()
        )
    
    elif waiting_for == "suffix":
        suffix = message.text.strip()
        update_user_settings(user_id, {"filename_suffix": suffix})
        del user_input_states[user_id]
        
        await message.reply_text(f"✅ Suffix set to: `{suffix}`\n\nA space will be added before it automatically.")
        
        settings = get_user_settings(user_id)
        await message.reply_text(
            get_settings_status_text(settings),
            reply_markup=get_main_menu_keyboard()
        )
    
    elif waiting_for == "caption_replacements":
        rules = message.text.strip()
        update_user_settings(user_id, {"caption_replacements": rules})
        del user_input_states[user_id]
        
        await message.reply_text(f"✅ Caption replacement rules set:\n`{rules}`")
        
        settings = get_user_settings(user_id)
        await message.reply_text(
            get_settings_status_text(settings),
            reply_markup=get_main_menu_keyboard()
        )
    
    elif waiting_for == "filename_replacements":
        rules = message.text.strip()
        update_user_settings(user_id, {"filename_replacements": rules})
        del user_input_states[user_id]
        
        await message.reply_text(f"✅ Filename replacement rules set:\n`{rules}`")
        
        settings = get_user_settings(user_id)
        await message.reply_text(
            get_settings_status_text(settings),
            reply_markup=get_main_menu_keyboard()
        )


@Client.on_message(filters.private & (filters.photo | filters.document) & ~filters.command(["settings", "cancel", "start", "help", "unzip"]), group=10)
async def handle_photo_input(client: Client, message: Message):
    """Handle photo/document input for thumbnail"""
    user_id = message.from_user.id
    
    # Check if user is waiting for thumbnail
    if user_id not in user_input_states:
        return
    
    state = user_input_states[user_id]
    if state.get("waiting_for") != "thumbnail":
        return
    
    # Get file_id from photo or document
    if message.photo:
        file_id = message.photo.file_id
    elif message.document:
        # Check if document is an image
        mime_type = message.document.mime_type or ""
        if not mime_type.startswith('image/'):
            await message.reply_text("❌ Please send an image file for thumbnail.")
            return
        file_id = message.document.file_id
    else:
        await message.reply_text("❌ Please send a photo or image file.")
        return
    
    # Save thumbnail
    update_user_settings(user_id, {"thumbnail": file_id})
    del user_input_states[user_id]
    
    await message.reply_text("✅ Thumbnail saved successfully!")
    
    settings = get_user_settings(user_id)
    await message.reply_text(
        get_settings_status_text(settings),
        reply_markup=get_main_menu_keyboard()
    )


@Client.on_message(filters.command("cancel") & filters.private)
async def handle_cancel_input(client: Client, message: Message):
    """Handle cancel command to abort input"""
    user_id = message.from_user.id
    
    if user_id in user_input_states:
        del user_input_states[user_id]
        await message.reply_text("❌ Input cancelled.")
        
        settings = get_user_settings(user_id)
        await message.reply_text(
            get_settings_status_text(settings),
            reply_markup=get_main_menu_keyboard()
        )
