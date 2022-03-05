import sqlite3

db = sqlite3.connect('Scores.sqlite')
cur = db.cursor()

cur.execute('''
create table if not exists SCORES (
score integer)
''')
db.commit()

result = cur.fetchall()
print(result)


#        cur.execute(f"INSERT INTO SCORES VALUES ({self.player.current_score})")