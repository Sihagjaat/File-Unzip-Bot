# Telegram Unzip Bot - Deployment Guide

## Prerequisites
- Linux server (Ubuntu 20.04+ recommended)
- Python 3.12+
- MongoDB installed and running
- UnRAR utility (for RAR file support)

## Installation Steps

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Dependencies
```bash
# Install Python 3.12+ (if not already installed)
sudo apt install python3 python3-pip python3-venv -y

# Install UnRAR for RAR file support
sudo apt install unrar -y

# Install MongoDB (if not already installed)
# Follow: https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/
```

### 3. Clone/Upload Bot Files
```bash
# Create directory
mkdir -p ~/bots
cd ~/bots

# Upload your bot files to this directory
# You can use SCP, SFTP, or git clone
```

### 4. Create Virtual Environment
```bash
cd ~/bots/Unzip_File_Bot
python3 -m venv venv
source venv/bin/activate
```

### 5. Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Configure Environment Variables
```bash
# Create .env file
nano .env
```

Add the following (replace with your actual values):
```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
ADMINS=123456789,987654321
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=unzip_bot
DOWNLOAD_DIR=downloads
```

Save and exit (Ctrl+X, then Y, then Enter)

### 7. Test Run
```bash
# Make sure you're in the virtual environment
python3 bot.py
```

If it starts successfully, press Ctrl+C to stop it.

### 8. Setup as System Service (Recommended)

#### Edit service file:
```bash
sudo nano /etc/systemd/system/unzip_bot.service
```

Copy content from `unzip_bot.service` file and modify:
- Replace `YOUR_USERNAME` with your Linux username
- Replace `/path/to/Unzip_File_Bot` with actual path (e.g., `/home/ubuntu/bots/Unzip_File_Bot`)
- Replace `/usr/bin/python3` with your venv python: `/home/ubuntu/bots/Unzip_File_Bot/venv/bin/python3`

#### Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable unzip_bot
sudo systemctl start unzip_bot
```

#### Check status:
```bash
sudo systemctl status unzip_bot
```

#### View logs:
```bash
# Live logs
sudo journalctl -u unzip_bot -f

# Or check log files
sudo tail -f /var/log/unzip_bot.log
sudo tail -f /var/log/unzip_bot_error.log
```

### 9. Manage the Service

```bash
# Start
sudo systemctl start unzip_bot

# Stop
sudo systemctl stop unzip_bot

# Restart
sudo systemctl restart unzip_bot

# View status
sudo systemctl status unzip_bot

# Disable auto-start
sudo systemctl disable unzip_bot
```

## Firewall Configuration
```bash
# If using UFW firewall, allow MongoDB port (if MongoDB is on same server)
sudo ufw allow 27017/tcp

# No need to open ports for the bot itself (it connects outbound to Telegram)
```

## MongoDB Configuration

### If MongoDB is on the same server:
```env
MONGODB_URI=mongodb://localhost:27017/
```

### If MongoDB is on a different server:
```env
MONGODB_URI=mongodb://username:password@host:27017/database?authSource=admin
```

## Setting Up UPI Payment (Admin Command)
After deployment, as admin, run:
```
/setupi your_upi_id@provider Bank Name
```

## Troubleshooting

### Bot not starting:
```bash
# Check logs
sudo journalctl -u unzip_bot -n 50

# Check if MongoDB is running
sudo systemctl status mongod

# Check if all dependencies are installed
source venv/bin/activate
pip list
```

### Permission errors:
```bash
# Ensure downloads directory exists and is writable
mkdir -p downloads
chmod 755 downloads
```

### Session file errors:
```bash
# Remove old session file
rm -f unzip_bot.session*
```

## Updating the Bot

```bash
# Stop the service
sudo systemctl stop unzip_bot

# Update code
cd ~/bots/Unzip_File_Bot
git pull  # or upload new files

# Update dependencies if needed
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl start unzip_bot
```

## Performance Optimization

### For high-traffic bots:
1. **Use MongoDB replica set** for better performance
2. **Increase worker count** in bot.py (already set to 8)
3. **Use SSD storage** for downloads directory
4. **Increase file descriptors limit**:
   ```bash
   sudo nano /etc/security/limits.conf
   ```
   Add:
   ```
   * soft nofile 65536
   * hard nofile 65536
   ```

## Security Best Practices

1. **Never commit .env file** to version control
2. **Use strong MongoDB passwords**
3. **Keep Python and dependencies updated**
4. **Regularly monitor logs** for suspicious activity
5. **Limit admin access** to trusted users only
6. **Use firewall** to restrict unnecessary access

## Backup

### Backup MongoDB database:
```bash
mongodump --db unzip_bot --out ~/backups/$(date +%Y%m%d)
```

### Restore MongoDB database:
```bash
mongorestore --db unzip_bot ~/backups/20231214/unzip_bot
```

## Support

For issues or questions, check:
- Bot logs: `sudo journalctl -u unzip_bot -f`
- MongoDB logs: `sudo journalctl -u mongod -f`
- Python errors in: `/var/log/unzip_bot_error.log`
