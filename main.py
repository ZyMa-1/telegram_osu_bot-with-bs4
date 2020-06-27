import config
import utils
from telebot import TeleBot
from flag import flag as convert_to_flag  # converts to emoji country flag

bot = TeleBot(config.TOKEN)


@bot.message_handler(commands=['help', 'start'])
def help_handler(msg):
    chat_id = msg.chat.id
    command = msg.text.split()[0]
    res = f"<b>Commands:</b>\n" \
          f"/help\n" \
          f"returns list of commands\n\n" \
          f"/user [username]\n" \
          f"returns some info about user\n\n" \
          f"/user_icon [username]\n" \
          f"get user icon\n\n" \
          f"/user_best [username]\n" \
          f"returns user top 5 ranks\n\n" \
          f"/set_default [username]\n" \
          f"sets default username, so you can use commands without username parameter\n\n" \
          f"/get_song [osz file]\n" \
          f"return mp3 song file"
    if command == "/start":
        res = f"<b>Hello There</b>\nThis bot was made for osu! community\n\n" + res
    bot.send_message(chat_id, res, parse_mode='HTML')


@bot.message_handler(commands=['user', 'user_icon', 'set_default', 'user_best'])
def user_handler(msg):
    chat_id = msg.chat.id
    username = msg.text.split()[-1]
    if username[0] == "/":
        username = utils.get_default_username(chat_id)
        if username is None:
            bot.send_message(chat_id, f"Invalid username")
            return
    user_info, user_extras = utils.get_user_info(username)
    if user_info is None:
        bot.send_message(chat_id, f"Invalid username")
        return

    command = msg.text.split()[0]
    if command == '/user':
        country_flag = convert_to_flag(user_info["country_code"])
        user_profile_url = f"http://osu.ppy.sh/u/{user_info['id']}"
        statistics = user_info["statistics"]
        is_supporter = "(osu! supporter ♥)" if user_info["is_supporter"] else ""
        bot.send_message(chat_id, f"<b>osu! standard</b>\n"
                                  f'<a href="{user_profile_url}">{user_info["username"]}</a> {is_supporter}\n\n'
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
    if command == "/user_best":
        res = ""
        for score in user_extras["scoresBest"]:
            beatmap_info = score["beatmap"]
            beatmap_url = f"https://osu.ppy.sh/b/{beatmap_info['id']}"
            beatmapset = score["beatmapset"]
            res += f'<a href="{beatmap_url}">{beatmapset["artist"] + " - " + beatmapset["title"]} [{beatmap_info["version"]}]</a>\n' \
                   f'mapped by <i>{beatmapset["creator"]}</i>\n' \
                   f'<b>star rating:</b> {beatmap_info["difficulty_rating"]} ⭐\n' \
                   f'<b>mods:</b> {" ".join(score["mods"]) if len(score["mods"]) > 0 else "NM"}\n' \
                   f'<b>accuracy:</b> {round(score["accuracy"] * 100, 2)}%\n' \
                   f'<b>pp:</b> {round(score["pp"], 2)}\n\n'
        bot.send_message(chat_id, res, parse_mode='HTML', disable_web_page_preview=True)


@bot.message_handler(content_types=['text'])
def text_handler(msg):
    chat_id = msg.chat.id
    bot.send_message(chat_id, f"I don't understand this command\n"
                              f"Type /help to see list of commands")


@bot.message_handler(content_types=['document'])
def doc_handler(msg):
    chat_id = msg.chat.id
    if msg.caption == "/get_song":
        doc = msg.document
        filename = doc.file_name
        file_id = doc.file_id
        real_filename = utils.generate_filename()
        if filename.split('.')[-1] != 'osz':
            bot.send_message(chat_id, "Wrong file extension")
            return
        if doc.file_size > 10485760:
            bot.send_message(chat_id, "File size is too large")
            return
        utils.get_file(file_id, f"temp/{real_filename}.zip")
        check = utils.get_song(real_filename)
        if check != "ok":
            bot.send_message(chat_id, "That's more than one song, idk which one you want...")
            utils.delete_temp_files(zip_filename=f"temp/{real_filename}.zip")
            return
        bot.send_audio(chat_id, open(f"temp/{real_filename}.mp3", 'rb'))
        utils.delete_temp_files(zip_filename=f"temp/{real_filename}.zip", mp3_filename=f"temp/{real_filename}.mp3")
    return


if __name__ == "__main__":
    bot.infinity_polling(timeout=300)
