import sys
import asyncio
import logging
import traceback
import threading
import logging.handlers as handlers
from http.server import BaseHTTPRequestHandler, HTTPServer

from FileStream.config import Telegram, Server
from aiohttp import web
from pyrogram import idle

from FileStream.bot import FileStream
from FileStream.server import web_server
from FileStream.bot.clients import initialize_clients

logging.basicConfig(
    level=logging.INFO,
    datefmt="%d/%m/%Y %H:%M:%S",
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(stream=sys.stdout),
              handlers.RotatingFileHandler("streambot.log", mode="a", maxBytes=104857600, backupCount=2, encoding="utf-8")],)

logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

server = web.AppRunner(web_server())

loop = asyncio.get_event_loop()


# ── Simple built-in HTTP health server on port 8080 ──────────────────────────

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = (
            "<!DOCTYPE html><html><head><title>FileStream Bot</title>"
            "<style>body{font-family:sans-serif;background:#0f1117;color:#e8eaf0;"
            "display:flex;align-items:center;justify-content:center;height:100vh;margin:0}"
            ".card{background:#1a1d27;border:1px solid #2e3250;border-radius:12px;"
            "padding:40px 48px;text-align:center}"
            "h1{color:#5865f2;margin-bottom:8px}p{color:#8b8fa8;margin:4px 0}"
            ".dot{display:inline-block;width:10px;height:10px;border-radius:50%;"
            "background:#3ba55d;margin-right:8px}"
            "</style></head><body>"
            "<div class='card'>"
            "<h1>FileStream Bot</h1>"
            "<p><span class='dot'></span>Online &amp; Running</p>"
            "<p>Telegram file streaming service is active.</p>"
            "</div></body></html>"
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass  # suppress request logs


def start_health_server():
    httpd = HTTPServer(("0.0.0.0", 8080), HealthHandler)
    httpd.serve_forever()


# ─────────────────────────────────────────────────────────────────────────────

async def start_services():
    print()
    if Telegram.SECONDARY:
        print("------------------ Starting as Secondary Server ------------------")
    else:
        print("------------------- Starting as Primary Server -------------------")
    print()
    print("-------------------- Initializing Telegram Bot --------------------")

    await FileStream.start()
    bot_info = await FileStream.get_me()
    FileStream.id = bot_info.id
    FileStream.username = bot_info.username
    FileStream.fname = bot_info.first_name
    print("------------------------------ DONE ------------------------------")
    print()
    print("---------------------- Initializing Clients ----------------------")
    await initialize_clients()
    print("------------------------------ DONE ------------------------------")
    print()
    print("------------------ Starting Health Server (8080) ------------------")
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    print("------------------------------ DONE ------------------------------")
    print()
    print("--------------------- Initializing Web Server ---------------------")
    await server.setup()
    await web.TCPSite(server, Server.BIND_ADDRESS, Server.PORT).start()
    print("------------------------------ DONE ------------------------------")
    print()
    print("------------------------- Service Started -------------------------")
    print("                        bot =>> {}".format(bot_info.first_name))
    if bot_info.dc_id:
        print("                        DC ID =>> {}".format(str(bot_info.dc_id)))
    print(" URL =>> {}".format(Server.URL))
    print(" Health =>> http://0.0.0.0:8080/")
    print("------------------------------------------------------------------")
    await idle()


async def cleanup():
    await server.cleanup()
    await FileStream.stop()


if __name__ == "__main__":
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        pass
    except Exception as err:
        logging.error(traceback.format_exc())
    finally:
        loop.run_until_complete(cleanup())
        loop.stop()
        print("------------------------ Stopped Services ------------------------")
