import redshift_connector
import pandas as pd
import itertools

# Redsift Connection Setting
conn = redshift_connector.connect(
    host='host_name',
    database='db_name',
    user='db_user_name',
    password="db_user_password"
)
cursor = conn.cursor()

# Get Data
cursor.execute("select * from  pg_user")
data_result = cursor.fetchall()

# Get Column
cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'pg_user' ORDER by ordinal_position")
column_result = cursor.fetchall()

# Create Dataframe
df = pd.DataFrame(data_result,columns=list(itertools.chain.from_iterable(column_result)))
print(df)
