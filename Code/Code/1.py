import mysql.connector
import datetime

# Connect to MySQL database
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="2307@darsh",
  database="final_project"
)


# Execute SELECT statement and fetch all rows
cursor = mydb.cursor()
cursor.execute("SELECT vehicle_no,toll_name,amount_paid FROM final_project.pre_book_table WHERE book_id = 161")
data=cursor.fetchall()
print(data)

for i in data:
    no , toll , amount = i

print(no)
print(toll)
print(amount)
  

cursor.execute("SELECT user_id FROM final_project.user_table where vehicle_no=%s",(no,))
email=cursor.fetchall()
print(email)

for i in email:
    mail = i

print()






