import os
import asyncio
from datetime import datetime, timezone, timedelta
from colorama import Fore, Style, Back, init
from telethon import TelegramClient, events
from telethon.errors import UserAlreadyParticipantError, UserNotParticipantError
from telethon.tl.functions.channels import JoinChannelRequest, GetParticipantRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

# Initialize colorama
init(autoreset=True)

### BOT ###
API_ID = 'API-BOT'
API_HASH = 'API-HASH'
SESSION_NAME = 'my_account'

### ADMIN ###
SOURCE_CHAT = 'me'
MESSAGE_IDS = [999999] #ID MESSAGE YANG SUDAH DI AMBIL DARI ID.PY
ADMIN_ID = 999999 #UBAH MENJADI ID TELEGRAM ADMIN

DESTINATION_CHATS_FILE = "destination_chats.txt"
DESTINATION_CHATS = []

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
is_running = False
last_send_time = None

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Print a beautiful header"""
    clear_screen()  # bersihkan layar setiap ada perintah admin
    print(f"\n{Fore.CYAN}{Style.BRIGHT}╔{'═' * (len(title) + 2)}╗")
    print(f"║ {title} ║")
    print(f"╚{'═' * (len(title) + 2)}╝{Style.RESET_ALL}")

def print_status(message, status_type="info"):
    """Print colored status messages"""
    colors = {
        "info": Fore.CYAN,
        "success": Fore.GREEN + Style.BRIGHT,
        "warning": Fore.YELLOW,
        "error": Fore.RED + Style.BRIGHT,
        "admin": Fore.MAGENTA,
        "system": Fore.BLUE
    }
    timestamp = get_current_time_gmt7()
    print(f"{colors[status_type]}[{timestamp}] {message}{Style.RESET_ALL}")

def print_command(message):
    """Print admin commands distinctly"""
    timestamp = get_current_time_gmt7()
    print(f"{Fore.MAGENTA}{Style.BRIGHT}>>> [{timestamp}] ADMIN COMMAND: {message}{Style.RESET_ALL}")

def get_current_time_gmt7():
    gmt7 = timezone(timedelta(hours=7))
    return datetime.now(gmt7).strftime('%H:%M:%S')

def save_destination_chats():
    with open(DESTINATION_CHATS_FILE, "w") as f:
        for chat in DESTINATION_CHATS:
            f.write(chat + "\n")

def load_destination_chats():
    if os.path.exists(DESTINATION_CHATS_FILE):
        with open(DESTINATION_CHATS_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]
    return []

DESTINATION_CHATS = load_destination_chats()

async def forward_messages_to_all_groups():
    global last_send_time
    last_send_time = get_current_time_gmt7()
    
    print_header("STARTING MESSAGE FORWARDING")
    print_status("Fetching messages from Saved Messages...", "info")
    
    success_count = 0
    fail_count = 0
    failed_groups = []

    try:
        messages = await client.get_messages(SOURCE_CHAT, ids=MESSAGE_IDS)
        if not messages:
            print_status("No messages found in Saved Messages", "error")
            return

        print_status(f"Starting forwarding to {len(DESTINATION_CHATS)} groups...", "info")
        
        for group in DESTINATION_CHATS:
            print_status(f"Sending to: {group}", "info")
            try:
                try:
                    entity = await client.get_entity(group)
                except ValueError:
                    print_status(f"Invalid group: {group}", "error")
                    failed_groups.append(group)
                    fail_count += 1
                    continue

                try:
                    await client(GetParticipantRequest(entity, 'me'))
                except UserNotParticipantError:
                    print_status(f"Bot not in group: {group}", "warning")
                    failed_groups.append(group)
                    fail_count += 1
                    continue

                await client.forward_messages(entity, messages)
                print_status(f"Successfully sent to {group}", "success")
                success_count += 1

            except Exception as group_error:
                print_status(f"Failed to send to {group}: {group_error}", "error")
                failed_groups.append(f"{group} - {str(group_error)}")
                fail_count += 1

        print_header("FORWARDING REPORT")
        print_status(f"Success: {success_count}", "success")
        print_status(f"Failed: {fail_count}", "error" if fail_count > 0 else "success")
        
        report = (
            f"📊 Forwarding Report:\n"
            f"✅ Success: {success_count}\n"
            f"❌ Failed: {fail_count}\n"
            f"🕒 Time: {get_current_time_gmt7()}"
        )

        if failed_groups:
            report += "\n\n🔴 Failed groups:\n" + "\n".join(failed_groups)

        await client.send_message(ADMIN_ID, report)
        print_status("Report sent to admin", "success")

    except Exception as e:
        error_msg = f"General error: {e}"
        print_status(error_msg, "error")
        await client.send_message(ADMIN_ID, f"🚨 {error_msg}")

@client.on(events.NewMessage(from_users=ADMIN_ID))
async def handler(event):
    global is_running, last_send_time
    message = event.raw_text.strip()

    print_command(message)

    if message.lower() == "/status":
        status = "ACTIVE" if is_running else "INACTIVE"
        color = "success" if is_running else "warning"
        await event.reply(f"📊 Bot status: {status.lower()}")
        print_header(f"BOT STATUS: {status}")
        print_status(f"Current status: {status}", color)

    elif message.lower() == "/stop":
        is_running = False
        last_send_time = None
        await event.reply("🛑 Forwarding paused.")
        print_header("FORWARDING STOPPED")
        print_status("Admin paused forwarding", "warning")

    elif message.lower() == "/start":
        is_running = True
        await event.reply("▶️ Forwarding resumed.")
        print_header("FORWARDING STARTED")
        print_status("Admin resumed forwarding", "success")

    elif message.lower() == "/now":
        waktu = get_current_time_gmt7()
        status = "ACTIVE" if is_running else "INACTIVE"
        color = "success" if is_running else "warning"
        await event.reply(f"🕒 Now: {waktu}\n📊 Status: {status.lower()}")
        print_header("CURRENT STATUS")
        print_status(f"Time: {waktu}, Status: {status}", color)

    elif message.lower() == "/lastsend":
        if last_send_time:
            await event.reply(f"📤 Last sent: {last_send_time}")
            print_header("LAST SEND TIME")
            print_status(f"Last message sent at: {last_send_time}", "info")
        else:
            await event.reply("📤 No send record yet.")
            print_status("No messages sent yet", "warning")

    elif message.lower() == "/help":
        help_msg = (
            "📘 Available commands:\n"
            "/status - Check bot status\n"
            "/start - Start forwarding\n"
            "/stop - Pause forwarding\n"
            "/now - Check time & status\n"
            "/lastsend - Last send time\n"
            "/help - Help\n"
            "/listgroups - List groups\n"
            "/clean - Clean invalid groups\n"
            "Send group link (t.me/...) to join"
        )
        await event.reply(help_msg)
        print_header("HELP MENU")
        print_status("Displayed help menu to admin", "info")

    elif message.lower() == "/clean":
        print_header("CLEANING GROUP LIST")
        print_status("Starting group list cleanup", "info")
        
        valid_chats = []
        removed_chats = []

        for chat in DESTINATION_CHATS:
            try:
                entity = await client.get_entity(chat)
                await client(GetParticipantRequest(entity, 'me'))
                valid_chats.append(chat)
            except Exception as e:
                removed_chats.append(f"{chat} (reason: {str(e)})")

        DESTINATION_CHATS[:] = valid_chats
        save_destination_chats()

        reply_msg = f"🧹 Cleaned!\nValid groups: {len(DESTINATION_CHATS)}"
        if removed_chats:
            reply_msg += "\n\nRemoved groups:\n" + "\n".join(removed_chats)

        await event.reply(reply_msg)
        
        print_header("CLEANUP COMPLETE")
        print_status(f"Valid groups remaining: {len(DESTINATION_CHATS)}", "success")
        if removed_chats:
            print_status(f"Removed groups: {len(removed_chats)}", "warning")
            for removed in removed_chats:
                print_status(f"- {removed}", "warning")

    elif message.lower() in ["/listgroups", "/list"]:
        print_header("GROUP LIST")
        if DESTINATION_CHATS:
            daftar = "\n".join(f"{i+1}. {chat}" for i, chat in enumerate(DESTINATION_CHATS))
            await event.reply(f"📃 Groups in destination_chats.txt:\n\n{daftar}")
            print_status(f"Showing {len(DESTINATION_CHATS)} groups:", "info")
            for i, chat in enumerate(DESTINATION_CHATS, 1):
                print_status(f"{i}. {chat}", "info")
        else:
            await event.reply("ℹ️ No groups in destination_chats.txt.")
            print_status("No groups saved yet", "warning")

    else:
        links = message.split()
        for link in links:
            if link.startswith("https://t.me/") or link.startswith("t.me/"):
                print_header(f"PROCESSING GROUP: {link}")
                if link not in DESTINATION_CHATS:
                    DESTINATION_CHATS.append(link)
                    save_destination_chats()
                    print_status(f"New group added: {link}", "success")

                try:
                    username = link.split('/')[-1]
                    if '/joinchat/' in link or '+' in link:
                        invite_hash = link.split('+')[-1]
                        await client(ImportChatInviteRequest(invite_hash))
                        await asyncio.sleep(2)
                    else:
                        entity = await client.get_entity(username)
                        try:
                            await client(GetParticipantRequest(entity, 'me'))
                        except UserNotParticipantError:
                            await client(JoinChannelRequest(entity))
                            await asyncio.sleep(2)

                    entity = await client.get_entity(username)
                    await client(GetParticipantRequest(entity, 'me'))
                    await event.reply(f"✅ Joined: {link}")
                    print_status(f"Successfully joined: {link}", "success")

                except UserAlreadyParticipantError:
                    await event.reply(f"✅ Already joined: {link}")
                    print_status(f"Already in group: {link}", "info")
                except Exception as e:
                    await event.reply(f"❌ Failed to join {link}: {str(e)}")
                    print_status(f"Failed to join {link}: {str(e)}", "error")

async def main():
    print_header("TELEGRAM FORWARDER BOT - NEXA TOOLS V1.0")
    print_status("Initializing bot...", "system")

    await client.start()
    print_status("Logged in to Telegram account", "success")
    print_status(f"Current time (GMT+7): {get_current_time_gmt7()}", "info")
    print_header("BOT READY")
    print_status("Waiting for admin commands...", "system")

    last_status = None
    while True:
        if is_running:
            if last_status != "running":
                print_header("FORWARDING STARTED")
                print_status("Bot started forwarding", "success")
                last_status = "running"
            await forward_messages_to_all_groups()
            print_status("Waiting 60 minutes for next cycle...", "info")
            await asyncio.sleep(60 * 60)
        else:
            if last_status != "stopped":
                print_header("FORWARDING PAUSED")
                print_status("Bot waiting for /start command", "warning")
                last_status = "stopped"
            await asyncio.sleep(10)

if __name__ == '__main__':
    try:
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        print_header("BOT STOPPED")
        print_status("Bot stopped by user", "error")
    except Exception as e:
        print_header("ERROR OCCURRED")
        print_status(f"Error: {e}", "error")
    finally:
        print_header("CLEANING UP")
        print_status("Disconnecting...", "system")
        client.loop.run_until_complete(client.disconnect())