import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


con = psycopg2.connect(
    "dbname= dtbank user= postgres host=localhost password=5432 port=5432")

con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

cur = con.cursor()

cur.execute(open("dropTables.sql", "r").read())
cur.execute(open("createTables.sql", "r").read())
cur.execute(open("inserts.sql", "r").read())
