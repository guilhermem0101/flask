from flask import Flask, send_file, request, jsonify
import os
import io
from flask_cors import CORS 
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
app = Flask(__name__)
CORS(app)
url = "https://raw.githubusercontent.com/guilhermem0101/ml-book-exemplos/main/dados_transformados.csv"

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


@app.route('/produtos/contagem', methods=['GET'])
def countByProdutos():
  produto = request.args.get('produto')
  
  df = pd.read_csv(url)
  qtd_por_produto = df.groupby('Product')['Quantity Ordered'].sum().sort_values(ascending=False)

    # Converter a série em um dicionário
  qtd_por_produto_dict = qtd_por_produto.to_dict()
  
    # Criar uma lista de objetos com informações sobre produtos e quantidades vendidas
  produtos_info = [{'produto': produto, 'quantidade': quantidade} for produto, quantidade in qtd_por_produto_dict.items()]
  
  return jsonify(produtos_info)



@app.route('/produtos', methods=['GET'])
def getAllProdutos():

  sql = "select * from Produtos"
  data = consulta(sql)

  return jsonify(data)


@app.route('/vendas-composicao', methods=['GET'])
def geTotal():

  df = pd.read_csv(url)
  pedidos_compostos = df[df.duplicated(['Order Date', 'Purchase Address'], keep='first')]
  return str(len(pedidos_compostos))


@app.route('/vendas-serie', methods=['GET'])
def getSeries():
  intervalo = request.args.get('intervalo')
 
  df = pd.read_csv(url)
  
  # Certifique-se de que o nome da coluna está correto
  df.rename(columns={'Data': 'Order Date'}, inplace=True)
  
  # Converte a coluna 'Order Date' para o tipo de data
  df['Order Date'] = pd.to_datetime(df['Order Date'])
  
  # Define 'Order Date' como o índice do DataFrame
  df.set_index('Order Date', inplace=True)
  
  serie_temporal = df.resample(intervalo)['Sales'].sum()
  
  plt.figure(figsize=(10, 6))
  serie_temporal.plot(kind='line', marker='o')
  img_buffer = io.BytesIO()
  plt.savefig(img_buffer, format='png')
  img_buffer.seek(0)

  # Retorna a imagem diretamente como resposta
  return send_file(img_buffer, mimetype='image/png')



if __name__ == '__main__':
  app.run(port=5000)
