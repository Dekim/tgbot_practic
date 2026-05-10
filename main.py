import os
import time

import requests
import telebot
from telebot import apihelper

BOT_TOKEN = "8778972764:AAGwbeTLfB-YisnyeKhcieWqR3ihol-7qJY"
OWM_API_KEY = "9455d981b0e1a3288dc4538766f2ae48"

bot = telebot.TeleBot(BOT_TOKEN)
OWM_URL = "https://api.openweathermap.org/data/2.5/weather"


def configure_telegram_proxy() -> None:
    proxy_url = os.getenv("TG_PROXY")
    if proxy_url:
        apihelper.proxy = {"https": proxy_url}
        print("Прокси для Telegram включен (TG_PROXY).")


def get_weather_emoji(weather_main: str) -> str:
    weather_map = {
        "Clear": "☀️",
        "Clouds": "☁️",
        "Rain": "🌧",
        "Drizzle": "🌦",
        "Thunderstorm": "⛈",
        "Snow": "❄️",
        "Mist": "🌫",
        "Fog": "🌫",
        "Haze": "🌫",
        "Smoke": "🌫",
        "Dust": "🌪",
        "Sand": "🌪",
        "Ash": "🌋",
        "Squall": "💨",
        "Tornado": "🌪",
    }
    return weather_map.get(weather_main, "🌍")


def get_weather(city_name: str) -> str:
    params = {
        "q": city_name,
        "appid": OWM_API_KEY,
        "units": "metric",
        "lang": "ru",
    }

    try:
        response = requests.get(OWM_URL, params=params, timeout=10)
        data = response.json()
        if response.status_code != 200 or data.get("cod") != 200:
            return "❌ Город не найден. Проверьте название и попробуйте снова."
        city = data["name"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        weather_description = data["weather"][0]["description"]
        weather_main = data["weather"][0]["main"]

        emoji = get_weather_emoji(weather_main)
        result = (
            f"{emoji} Погода в городе: {city}\n\n"
            f"🌡 Температура: {temp}°C\n"
            f"🤗 Ощущается как: {feels_like}°C\n"
            f"💧 Влажность: {humidity}%\n"
            f"💨 Скорость ветра: {wind_speed} м/с\n"
            f"📝 Описание: {weather_description.capitalize()}"
        )
        return result

    except requests.exceptions.RequestException:
        return "⚠️ Ошибка сети при запросе погоды. Попробуйте позже."
    except Exception:
        return "⚠️ Произошла непредвиденная ошибка. Попробуйте позже."


@bot.message_handler(commands=["start"])
def send_start(message):
    bot.reply_to(
        message,
        "Привет! 👋\n"
        "Я бот погоды.\n"
        "Просто отправь название города (например: Москва или London), "
        "и я пришлю текущую погоду.",
    )


@bot.message_handler(commands=["help"])
def send_help(message):
    bot.reply_to(
        message,
        "📌 Доступные команды:\n"
        "/start — приветствие\n"
        "/help — список команд\n\n"
        "Также можно просто отправить название города.",
    )


@bot.message_handler(func=lambda message: True)
def handle_city(message):
    city_name = message.text.strip()
    if not city_name:
        bot.reply_to(message, "Введите название города.")
        return

    weather_text = get_weather(city_name)
    bot.reply_to(message, weather_text)


if __name__ == "__main__":
    configure_telegram_proxy()
    print("Бот запущен...")
    while True:
        try:
            bot.infinity_polling(skip_pending=True, timeout=20, long_polling_timeout=20)
        except Exception as error:
            print(f"Сбой подключения к Telegram API: {error}")
            print("Повторная попытка через 10 секунд...")
            time.sleep(10)
