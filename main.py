from flask import Flask, render_template
from dotenv import load_dotenv
load_dotenv()
import os
import MySQLdb
import mysql.connector
app = Flask(__name__)



def conecta_db2():
  conn = mysql.connector.connect(
    host="aws.connect.psdb.cloud",
    database="analises",
    user="boc36q84eq64ebmrjqbs",
    password="pscale_pw_gpxgFaKmTnOUcs5vHQbBLI3U3uVuRJrBmS6wbKUEkbg"

  )
  return conn


def conecta_db():
  
  connection = MySQLdb.connect(
    host= "aws.connect.psdb.cloud",
    user="rlk7h67rkbqblfoopzzb",
    passwd= "pscale_pw_Q0K5ORUMEoO1R80hZ0lwp0NN7rTa8y0YQCuyIe1maTc",
    db= "analises",
    autocommit = True,
    ssl_mode = "VERIFY_IDENTITY",
    ssl      = {
      "ca": "./etc/ssl/cert.pem"
    }
  )
  return connection

# Consulta global
def consulta(sql):
  con = conecta_db2()
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


@app.route('/test', methods=['GET'])
def getCep():

  sql = "select * from teste"
  data = consulta(sql)
  # # Criar um DataFrame pandas com os dados retornados
  # df = pd.DataFrame(data, columns=['nome_curso', 'cod_curso'])
  # # Converter o DataFrame em JSON
  # json_data = df.to_json(orient='records')
  return data

if __name__ == '__main__':
  app.run(port=5000)
