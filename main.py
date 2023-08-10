from flask import Flask
import os
import mysql.connector
app = Flask(__name__)


import os
def conecta_db():
  conn = mysql.connector.connect(
    host=os.getenv("host"),
    database=os.getenv("database"),
    user=os.getenv("user"),
    password=os.getenv("password"),
    ssl_verify_identity = True,
    ssl_ca=os.getenv("ssl_ca"),
    use_pure=True
  )
  return conn




# Consulta global
def consulta(sql):
  con = conecta_db()
  cur = con.cursor()
  cur.execute(sql)
  recset = cur.fetchall()
  con.close()
  return recset

# Insert global
def inserir_dados(sql, values):
  con = conecta_db()
  cur = con.cursor()
  cur.execute(sql, values)
  con.commit()
  con.close()
    


@app.route('/as', methods=['GET'])
def indexs():
  x=[1,2,3]
  return x


@app.route('/produtos', methods=['GET'])
def getCep():

  sql = "select * from Produtos"
  data = consulta(sql)

  return data

if __name__ == '__main__':
  app.run(port=5000)
