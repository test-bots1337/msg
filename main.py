import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.messages import GetDialogFiltersRequest
from telethon.tl.types import MessageEntityCustomEmoji
import time
from telethon.tl.types import DialogFilter

# --- НАСТРОЙКИ ---
api_id = 123 # ваш api_id
api_hash = ""  # ваш api_hash
string_session = StringSession("")  # вставьте сессию после первого входа

# --- РАССЫЛКА ---
MESSAGE_DELAY_MS = 2000

message_text = """🤑@Mvlnt и @blamins🤑 представляют:

🤑Скупаем бачи/баксы✉️

📷От 2$ - 74₽
🖼От 5$ - 75₽
📹От 10$ - 76₽
🧠От 50$ - 77₽
🧠От 100$ - 78₽

🙀Бюджет не бесконечен пишите в ЛС.
😹Идём онли гарантов чата.
😻Скам - даже не пробуйте(не теряйте свое время)"""

emoji_data = [
    {"placeholder": "🤑", "id": 5449535362219132702},
    {"placeholder": "🤑", "id": 5350716797622442220},
    {"placeholder": "🤑", "id": 5249054346200509700},
    {"placeholder": "✉️", "id": 5350291836378307462},
    {"placeholder": "📷", "id": 5278410301639769147},
    {"placeholder": "🖼", "id": 5280774517927457293},
    {"placeholder": "📹", "id": 5278589573574703984},
    {"placeholder": "🧠", "id": 5280803680755398454},
    {"placeholder": "🧠", "id": 5278578595638295143},
    {"placeholder": "🙀", "id": 4947487705752667417},
    {"placeholder": "😹", "id": 4949885177972131362},
    {"placeholder": "😻", "id": 4947697806962852817},
]


def create_entities(text, data):
    entities = []
    used_indices = set()
    for emoji in data:
        start = 0
        while True:
            index = text.find(emoji["placeholder"], start)
            if index == -1:
                break
            if index not in used_indices:
                entities.append(MessageEntityCustomEmoji(
                    offset=index,
                    length=len(emoji["placeholder"]),
                    document_id=emoji["id"]
                ))
                used_indices.add(index)
                break
            start = index + 1
    return entities


async def main():
    client = TelegramClient(string_session, api_id, api_hash)

    await client.start()
    print("✅ Клиент запущен.")
    print("🔑 Ваша строка сессии (сохраните):")
    print(f'"{client.session.save()}"\n')

    filters = await client(GetDialogFiltersRequest())
    custom_folders = [f for f in filters.filters if isinstance(f, DialogFilter)]

    if not custom_folders:
        print("❌ Нет созданных папок.")
        return

    print("\n--- Ваши папки ---")
    for folder in custom_folders:
        print(f'ID: {folder.id}, Название: "{folder.title.text}"')
    print("-------------------")

    folder_id = int(input("Введите ID папки для рассылки: "))
    target_folder = next((f for f in custom_folders if f.id == folder_id), None)

    if not target_folder:
        print("❌ Папка не найдена.")
        return

    peers = target_folder.include_peers
    print(f"\n📨 Найдено {len(peers)} чатов. Рассылка начинается...\n")

    message_entities = create_entities(message_text, emoji_data)

    for peer in peers:
        try:
            entity = await client.get_entity(peer)
            title = getattr(entity, 'title', None) or getattr(entity, 'username', None) or f"ID {getattr(entity, 'user_id', 'неизв')}"
            await client.send_message(
                entity,
                message=message_text,
                formatting_entities=message_entities
            )
            print(f"✅ Отправлено в: {title}")
        except FloodWaitError as e:
            print(f"⏳ FloodWait: ждем {e.seconds} сек...")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"⚠️ Ошибка при отправке: {e}")
        await asyncio.sleep(MESSAGE_DELAY_MS / 1000)

    print("\n🏁 Рассылка завершена.")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
