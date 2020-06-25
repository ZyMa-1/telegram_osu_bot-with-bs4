import config
import utils
from telebot import TeleBot
from flag import flag as convert_to_flag  # converts to emoji country flag

bot = TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def start_handler(msg):
    chat_id = msg.chat.id
    bot.send_message(chat_id, f"<b>Hello There</b>\n"
                              f"This bot was made for osu! community\n\n"
                              f"<b>Modes:</b>\n"
                              f"0 - osu! standard\n\n"
                              f"<b>Commands:</b>\n"
                              f"/help\n"
                              f"returns list of commands\n\n", parse_mode='HTML')


@bot.message_handler(commands=['help'])
def help_handler(msg):
    chat_id = msg.chat.id
    bot.send_message(chat_id, f"<b>Modes:</b>\n"
                              f"0 - osu! standard\n\n"
                              f"<b>Commands:</b>\n"
                              f"/help\n"
                              f"returns list of commands\n\n"
                              f'/user [username]\n'
                              f'returns some info about user\n\n'
                              f'/user_icon [username]\n'
                              f'get user icon\n\n'
                              f'/set_default [username]\n'
                              f'sets default username, so you can use commands without username parameter\n', parse_mode='HTML')


@bot.message_handler(commands=['user', 'user_icon', 'set_default'])
def user_handler(msg):
    chat_id = msg.chat.id
    username = msg.text.split()[-1]
    if username[0] == "/":
        username = utils.get_default_username(chat_id)
        if username is None:
            bot.send_message(chat_id, f"Invalid username")
            return
    user_info = utils.get_user_info(username)
    if user_info is None:
        bot.send_message(chat_id, f"Invalid username")
        return

    command = msg.text.split()[0]
    if command == '/user':
        country_flag = convert_to_flag(user_info["country_code"])
        user_profile_url = f"http://osu.ppy.sh/u/{user_info['id']}"
        statistics = user_info["statistics"]
        bot.send_message(chat_id, f"<b>osu! standard</b>\n"
                                  f'<a href="{user_profile_url}">{user_info["username"]}</a>\n\n'
                                  f'<b>rank:</b> #{statistics["rank"]["global"]} (#{statistics["rank"]["country"]}{country_flag})\n'
                                  f'<b>pp:</b> {round(statistics["pp"], 2)}\n'
                                  f'<b>accuracy:</b> {round(statistics["hit_accuracy"], 2)}%\n\n'
                                  f'<b>play count:</b> {statistics["play_count"]}\n'
                                  f'<b>play time:</b> {utils.format_time(statistics["play_time"])}', parse_mode='HTML',
                         disable_web_page_preview=True)
    if command == '/user_icon':
        bot.send_photo(chat_id, user_info["avatar_url"])
    if command == '/set_default':
        utils.set_default_username(chat_id, username)
        bot.send_message(chat_id, "Success")


@bot.message_handler(content_types=['text'])
def text_handler(msg):
    chat_id = msg.chat.id
    bot.send_message(chat_id, f"I don't understand this command\n"
                              f"Type /help to see list of commands")


if __name__ == "__main__":
    bot.infinity_polling(timeout=300)
