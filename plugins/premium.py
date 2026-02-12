from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.database import users_collection, bot_config_collection
from datetime import datetime
import qrcode
import io
import os

# Pricing configuration (in INR and USDT)
PRICING = {
    'premium': {
        1: {"inr": 5, "usdt": 0.05},
        7: {"inr": 30, "usdt": 0.30},
        30: {"inr": 90, "usdt": 0.90}
    },
    'ultra_premium': {
        1: {"inr": 15, "usdt": 0.15},
        7: {"inr": 50, "usdt": 0.50},
        30: {"inr": 140, "usdt": 1.40}
    }
}

# Store user purchase states
purchase_states = {}


@Client.on_message(filters.command("premium") & filters.private)
async def premium_command(client: Client, message: Message):
    """Handle /premium command - start purchase flow"""
    user_id = message.from_user.id
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 Premium", callback_data="buy_premium")],
        [InlineKeyboardButton("⭐ Ultra Premium", callback_data="buy_ultra_premium")],
        [InlineKeyboardButton("❌ Cancel", callback_data="buy_cancel")]
    ])
    
    await message.reply_text(
        "💳 **Purchase Premium**\n\n"
        "Select your plan:\n\n"
        "**💎 Premium**\n"
        "• 2 GB max file size\n"
        "• 15 files per day\n"
        "• Priority support\n\n"
        "**⭐ Ultra Premium**\n"
        "• 2 GB max file size\n"
        "• 50 files per day\n"
        "• Premium support",
        reply_markup=keyboard
    )


@Client.on_callback_query(filters.regex("^buy_"))
async def purchase_callback(client: Client, callback_query: CallbackQuery):
    """Handle purchase flow callbacks"""
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    # Cancel purchase
    if data == "buy_cancel":
        purchase_states.pop(user_id, None)
        await callback_query.message.delete()
        await callback_query.answer("Purchase cancelled", show_alert=False)
        return
    
    # Back button
    if data == "buy_back":
        state = purchase_states.get(user_id, {})
        
        # Navigate back based on current step
        if 'payment_method' in state:
            # Go back to duration selection from payment method
            del state['payment_method']
            plan_type = state['plan_type']
            plan_name = "Premium" if plan_type == "premium" else "Ultra Premium"
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("1 Day", callback_data="buy_dur_1")],
                [InlineKeyboardButton("7 Days", callback_data="buy_dur_7")],
                [InlineKeyboardButton("30 Days", callback_data="buy_dur_30")],
                [InlineKeyboardButton("⬅️ Back", callback_data="buy_back")],
                [InlineKeyboardButton("❌ Cancel", callback_data="buy_cancel")]
            ])
            await callback_query.message.edit_text(
                f"💎 **{plan_name}**\n\nSelect duration:",
                reply_markup=keyboard
            )
        elif 'duration' in state:
            # Go back to plan selection from duration
            del state['duration']
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 Premium", callback_data="buy_premium")],
                [InlineKeyboardButton("⭐ Ultra Premium", callback_data="buy_ultra_premium")],
                [InlineKeyboardButton("❌ Cancel", callback_data="buy_cancel")]
            ])
            await callback_query.message.edit_text(
                "💳 **Purchase Premium**\n\n"
                "Select your plan:\n\n"
                "**💎 Premium**\n"
                "• 2 GB max file size\n"
                "• 15 files per day\n"
                "• Priority support\n\n"
                "**⭐ Ultra Premium**\n"
                "• 2 GB max file size\n"
                "• 50 files per day\n"
                "• Premium support",
                reply_markup=keyboard
            )
        elif 'plan_type' in state:
            # Go back to initial screen from plan selection
            purchase_states.pop(user_id, None)
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 Premium", callback_data="buy_premium")],
                [InlineKeyboardButton("⭐ Ultra Premium", callback_data="buy_ultra_premium")],
                [InlineKeyboardButton("❌ Cancel", callback_data="buy_cancel")]
            ])
            await callback_query.message.edit_text(
                "💳 **Purchase Premium**\n\n"
                "Select your plan:\n\n"
                "**💎 Premium**\n"
                "• 2 GB max file size\n"
                "• 15 files per day\n"
                "• Priority support\n\n"
                "**⭐ Ultra Premium**\n"
                "• 2 GB max file size\n"
                "• 50 files per day\n"
                "• Premium support",
                reply_markup=keyboard
            )
        return
    
    # Delete QR and go back (special handling for UPI screen)
    if data == "buy_back_qr":
        state = purchase_states.get(user_id, {})
        if 'payment_method' in state:
            del state['payment_method']
        
        plan_type = state.get('plan_type')
        duration = state.get('duration')
        
        price_inr = PRICING[plan_type][duration]['inr']
        plan_name = "Premium" if plan_type == "premium" else "Ultra Premium"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 UPI Payment", callback_data="buy_pay_upi")],
            [InlineKeyboardButton("💰 Crypto (USD/USDT)", callback_data="buy_pay_crypto")],
            [InlineKeyboardButton("⬅️ Back", callback_data="buy_back")],
            [InlineKeyboardButton("❌ Cancel", callback_data="buy_cancel")]
        ])
        
        await callback_query.message.delete()
        await client.send_message(
            user_id,
            f"💳 **Payment Method**\n\n"
            f"**Plan:** {plan_name}\n"
            f"**Duration:** {duration} day(s)\n"
            f"**Amount:** ₹{price_inr}\n\n"
            f"Choose your payment method:",
            reply_markup=keyboard
        )
        return
    
    # Plan selection
    if data in ["buy_premium", "buy_ultra_premium"]:
        plan_type = "premium" if data == "buy_premium" else "ultra_premium"
        plan_name = "Premium" if plan_type == "premium" else "Ultra Premium"
        
        purchase_states[user_id] = {"plan_type": plan_type}
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("1 Day", callback_data="buy_dur_1")],
            [InlineKeyboardButton("7 Days", callback_data="buy_dur_7")],
            [InlineKeyboardButton("30 Days", callback_data="buy_dur_30")],
            [InlineKeyboardButton("⬅️ Back", callback_data="buy_back")],
            [InlineKeyboardButton("❌ Cancel", callback_data="buy_cancel")]
        ])
        
        await callback_query.message.edit_text(
            f"💎 **{plan_name}**\n\nSelect duration:",
            reply_markup=keyboard
        )
        return
    
    # Duration selection  
    if data.startswith("buy_dur_"):
        duration = int(data.split("_")[-1])
        
        if user_id not in purchase_states:
            await callback_query.answer("Session expired, please start again", show_alert=True)
            return
        
        purchase_states[user_id]['duration'] = duration
        
        plan_type = purchase_states[user_id]['plan_type']
        price_inr = PRICING[plan_type][duration]['inr']
        plan_name = "Premium" if plan_type == "premium" else "Ultra Premium"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 UPI Payment", callback_data="buy_pay_upi")],
            [InlineKeyboardButton("💰 Crypto (USD/USDT)", callback_data="buy_pay_crypto")],
            [InlineKeyboardButton("⬅️ Back", callback_data="buy_back")],
            [InlineKeyboardButton("❌ Cancel", callback_data="buy_cancel")]
        ])
        
        await callback_query.message.edit_text(
            f"💳 **Payment Method**\n\n"
            f"**Plan:** {plan_name}\n"
            f"**Duration:** {duration} day(s)\n"
            f"**Amount:** ₹{price_inr}\n\n"
            f"Choose your payment method:",
            reply_markup=keyboard
        )
        return
    
    # UPI Payment
    if data == "buy_pay_upi":
        if user_id not in purchase_states:
            await callback_query.answer("Session expired, please start again", show_alert=True)
            return
        
        state = purchase_states[user_id]
        plan_type = state['plan_type']
        duration = state['duration']
        price_inr = PRICING[plan_type][duration]['inr']
        plan_name = "Premium" if plan_type == "premium" else "Ultra Premium"
        
        # Get UPI details from config
        upi_config = bot_config_collection.find_one({"setting_name": "upi_payment"})
        
        if not upi_config:
            await callback_query.answer("UPI payment not configured. Please contact admin.", show_alert=True)
            return
        
        upi_id = upi_config.get('upi_id')
        bank_name = upi_config.get('bank_name', 'Bank')
        
        # Generate payment note
        payment_note = f"UNZIP{user_id}{duration}D"
        
        # Generate UPI QR code
        upi_url = f"upi://pay?pa={upi_id}&pn={bank_name}&am={price_inr}&tn={payment_note}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(upi_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        bio = io.BytesIO()
        img.save(bio, 'PNG')
        bio.seek(0)
        
        # Admin contact button
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📤 Send Payment Proof to Admin", url="https://t.me/LuciferJaat8")],
            [InlineKeyboardButton("⬅️ Back", callback_data="buy_back_qr")],
            [InlineKeyboardButton("❌ Cancel", callback_data="buy_cancel")]
        ])
        
        caption = (
            f"💳 **UPI Payment**\n\n"
            f"**Plan:** {plan_name}\n"
            f"**Duration:** {duration} day(s)\n"
            f"**Amount:** ₹{price_inr}\n\n"
            f"**📱 Payment Steps:**\n"
            f"1. Scan QR code or use UPI ID below\n"
            f"2. Enter amount: ₹{price_inr}\n"
            f"3. **Important:** Add this note: `{payment_note}`\n"
            f"4. Complete payment\n"
            f"5. Take screenshot of successful payment\n"
            f"6. Click button below to send proof to admin\n\n"
            f"**UPI ID:** `{upi_id}`\n"
            f"**Bank:** {bank_name}\n"
            f"**Payment Note:** `{payment_note}`\n\n"
            f"⚠️ **Include payment note to get automatic verification!**\n\n"
            f"When contacting admin, send:\n"
            f"📸 Payment screenshot\n"
            f"🆔 Your User ID: `{user_id}`\n"
            f"💎 Plan: {plan_name} ({duration}d)"
        )
        
        await callback_query.message.delete()
        await client.send_photo(
            user_id,
            photo=bio,
            caption=caption,
            reply_markup=keyboard
        )
        return
    
    # Crypto Payment
    if data == "buy_pay_crypto":
        if user_id not in purchase_states:
            await callback_query.answer("Session expired, please start again", show_alert=True)
            return
        
        state = purchase_states[user_id]
        plan_type = state['plan_type']
        duration = state['duration']
        price_inr = PRICING[plan_type][duration]['inr']
        price_usd = PRICING[plan_type][duration]['usdt']
        plan_name = "Premium" if plan_type == "premium" else "Ultra Premium"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Contact Admin", url="https://t.me/LuciferJaat8")],
            [InlineKeyboardButton("⬅️ Back", callback_data="buy_back")],
            [InlineKeyboardButton("❌ Cancel", callback_data="buy_cancel")]
        ])
        
        await callback_query.message.edit_text(
            f"💰 **Crypto Payment**\n\n"
            f"**Plan:** {plan_name}\n"
            f"**Duration:** {duration} day(s)\n"
            f"**Amount:** ≈ ${price_usd} USD\n\n"
            f"**📱 Payment Steps:**\n"
            f"1. Click 'Contact Admin' button below\n"
            f"2. Send this message to admin:\n\n"
            f"```\n"
            f"🔹 Purchase Request\n"
            f"User ID: {user_id}\n"
            f"Plan: {plan_name}\n"
            f"Duration: {duration} days\n"
            f"Amount: ${price_usd} USD\n\n"
            f"I want to pay with: [Your Crypto Choice]\n"
            f"(Bitcoin/USDT/ETH/etc.)\n"
            f"```\n\n"
            f"3. Admin will provide crypto address\n"
            f"4. Send payment and share transaction ID\n"
            f"5. Admin will verify and send redeem code\n\n"
            f"⚠️ **Please specify which cryptocurrency you prefer!**",
            reply_markup=keyboard
        )
        return


# Admin command to configure UPI
@Client.on_message(filters.command("setupi") & filters.private)
async def set_upi_command(client: Client, message: Message):
    """Admin command to set UPI payment details"""
    from config import ADMINS
    
    if message.from_user.id not in ADMINS:
        await message.reply_text("❌ This command is for admins only!")
        return
    
    parts = message.text.split(maxsplit=2)
    if len(parts) != 3:
        await message.reply_text(
            "❌ **Invalid Usage!**\n\n"
            "**Format:** `/setupi <upi_id> <bank_name>`\n\n"
            "**Example:** `/setupi someone@paytm PayTM Bank`"
        )
        return
    
    upi_id = parts[1]
    bank_name = parts[2]
    
    # Store in database
    bot_config_collection.update_one(
        {"setting_name": "upi_payment"},
        {"$set": {
            "upi_id": upi_id,
            "bank_name": bank_name,
            "updated_at": datetime.utcnow()
        }},
        upsert=True
    )
    
    await message.reply_text(
        f"✅ **UPI Payment Configured!**\n\n"
        f"**UPI ID:** `{upi_id}`\n"
        f"**Bank Name:** {bank_name}\n\n"
        f"Users can now purchase premium using UPI!"
    )
