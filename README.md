# Telegram Unzip Bot

A powerful Telegram bot for extracting archive files with premium subscription support.

## Features

- 🗜️ Extract multiple archive formats (ZIP, RAR, 7Z, TAR, GZ, BZ2)
- 💎 Premium subscription system with UPI and Crypto payments
- 🔐 Password-protected archive support
- 📊 User quota management
- 👑 Admin panel with full control
- 💳 Auto-generated UPI QR codes
- 🎁 Redeem code system
- 📡 Force subscription to channels
- 📝 Detailed logging

## Supported Archive Formats

- `.zip` - ZIP archives
- `.rar` - RAR archives
- `.7z` - 7-Zip archives
- `.tar` - TAR archives
- `.gz` - GZIP archives
- `.bz2` - BZIP2 archives
- `.tgz`, `.tbz2` - Compressed TAR archives

## User Tiers

- 🆓 **Free**: 1 file/day, 1GB max
- 💎 **Premium**: 15 files/day, 2GB max
- ⭐ **Ultra Premium**: 50 files/day, 2GB max

## Commands

### User Commands
- `/start` - Start the bot
- `/help` - Get help information
- `/unzip` - Extract archive (reply to file)
- `/unzip "password"` - Extract password-protected archive
- `/myplan` - Check current subscription
- `/premium` - Purchase premium subscription
- `/redeem CODE` - Redeem premium code
- `/cancel` - Cancel ongoing process

### Admin Commands
- `/admin` - Show admin panel
- `/addpremium <user_id> <plan> <days>` - Grant premium
- `/removepremium <user_id>` - Remove premium
- `/premiumusers` - List all premium users
- `/generate` - Generate redeem codes
- `/listcodes` - View all redeem codes
- `/setupi <upi_id> <bank>` - Configure UPI payment
- `/setlogchannel` - Set log channel
- `/addforcesub` - Add force subscription channel
- `/removeforcesub` - Remove force sub channel
- `/stats` - View bot statistics
- `/processes` - View ongoing processes
- `/broadcast` - Broadcast message to all users
- `/exportusers` - Export user data as CSV

## Tech Stack

- **Language**: Python 3.12+
- **Framework**: Pyrogram
- **Database**: MongoDB
- **Archive Libraries**: py7zr, rarfile, zipfile, tarfile
- **QR Code**: qrcode, pillow

## Requirements

See `requirements.txt` for all dependencies.

## Deployment

See `DEPLOYMENT.md` for detailed deployment instructions.

## Configuration

Create a `.env` file with:
```env
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
BOT_TOKEN=your_bot_token
ADMINS=comma_separated_admin_ids
MONGODB_URI=your_mongodb_connection_string
DATABASE_NAME=unzip_bot
DOWNLOAD_DIR=downloads
```

## License

This project is for educational purposes.

## Support

For issues or feature requests, contact the bot admin.
