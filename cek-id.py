from telethon import TelegramClient

# Konfigurasi API Telegram
API_ID = '9999999' 
API_HASH = '9999999'
SESSION_NAME = 'my_account'

# Saved Messages alias
SOURCE_CHAT = 'me'  # Saved Messages atau username grup/channel lainnya

# Buat sesi Telegram
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def get_message_id():
    """
    Ambil pesan terbaru dari SOURCE_CHAT dan cetak ID pesan.
    """
    await client.start()
    messages = await client.get_messages(SOURCE_CHAT, limit=5)  # Ambil 5 pesan terbaru
    for msg in messages:
        print(f"ID Pesan: {msg.id}, Isi Pesan: {msg.text if msg.text else 'Media'}")

with client:
    client.loop.run_until_complete(get_message_id())
