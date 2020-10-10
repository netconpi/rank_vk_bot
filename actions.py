
from random import randint
import texts


def message_send(vk, chat_id, msg):
    vk.messages.send(
        peer_id=chat_id,
        random_id=randint(0, 999999),
        message=msg
    )


def get_name(vk, user_id):
    res = vk.users.get(
        user_ids=user_id,
        fields='screen_name'
    )

    return res[0]['first_name'], res[0]['last_name']


def make_list(vk, data):
    output_message = texts.TOP_TITLE
    for i in data:
        first_name, last_name = get_name(vk, i[0])
        output_message += texts.TOP_RECORD.format(i[0], first_name, last_name, i[1])

    return output_message
