import sqlite3
import texts


def connect():
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    return connection, cursor


def fetch(req):
    connection, cursor = connect()
    try:
        cursor.execute(req)
        res = cursor.fetchall()
        return res if res else 0
    except sqlite3.OperationalError:
        return 0


def commit(req):
    connection, cursor = connect()
    try:
        cursor.execute(req)
        connection.commit()
        return 1
    except sqlite3.OperationalError:
        return 0


def is_admin(user_id):
    res = fetch(f"SELECT * FROM users WHERE user_id='{user_id}'")
    print('is_admin')
    if not res:
        return 0
    elif res[0][-1] == '1':
        return 1
    else:
        return 0


def user_exist(user_id):
    if not fetch(f"SELECT * FROM users WHERE user_id='{user_id}'"):
        return 1
    else:
        return 0


def create_user(user_id, score=0):
    try:
        commit(f"INSERT INTO users (user_id, score) VALUES ('{user_id}', '{score}')")
        return 1
    except sqlite3.Error:
        return 0


def change_rank(user_id, amount):
    rank = fetch(f"SELECT score FROM users WHERE user_id='{user_id}'")
    if not rank:
        return create_user(user_id, score=amount)
    else:
        try:
            commit(f"UPDATE users SET score='{float(rank[0][0])+float(amount)}' WHERE user_id='{user_id}'")
            return [1, f'{float(rank[0][0])+float(amount)}']
        except sqlite3.Error:
            return 0
        except ValueError:
            return [0, 1]


def upload_rank_change_note(user_id, prov_id, amount, reason=''):
    if reason == '':
        return commit(f"INSERT INTO score_logs (user_id, amount, promoted_by, reason) VALUES"
                      f"('{user_id}', '{amount}', '{prov_id}', 'причина не указана')")
    else:
        return commit(f"INSERT INTO score_logs (user_id, amount, promoted_by, reason) VALUES"
                      f"('{user_id}', '{amount}', '{prov_id}', '{reason}')")


def get_rank(user_id):
    rank = fetch(f"SELECT score FROM users WHERE user_id='{user_id}'")
    if not rank:
        if create_user(user_id):
            return '0'
        else:
            return 0
    else:
        return rank[0][0]


def last_events(user_id):
    res = fetch(f"SELECT * FROM score_logs WHERE user_id='{user_id}' ORDER BY id DESC LIMIT 5")
    if not res:
        return texts.NO_RECORDS_YET
    else:
        output = ''
        for i in res:
            output += texts.ACTION_RECORD.format(i[3], i[2], i[4])
        return output


def get_top_users():
    try:
        res = fetch(f"SELECT * FROM users ORDER BY score DESC LIMIT 5")
        output_data = []
        for i in res:
            output_data.append([i[1], i[2]])
        return output_data
    except sqlite3.Error:
        return 0
