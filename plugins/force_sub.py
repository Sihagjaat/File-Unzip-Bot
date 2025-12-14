from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.database import force_sub_channels_collection


async def check_force_subscription(client: Client, user_id: int):
    """
    Check if user is subscribed to all force sub channels
    Returns: (is_subscribed: bool, buttons: InlineKeyboardMarkup)
    """
    channels = list(force_sub_channels_collection.find())
    
    if not channels:
        return True, None
    
    not_subscribed = []
    buttons_list = []
    
    for channel in channels:
        try:
            member = await client.get_chat_member(channel['channel_id'], user_id)
            if member.status in ['left', 'kicked']:
                not_subscribed.append(channel)
        except Exception:
            not_subscribed.append(channel)
    
    if not_subscribed:
        # Create join buttons
        for channel in not_subscribed:
            try:
                chat = await client.get_chat(channel['channel_id'])
                invite_link = chat.invite_link
                if not invite_link:
                    # Try to export invite link if bot is admin
                    try:
                        invite_link = await client.export_chat_invite_link(channel['channel_id'])
                    except:
                        invite_link = f"https://t.me/c/{str(channel['channel_id'])[4:]}"
                
                channel_title = channel.get('channel_title') or chat.title
                buttons_list.append([InlineKeyboardButton(f"Join {channel_title}", url=invite_link)])
            except:
                pass
        
        # Add verification button
        buttons_list.append([InlineKeyboardButton("✅ I Joined, Verify", callback_data="verify_subscription")])
        
        buttons = InlineKeyboardMarkup(buttons_list)
        return False, buttons
    
    return True, None


@Client.on_callback_query(filters.regex("verify_subscription"))
async def verify_subscription_callback(client: Client, callback_query):
    """Handle subscription verification callback"""
    user_id = callback_query.from_user.id
    
    is_subscribed, buttons = await check_force_subscription(client, user_id)
    
    if is_subscribed:
        await callback_query.message.edit_text("✅ Thank you! You can now use the bot.\nSend /help to see available commands.")
    else:
        await callback_query.answer("❌ Please join all channels first!", show_alert=True)
        await callback_query.message.edit_reply_markup(buttons)
