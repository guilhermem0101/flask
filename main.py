from flask import Flask, send_file
import os
import io
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
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
def getAllProdutos():

  sql = "select * from Produtos"
  data = consulta(sql)

  return data


@app.route('/vendas', methods=['GET'])
def getSerie():
  url = "https://raw.githubusercontent.com/guilhermem0101/ml-book-exemplos/main/dados_transformados.csv"
  df = pd.read_csv(url)
  df = df[df['Order Date'] != 'Order Date']
  df.set_index('Order Date', inplace=True)
  serie_temporal_dia = df.resample('D')['Sales'].sum()
  plt.figure(figsize=(10, 6))
  serie_temporal_dia.plot(kind='line', marker='o')
  img_buffer = io.BytesIO()
  plt.savefig(img_buffer, format='png')
  img_buffer.seek(0)

  # Retorna a imagem diretamente como resposta
  return send_file(img_buffer, mimetype='image/png')





if __name__ == '__main__':
  app.run(port=5000)
