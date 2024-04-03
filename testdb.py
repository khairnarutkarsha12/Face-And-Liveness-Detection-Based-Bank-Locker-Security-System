import sqlite3

con = sqlite3.connect('doorlock.db')
cursorObj = con.cursor()
cursorObj.execute("CREATE TABLE IF NOT EXISTS Users (UserName text,Password text, Locker text, Nominee text, Time text, Counter int, Status text)")
cursorObj.execute("INSERT INTO Users VALUES(?,?,?,?,?,?,?)",("abc","123","gh","primary","12-12-12",0,"Active"))
cursorObj.execute("INSERT INTO Users VALUES(?,?,?,?,?,?,?)",("xyz","143","gh","primary","12-13-23",0,"Active"))
con.commit()