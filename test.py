import psycopg2

password = 'E-1Le1sIjuvKGE2lQFWXcA'

URL = f'postgresql://abdullah:{password}@free-tier4.aws-us-west-2.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&options=--cluster%3Drunny-tiger-2222&sslrootcert=root.crt'

db = psycopg2.connect(URL)

myCursor = db.cursor()

print('PostgreSQL database version:')
myCursor.execute('SELECT version()')
db_version = myCursor.fetchone()
print(db_version)


# remove row with userId = '4'
myCursor.execute("DELETE FROM pokewordle WHERE userId = '655569116333080586'")
db.commit()
# query = "INSERT INTO pokewordle (userId, currentword,guesses,lives,stats) VALUES (%s, %s, %s, %s, %s)"
# myCursor.execute(query, ("4", "pikachu", [], 5, [0,0,0,0,0,0]))
# db.commit()
# myCursor.execute("SELECT * FROM pokewordle")

rows = myCursor.fetchall()

for row in rows:
    print(row)
    