import os
import logging
from typing import Dict, Optional
from urllib.parse import quote, urljoin

import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)

# ------------------------
# Configuración
# ------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("Falta la variable TELEGRAM_TOKEN en el archivo .env")
API_BASE = os.getenv("API_BASE", "https://framex.with-madrid.dev/api/")
VIDEO_NAME = os.getenv(
    "VIDEO_NAME", "Falcon Heavy Test Flight (Hosted Webcast)-wbSwFU6tY1c"
)


# ------------------------
# Cliente para FrameX
# ------------------------
class FrameX:
    def __init__(self, base_url: str = API_BASE):
        self.base_url = base_url.rstrip("/")

    async def get_video_info(self, video: str):
        url = urljoin(self.base_url + "/", f"video/{quote(video)}/")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                resp.raise_for_status()
                return await resp.json()

    def frame_url(self, video: str, frame: int) -> str:
        return urljoin(
            self.base_url + "/", f"video/{quote(video)}/frame/{quote(str(frame))}/"
        )


# ------------------------
# Búsqueda de bisección
# ------------------------
class BisectionSearch:
    def __init__(self, total_frames: int):
        self.left = 0
        self.right = total_frames - 1
        self.last_frame: Optional[int] = None

    def next_frame(self) -> Optional[int]:
        if self.left + 1 >= self.right:
            return None
        mid = (self.left + self.right) // 2
        self.last_frame = mid
        return mid

    def record_answer(self, frame: int, launched: bool):
        if launched:
            self.right = min(self.right, frame)
        else:
            self.left = max(self.left, frame)

    def is_finished(self) -> bool:
        return self.left + 1 >= self.right

    def result(self) -> int:
        return self.right


USER_ACTIONS: Dict[int, BisectionSearch] = {}
framex = FrameX()


# ------------------------
# Funciones del bot
# ------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hola, soy RocketFinderBot.\n\n"
        "Mi trabajo es ayudarte a encontrar el momento exacto en el que un cohete despega en un video.\n"
        "Funciona de forma muy sencilla: te enseñaré imágenes y tú me dirás si ya ha despegado o no.\n\n"
        "Cuando quieras empezar, escribe /newtest."
    )


async def newtest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    video = await framex.get_video_info(VIDEO_NAME)
    total_frames = video["frames"]

    USER_ACTIONS[user_id] = BisectionSearch(total_frames)

    await update.message.reply_text(
        f"He preparado una nueva búsqueda para ti.\n\n"
        f"Video: {VIDEO_NAME}\n"
        f"Total de imágenes: {total_frames}\n\n"
        "A partir de ahora te iré enseñando capturas del video. Tú solo tendrás que decirme si el cohete ya despegó o todavía no."
    )

    await send_next_frame(context, user_id)


async def send_next_frame(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    action = USER_ACTIONS.get(user_id)
    if not action:
        await context.bot.send_message(
            chat_id=user_id,
            text="No tienes ninguna búsqueda activa en este momento. Escribe /newtest para comenzar una."
        )
        return

    frame = action.next_frame()
    if frame is None:
        result = action.result()
        url = framex.frame_url(VIDEO_NAME, result)
        await context.bot.send_photo(
            chat_id=user_id,
            photo=url,
            caption=f"Hemos terminado. El cohete comienza a despegar en el frame {result}."
        )
        USER_ACTIONS.pop(user_id, None)
        return

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Sí, ya despegó", callback_data=f"ans:{frame}:1"),
                InlineKeyboardButton("No, todavía no", callback_data=f"ans:{frame}:0"),
            ]
        ]
    )

    url = framex.frame_url(VIDEO_NAME, frame)
    await context.bot.send_photo(
        chat_id=user_id,
        photo=url,
        caption=f"Estamos en el frame {frame}.\n\n¿El cohete ya despegó?",
        reply_markup=keyboard,
    )


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    if not query.data.startswith("ans:"):
        return

    _, frame_str, val_str = query.data.split(":")
    frame = int(frame_str)
    launched = bool(int(val_str))

    action = USER_ACTIONS.get(user_id)
    if not action:
        await query.message.reply_text("Ahora mismo no tienes ninguna búsqueda activa. Escribe /newtest para empezar.")
        return

    action.record_answer(frame, launched)

    if action.is_finished():
        result = action.result()
        url = framex.frame_url(VIDEO_NAME, result)
        await context.bot.send_photo(
            chat_id=user_id,
            photo=url,
            caption=f"Ya tenemos la respuesta: el cohete despegó en el frame {result}."
        )
        USER_ACTIONS.pop(user_id, None)
        return

    await send_next_frame(context, user_id)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    USER_ACTIONS.pop(user_id, None)
    await update.message.reply_text(
        "Has cancelado la búsqueda. Si quieres empezar otra más adelante, simplemente escribe /newtest."
    )


# ------------------------
# Main
# ------------------------
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("newtest", newtest))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(handle_answer))

    logger.info("Bot iniciado.")
    app.run_polling()


if __name__ == "__main__":
    main()
