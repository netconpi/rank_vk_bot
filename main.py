import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import requests

import secrets
import db
import actions
import texts


def main(vk, longpoll):
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            text = event.obj.message['text'].split()
            from_id = event.obj.message['from_id']
            peer_id = event.obj.message['peer_id']
            if text[0][0] == '!':
                if db.is_admin(from_id):
                    if text[0] == '!rn':
                        if len(text) > 2:
                            user_id = text[1][3:text[1].find('|')]
                            res = db.change_rank(user_id, text[2])
                            if res[0]:
                                actions.message_send(vk, peer_id, texts.SUC_RANK_CHANGE.format(text[1], res[1]))
                                db.upload_rank_change_note(user_id, from_id, text[2], ' '.join(text[3:]))
                            else:
                                if len(res) > 1:
                                    actions.message_send(vk, peer_id, texts.ERROR.format(texts.ERROR_CONVERT_TO_FLOAT))
                                else:
                                    actions.message_send(vk, peer_id, texts.ERROR.format(texts.ERROR_DATABASE))
                        else:
                            actions.message_send(vk, peer_id, texts.ERROR.format(texts.ERROR_ARG))
                else:
                    actions.message_send(vk, peer_id, texts.ERROR.format(texts.ERROR_NOT_ADMIN))

            if text[0][0] == '/':
                if text[0] == '/rn':
                    if len(text) == 1:
                        res = db.get_rank(from_id)
                        first_name, last_name = actions.get_name(vk, from_id)
                        actions.message_send(vk, peer_id, texts.USER_RANK.format(
                            f'[id{from_id}|{first_name} {last_name}]',
                            res,
                            db.last_events(from_id)
                        ))
                    if len(text) == 2:
                        user_id = text[1][3:text[1].find('|')]
                        res = db.get_rank(user_id)
                        first_name, last_name = actions.get_name(vk, user_id)
                        actions.message_send(vk, peer_id, texts.OTHER_USER_RANK.format(
                            f'[id{user_id}|{first_name} {last_name}]',
                            res,
                            db.last_events(user_id)
                        ))
                elif text[0] == '/top':
                    res = db.get_top_users()
                    message = actions.make_list(vk, res)
                    actions.message_send(vk, peer_id, message)


def always_connected():
    vk_session = vk_api.VkApi(token=secrets.TOKEN)
    longpoll = VkBotLongPoll(vk_session, secrets.GROUP_ID)
    vk = vk_session.get_api()

    try:
        print('Запуск бота')
        main(vk, longpoll)
    except requests.exceptions.ReadTimeout:
        print('Перезапуск бота')
        always_connected()


if __name__ == '__main__':
    always_connected()
