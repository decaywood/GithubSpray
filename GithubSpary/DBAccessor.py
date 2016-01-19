# coding=utf-8
import pymysql

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='123456',
                             db='github_db',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


def db_operation(sql, arg, query=False):
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, arg)

            if not query:
                connection.commit()
            else:
                result = cursor.fetchall()
                return result
    except Exception as e:
        print e


def update_info(user, full_name, email, location):
    if user is not None and full_name is not None and email is not None and location is not None:
        # Read a single record
        sql = "UPDATE `user_info` SET `user_name` = %s, `user_email` = %s, `user_location` = %s WHERE `user_` = %s"
        db_operation(sql, (full_name, email, location, user))


def insert_info(user, full_name, email, location):
    if user is not None and full_name is not None and email is not None and location is not None:
        # Read a single record
        sql = "INSERT INTO `user_info` (`user_`, `user_name`, `user_email`, `user_location`) VALUES (%s, %s, %s, %s)"
        db_operation(sql, (user, full_name, email, location))


def delete_info(name):
    if name is not None:
        sql = "DELETE FROM `user_info` WHERE `user_` = %s"
        db_operation(sql, (name,))


def get_all_user_path():
    sql = "SELECT `user_` FROM `user_info`"
    res = {'/' + raw['user_'] for raw in db_operation(sql, None, True)}
    return res


def reset_db():
    sql = "TRUNCATE `user_info`"
    db_operation(sql, None)


def close_db():
    connection.close()


if __name__ == '__main__':
    update_info('ftxbird', 'soulnix', 'ftxbird@gmail.com', '北京')
