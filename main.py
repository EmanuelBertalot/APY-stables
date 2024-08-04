import json
import requests
from telegram import Bot
from telegram.ext import Application, ApplicationBuilder, CommandHandler
import asyncio

# URL del archivo JSON
JSON_URL = 'https://raw.githubusercontent.com/enzonotario/esjs-argentina-datos-api/main/datos/v1/finanzas/rendimientos/index.json'

# Token de tu bot de Telegram
TELEGRAM_TOKEN = '7219866535:AAH-Ykrtp8iQJE_PIqvtsSWrGCEszxXtopE'
CHAT_ID = '798183117'  # Reemplaza con tu chat_id

def get_stablecoin_yield():
    """Obtiene los datos de rendimiento de la API."""
    try:
        response = requests.get(JSON_URL)
        response.raise_for_status()
        data = response.json()

        yield_data = {}
        for item in data:
            exchange = item['entidad']
            rates = {}
            for rate_item in item['rendimientos']:
                moneda = rate_item['moneda']
                apy = rate_item['apy']
                rates[moneda] = apy
            yield_data[exchange] = rates
        return yield_data
    except requests.RequestException as e:
        print(f"Error al acceder a la API: {e}")
        return None

def get_best_yields(yield_data):
    """Analiza los rendimientos y retorna los mejores para cada stablecoin."""
    best_yields = {}
    changes = []
    for stablecoin in ["USDC", "USDT", "DAI"]:
        best_exchange = None
        highest_yield = 0
        for exchange, rates in yield_data.items():
            if rates.get(stablecoin, 0) > highest_yield:
                highest_yield = rates.get(stablecoin, 0)
                best_exchange = exchange
        best_yields[stablecoin] = (best_exchange, highest_yield)

    return best_yields

async def send_telegram_notification(bot, message):
    """Envía las notificaciones de los mejores rendimientos a Telegram."""
    await bot.send_message(chat_id=CHAT_ID, text=message)

async def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    previous_yields = {}

    while True:
        yield_data = get_stablecoin_yield()
        if yield_data:
            best_yields = get_best_yields(yield_data)
            message = "Mejores rendimientos actuales:\n"
            for stablecoin, (exchange, apy) in best_yields.items():
                message += f"{stablecoin}: {apy}% en {exchange}\n"
            await send_telegram_notification(bot, message)
        await asyncio.sleep(300)

if __name__ == '__main__':
    asyncio.run(main())