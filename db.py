import sqlite3
# подключение к базе данных
connect = sqlite3.connect("subs.db")
cursor = connect.cursor()
# создание таблиц базы данных и связей
cursor.execute('''
 CREATE TABLE IF NOT EXISTS  "categories" (
	"id"	INTEGER,
	"name"	TEXT,
	"system_name"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
''')

cursor.execute('''
 CREATE TABLE IF NOT EXISTS  "users" (
	"id"	INTEGER,
	"login"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
''')
cursor.execute('''
 CREATE TABLE IF NOT EXISTS  "subscribes" (
    "id_user"	INTEGER,
	"id_category"	INTEGER,
    FOREIGN KEY (id_user)  REFERENCES users (id),
    FOREIGN KEY (id_category)  REFERENCES categories (id)
);
''')
# переменные для хронения текущего авторизованного аккаунта
login = None
iduser = None
# функция для регистрации пользователя (автоматически авторизует его)
def registr(connect, cursor, login):
    rez = cursor.execute(""" SELECT login FROM users 
    WHERE login = ? """, (login,)).fetchone()
    print(rez)
    if(rez == None):
        cursor.execute("""INSERT INTO users ("id", "login") VALUES (NULL, ?)""", (login,))
        connect.commit()
        login = login
        print(cursor.execute(""" SELECT id FROM users WHERE login = ? """, (login,)).fetchone())
        iduser = cursor.execute(""" SELECT id FROM users WHERE login = ? """, (login,)).fetchone()[0]
        return f"Пользователь успешно зарегистрирован"
    else:
        return "для просмотра всех возможных категорий введите /subscriptionsAdd"
# функция для аторизации пользователя
def selectUser(connect, cursor, login):
    rez = cursor.execute(""" SELECT id FROM users 
    WHERE login = ? """, (login,)).fetchone()
    if(rez == None):
        return "неверный логин или пароль"
    else:
        return rez[0]
# функция добавления категории (может пользоваться даже не авторизованный пользователь)
def addCategory(connect, cursor, name):
    rez = cursor.execute(""" SELECT name FROM categories 
    WHERE name = ? """, (name,)).fetchone()
    if(rez == None):
        cursor.execute("""INSERT INTO categories ("id", "name") VALUES (NULL, ?)""", (name,))
        connect.commit()
        return f"Категория {name} успешно добавленна" 
    else:
        return "Такая категория уже существует"
# функция подписки на категорию (только для авторизованных пользователей)
def podpis(connect, cursor, userid, selectcateg):
    if (userid == None):
        return "Чтобы подписаться нужно авторизоваться"
    else:
        print(selectcateg)
        rez = cursor.execute(""" SELECT id FROM categories WHERE system_name = ? """, (selectcateg,)).fetchone()
        if(rez != None):
            ald = cursor.execute(""" SELECT id_user FROM subscribes WHERE id_user = ? AND id_category = ? """, (userid, rez[0])).fetchone()
            if(ald == None):
                cursor.execute("""INSERT INTO subscribes ("id_user", "id_category") VALUES ( ?, ?)""", (userid, rez[0]))
                connect.commit()
                return f"вы успешно подписаны на {selectcateg}"
            else:
                return f"вы уже подписаны на {selectcateg}"
        else :
            return "Введённой категории несуществует"
def podpisForName(connect, cursor, userid, selectcateg):
    if (userid == None):
        return "Чтобы подписаться нужно авторизоваться"
    else:
        print(selectcateg)
        rez = cursor.execute(""" SELECT id FROM categories WHERE name = ? """, (selectcateg,)).fetchone()
        if(rez != None):
            ald = cursor.execute(""" SELECT id_user FROM subscribes WHERE id_user = ? AND id_category = ? """, (userid, rez[0])).fetchone()
            if(ald == None):
                cursor.execute("""INSERT INTO subscribes ("id_user", "id_category") VALUES ( ?, ?)""", (userid, rez[0]))
                connect.commit()
                return f"вы успешно подписаны на {selectcateg}"
            else:
                return f"вы уже подписаны на {selectcateg}"
        else :
            return "Введённой категории несуществует"
# функция просмотра подписок (только для авторизованных пользователей)
def showCategoryes(connect, cursor):
    rez = cursor.execute(""" SELECT name, system_name FROM categories """).fetchall()
    # print(rez)


    return rez
def showCategoryesSystem(connect, cursor, dop):
    rez = cursor.execute(""" SELECT system_name FROM categories """).fetchall()
    # print(rez)
    categ = []
    for i in rez:
        categ.append(dop + i[0])
    return categ

def showPodpis(connect, cursor, userid):
    if (userid == None):
        return "Для просмотра подписок нужно авторизоваться"
    else:
        subsuser =  cursor.execute(""" SELECT categories.name, categories.system_name FROM subscribes INNER JOIN categories ON categories.id = subscribes.id_category  WHERE id_user = ?  """, (userid, )).fetchall()

        return subsuser
def showPodpisSystem(connect, cursor, userid):
    if (userid == None):
        return "Для просмотра подписок нужно авторизоваться"
    else:
        subsuser =  cursor.execute(""" SELECT categories.name, categories.system_name FROM subscribes INNER JOIN categories ON categories.id = subscribes.id_category  WHERE id_user = ?  """, (userid, )).fetchall()
        rez = 'Вы подписаны на: \n'
        count =1
        for i in subsuser:
            rez += f"{count}) {i[0]}. для отписки от данной категории {'/del' +i[1]}\n"
            count+=1
        return subsuser
# функция отписки от категории (только для авторизованного пользователя)
def unsubs(connect, cursor, userid, categoryName):
    if (userid == None):
        return "Чтобы отписываться нужно авторизоваться"
    else:
        print(categoryName)
        categoryId = cursor.execute(""" SELECT id FROM categories WHERE system_name = ?  """, (categoryName, )).fetchone()
        if(categoryId == None):
            return "Такой категории несуществует"
        else:
            categoryIdOnUser = cursor.execute(""" SELECT categories.id FROM subscribes INNER JOIN categories ON categories.id = subscribes.id_category  WHERE id_user = ? AND id_category = ?  """, (userid, categoryId[0])).fetchone()
            if(categoryIdOnUser == None):
                return "Вы не подписаны на данную категорию"
            else:
                cursor.execute(""" DELETE FROM subscribes WHERE id_user = ? AND id_category = ?  """, (userid, categoryIdOnUser[0]))
                connect.commit()
                return f"вы успешно отписаны от {categoryName}"


def unsubsForName(connect, cursor, userid, categoryName):
    if (userid == None):
        return "Чтобы отписываться нужно авторизоваться"
    else:
        print(categoryName)
        categoryId = cursor.execute(""" SELECT id FROM categories WHERE name = ?  """, (categoryName, )).fetchone()
        if(categoryId == None):
            return "Такой категории несуществует"
        else:
            categoryIdOnUser = cursor.execute(""" SELECT categories.id FROM subscribes INNER JOIN categories ON categories.id = subscribes.id_category  WHERE id_user = ? AND id_category = ?  """, (userid, categoryId[0])).fetchone()
            if(categoryIdOnUser == None):
                return "Вы не подписаны на данную категорию"
            else:
                cursor.execute(""" DELETE FROM subscribes WHERE id_user = ? AND id_category = ?  """, (userid, categoryIdOnUser[0]))
                connect.commit()
                return f"вы успешно отписаны от {categoryName}"
# функция просмотра всех категорий (для всех пользователей)
def showAllCategorys(connect, cursor):
        subsuser =  cursor.execute(""" SELECT name FROM categories """).fetchall()
        rez = 'Категории: \n'
        count =1
        for i in subsuser:
            rez += f"{count}) {i[0]} для отписки от данной категории {'/del' +i[1]}\n"
            count+=1
        return rez
# функция удаление категории (для всех пользователей)
def delCategory(connect, cursor, categoryName):

    categoryId = cursor.execute(""" SELECT id FROM categories WHERE name = ?""", (categoryName,)).fetchone()
    if(categoryId == None):
        return f"категории {categoryName} несуществует"
    else:
        cursor.execute(""" DELETE FROM subscribes WHERE id_category = ?""", (categoryId[0], ))
        cursor.execute(""" DELETE FROM categories WHERE id = ?""", (categoryId[0],))
        connect.commit()
        return f"категория {categoryName} успешно удалена"
# функция удаления пользователя 
def delUser(connect, cursor, login, password):
    rez = cursor.execute(""" SELECT login, password FROM users 
    WHERE login = ? """, (login, )).fetchone()
    print(rez)
    if(rez == None):
        return "Такого пользователя несуществует"
    elif(rez[1] != password):
        return "В удалении отказанно Неверный пароль "
    else:
        userid = cursor.execute(""" SELECT id FROM users WHERE login = ? AND password = ? """, (login, password)).fetchone()
        cursor.execute(""" DELETE FROM subscribes WHERE id_user = ?""", (userid[0], ))
        cursor.execute(""" DELETE FROM users WHERE login = ? AND password = ? """, (login, password))
        connect.commit()
        return f"Пользователь с логином {login} успешно удалён"
# пользовательский интрфейс через командную строку 
# while True:
#     print('''
#     Выберете желаемое действие
#     1) Зарегистрировать пользователя
#     2) Авторизовать пользователя
#     3) Просмотреть информацию авторизованного аккаунта
#     4) Добавить категорию
#     5) Подписаться на категорию
#     6) Просмотреть подписки
#     7) Отписаться от категории
#     8) Удалить категорию
#     9) Просмотреть категории
#     10) удаление пользователя
#     STOP) Остановить выполнение команд
#     ''')
#     comand = input("Введите команду ")
#     if (comand == "STOP"):
#         break
#     if (comand == "1"):
#         login = input("Введите логин ")
#         password = input("Введите пароль ")
#         temp = registr(connect, cursor,  login )
#         print(temp[2])
#         login = temp[1]
#         iduser = temp[0]
#     if (comand == "2"):
#         login = input("Введите логин ")
#         password = input("Введите пароль ")
#         temp = autor(connect, cursor, login, password)
#         print(temp[2])
#         login = temp[1]
#         iduser = temp[0]
#     if (comand == "3"):
#         print(login)
#         print(iduser)
#     if (comand == "4"):
#         name = input("Введите название категории ")
#         print(addCategory(connect, cursor, name))
#     if (comand == "5"):
#         print(podpis(connect, cursor, iduser))
#     if (comand == "6"):
#         print(showPodpis(connect, cursor, iduser))
#     if (comand == "7"):
#         print(unsubs(connect, cursor, iduser))
#     if (comand == "8"):
#         print(showAllCategorys(connect, cursor))
#         categoryName = input("Введите название категории ")
#         print(delCategory(connect, cursor, categoryName))
#     if (comand == "9"):
#         print(showAllCategorys(connect, cursor))
#     if (comand == "10"):
#         login = input("Введите логин ")
#         password = input("Введите пароль ")
#         print(delUser(connect, cursor, login, password))