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
    
def filtroPeriodo(data_inicial, data_final, dados):
  # Filtra os dados com base no período de tempo especificado
  filtro = (dados['Order Date'] >= data_inicial) & (dados['Order Date'] <= data_final)
  df_filtrado = dados[filtro]

  return df_filtrado

def get_city(address):
  return address.split(',')[1]

# funtction to get the state in the data
def get_state(address):
  return address.split(',')[2].split(' ')[1]



@app.route('/produtos-contagem', methods=['GET'])
def countByProdutos():
  produto = request.args.get('produto')
  data_inicial = request.args.get('data_inicial', None)  # Padrão: None
  data_final = request.args.get('data_final', None)
  df = pd.read_csv(url)
  df['Order Date'] = pd.to_datetime(df['Order Date'])
  
  #filtra por periodo selecionado
  if data_inicial is not None and data_final is not None:
    df = filtroPeriodo(data_inicial, data_final, df)
    
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
  
  produtos_serializados = []
  for vaga in data:
      vaga_dict = {
          'IDProduto': vaga[0],
          'NomeProduto': vaga[1],
          'CategoriaProduto': vaga[2],
          'QuantidadeEstoque': vaga[3],      
      }
      produtos_serializados.append(vaga_dict)

  return jsonify(produtos_serializados)
  


@app.route('/vendas-composicao', methods=['GET'])
def geTotal():

  df = pd.read_csv(url)
  pedidos_compostos = df[df.duplicated(['Order Date', 'Purchase Address'], keep='first')]
  return str(len(pedidos_compostos))


@app.route('/vendas-serie', methods=['GET'])
def getSeries():
  periodo = request.args.get('periodo')
  data_inicial = request.args.get('data_inicial', None)  # Padrão: None
  data_final = request.args.get('data_final', None)
  df = pd.read_csv(url)
  # Converte a coluna 'Order Date' para o tipo de data
  df['Order Date'] = pd.to_datetime(df['Order Date'])
  
  #filtra por periodo selecionado
  if data_inicial is not None and data_final is not None:
    df = filtroPeriodo(data_inicial, data_final, df)
  
  # Certifique-se de que o nome da coluna está correto
  df.rename(columns={'Data': 'Order Date'}, inplace=True)
  
  # Define 'Order Date' como o índice do DataFrame
  df.set_index('Order Date', inplace=True)
  
  serie_temporal = df.resample(periodo)['Sales'].sum()
  
  plt.figure(figsize=(10, 6))
  serie_temporal.plot(kind='line', marker='o')
  img_buffer = io.BytesIO()
  plt.savefig(img_buffer, format='png')
  img_buffer.seek(0)

  # Retorna a imagem diretamente como resposta
  return send_file(img_buffer, mimetype='image/png')



@app.route('/vendas-por-cidade', methods=['GET'])
def getVendasByCity():
  data_inicial = request.args.get('data_inicial', None)  # Padrão: None
  data_final = request.args.get('data_final', None)
  
  df = pd.read_csv(url)
  df['Order Date'] = pd.to_datetime(df['Order Date'])
   #filtra por periodo selecionado
  if data_inicial is not None and data_final is not None:
    df = filtroPeriodo(data_inicial, data_final, df)
  
  df['Cities'] = df['Purchase Address'].apply(lambda x: f"{get_city(x)} ({get_state(x)})") 
  
  cidades_mais_vendas = df.groupby('Cities')['Sales'].sum().sort_values(ascending=False)
  cidade_info = [{'cidade': cidade, 'arrecadacao': arrecadacao} for cidade, arrecadacao in cidades_mais_vendas.items()]
  
  return jsonify(cidade_info)




@app.route('/ticket-medio', methods=['GET'])
def getMediaVendas():
  data_inicial = request.args.get('data_inicial', None)  # Padrão: None
  data_final = request.args.get('data_final', None)
  
  df = pd.read_csv(url)
  df['Order Date'] = pd.to_datetime(df['Order Date'])
   #filtra por periodo selecionado
  if data_inicial is not None and data_final is not None:
    df = filtroPeriodo(data_inicial, data_final, df)
    
  valor_medio_vendas = df['Sales'].mean()
  valor_medio_formatado = round(valor_medio_vendas, 2)
  return str(valor_medio_formatado)

if __name__ == '__main__':
  app.run(port=5000)
