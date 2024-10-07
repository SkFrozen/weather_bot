import os
from datetime import datetime

import requests
import telebot
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

from models.base import engine
from models.user_country import UserCountry
from modules.my_module import get_countries_list

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
COUNTRIES_FILE = "countries.csv"

bot = telebot.TeleBot(SECRET_KEY, parse_mode=None)
session_pool = sessionmaker(bind=engine)
countries = get_countries_list(COUNTRIES_FILE)


@bot.message_handler(commands=["start", "help"])
def start_bot(message):
    bot.reply_to(
        message,
        "Hello! This bot is used to get weather forecast for a chosen country.\n"
        + "Use /choose commands to choose a country.\n"
        + "Use /weather <City name> to get current weather.",
    )


@bot.message_handler(commands=["choose"])
def choose_country(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for country in countries:
        markup.add(telebot.types.KeyboardButton(country))
    bot.reply_to(message, "Choose your country:", reply_markup=markup)


@bot.message_handler(commands=["country"])
def get_country(message):
    with session_pool() as session:
        user = UserCountry.get_user_country(
            user_id=message.from_user.id, session=session
        )
        if user:
            bot.reply_to(message, user.country)
        else:
            bot.reply_to(message, "You haven't chosen a country yet.")


@bot.message_handler(func=lambda message: message.text in countries)
def country_handler(message):
    country_and_iso = message.text.split("/")
    country = country_and_iso[0]
    iso = country_and_iso[1]
    user_id = message.from_user.id
    with session_pool() as session:
        user_country = UserCountry.get_user_country(user_id=user_id, session=session)
        if user_country:
            user_country.country = country
            user_country.country_iso_2 = iso
            session.commit()
        else:
            UserCountry.add(
                user_id=user_id, country=country, country_iso_2=iso, session=session
            )
    bot.send_message(
        message.chat.id,
        f"You choose {message.text}!",
        reply_markup=telebot.types.ReplyKeyboardRemove(),
    )


@bot.message_handler(commands=["weather"])
def weather_message(message):
    location = message.text.split()[1]
    with session_pool() as session:
        country_iso_2 = UserCountry.get_country(
            user_id=message.from_user.id, session=session
        )
    if not country_iso_2:
        bot.reply_to(message, "You have to choose a country")
    else:
        weather_api_url = f"http://api.openweathermap.org/data/2.5/weather?q={location},{country_iso_2}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(weather_api_url)
        if response.status_code == 200:
            weather_data = response.json()
            date = datetime.fromtimestamp(weather_data.get("dt"))
            sunrise = datetime.fromtimestamp(weather_data.get("sys").get("sunrise"))
            sunset = datetime.fromtimestamp(weather_data.get("sys").get("sunset"))
            weather_description = weather_data.get("weather")[0].get("description")
            temperature = weather_data.get("main").get("temp")
            feels_temperature = weather_data.get("main").get("feels_like")
            pressure = weather_data.get("main").get("pressure")
            humidity = weather_data.get("main").get("humidity")
            wind_speed = weather_data.get("wind").get("speed")
            bot.send_message(
                message.chat.id,
                f"Today: {date}\n"
                f"Description: {weather_description}\n"
                f"Temperature: {temperature}°C\n"
                f"Feels like: {feels_temperature}°C\n"
                f"Pressuer: {pressure}hPa\n"
                f"Humidity: {humidity}%\n"
                f"Wind Speed: {wind_speed} m/s\n"
                f"Sunrise: {sunrise}\n"
                f"Sunset: {sunset}\n",
            )
        else:
            bot.send_message(
                message.chat.id, "Error: Check name of your city or country"
            )


if __name__ == "__main__":
    bot.polling(none_stop=True)
