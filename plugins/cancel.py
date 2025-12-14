from pyrogram import Client, filters
from pyrogram.types import Message


# Dictionary to store ongoing processes
user_processes = {}


@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client: Client, message: Message):
    """Handle /cancel command to stop ongoing processes instantly"""
    user_id = message.from_user.id
    
    if user_id not in user_processes or not user_processes[user_id].get('active'):
        await message.reply_text("❌ No ongoing process to cancel.")
        return
    
    # Mark process for cancellation INSTANTLY
    user_processes[user_id]['cancel_requested'] = True
    user_processes[user_id]['active'] = False  # Mark as inactive immediately
    
    await message.reply_text("✅ **Cancellation initiated!**\n\nYour process is being stopped...")


def start_process(user_id, process_type, **kwargs):
    """Register a new process for a user"""
    user_processes[user_id] = {
        'active': True,
        'cancel_requested': False,
        'type': process_type,
        **kwargs
    }


def end_process(user_id):
    """End a process for a user"""
    if user_id in user_processes:
        user_processes[user_id]['active'] = False


def is_cancelled(user_id):
    """Check if user requested cancellation"""
    if user_id in user_processes:
        return user_processes[user_id].get('cancel_requested', False)
    return False


def get_active_processes():
    """Get all active processes"""
    active = []
    for user_id, process in user_processes.items():
        if process.get('active'):
            active.append({
                'user_id': user_id,
                **process
            })
    return active
