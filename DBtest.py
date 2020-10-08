import sqlite3

conn = sqlite3.connect("computerNetwork.db")
cursor = conn.cursor()
instructQuery = """
                select * from UserData where username == "{user}"
            """.format(user = "bbb")
print(instructQuery)
cursor.execute(instructQuery)
values = cursor.fetchall()
print(len(values))
for row in values:
    print(row[0])
    print(row[1])