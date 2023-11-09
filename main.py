from datetime import datetime
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = 'Token'
BOT_USERNAME = '@Price_Announcer_bot'
api_key = 'api_key'
endpoint = 'latest'

url = f'http://api.exchangeratesapi.io/v1/{endpoint}?access_key={api_key}'


async def post_exchange_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(url)

        status_code = response.status_code
        if status_code == 200:
            json_data = response.json()

            rates = json_data.get('rates')
            if rates is not None:
                response_text = "Exchange Rates:\n"
                for currency, rate in rates.items():
                    response_text += f"{currency}: {rate:.2f}\n"

                await update.message.reply_text(response_text)

            base_currency = json_data.get('base')
            if base_currency is not None:
                await update.message.reply_text(f"Base Currency: {base_currency}")

            timestamp = json_data.get('timestamp')
            if timestamp is not None:
                date = datetime.fromtimestamp(timestamp)
                formatted_date = date.strftime("%Y-%m-%d %H:%M:%S")
                await update.message.reply_text(f"Time: {formatted_date}")

        else:
            await update.message.reply_text(
                f"Failed to retrieve exchange rates. Status Code: {status_code}\nResponse Content: {response.text}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("type /exchangerates to get the online currency prices")


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("type /help")


def handle_response(text: str) -> str:
    text: str = text.lower()

    if 'hello' in text:
        return 'Hello, please type /help '

    return 'Invalid command'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print('BOT:', response)
    await update.message.reply_text(response)


async def error(update: Update, context:ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':

    print('starting bot')
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('exchangerates', post_exchange_rates))

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=3)
