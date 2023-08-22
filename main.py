from flask import Flask, send_file, request, jsonify
import os
import io
from flask_cors import CORS 
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
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


def univariate_analysis(data, color, title1):
  
  fig = sns.histplot( # create a distplot visualization
    data, # data      
    kde=True, # kde
    color=color # color
  )
  fig.grid(True)
  # Set title and labels
  fig.set_title(title1)
  fig.set_ylabel('Frequência')
  fig.set_xlabel('Valor da venda')
  
  return fig 




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
    
  qtd_por_produto = df.groupby('Product')['Quantity Ordered'].sum().sort_values(ascending=True)

  
  plt.figure(figsize=(13, 8))
  ax = qtd_por_produto.plot(kind='barh', color=plt.cm.Paired.colors)
  plt.xlabel('Quantidade')
  plt.ylabel('Produtos')
  plt.title('Produtos Mais Vendidos')
  ax.set_yticklabels(qtd_por_produto.index, rotation=45, ha='right')
  # Salva o gráfico em um buffer de imagem
  img_buffer = io.BytesIO()
  plt.savefig(img_buffer, format='png')
  img_buffer.seek(0)
  
  # Codifica o buffer da imagem em base64
  return send_file(img_buffer, mimetype='image/png')


@app.route('/vendas-por-produto', methods=['GET'])
def countBySales():
  produto = request.args.get('produto')
  data_inicial = request.args.get('data_inicial', None)  # Padrão: None
  data_final = request.args.get('data_final', None)
  df = pd.read_csv(url)
  df['Order Date'] = pd.to_datetime(df['Order Date'])
  
  #filtra por periodo selecionado
  if data_inicial is not None and data_final is not None:
    df = filtroPeriodo(data_inicial, data_final, df)
    
  qtd_por_produto = df.groupby('Product')['Sales'].sum().sort_values(ascending=True)

    # Converter a série em um dicionário
  plt.figure(figsize=(13, 8))
  ax = qtd_por_produto.plot(kind='barh', color=plt.cm.Paired.colors)
  plt.xlabel('Arrecadação (Em Milhões)')
  plt.ylabel('Produtos')
  plt.title('Produtos Com Mais Arrecadação')
  ax.set_yticklabels(qtd_por_produto.index, rotation=45, ha='right')
   
  # Salva o gráfico em um buffer de imagem
  img_buffer = io.BytesIO()
  plt.savefig(img_buffer, format='png')
  img_buffer.seek(0)
  
  # Codifica o buffer da imagem em base64
  return send_file(img_buffer, mimetype='image/png')




@app.route('/histograma-de-produtos', methods=['GET'])
def histogramaProdutosByOrdem():
  produto = request.args.get('produto')
  data_inicial = request.args.get('data_inicial', None)  # Padrão: None
  data_final = request.args.get('data_final', None)
  df = pd.read_csv(url)
  df['Order Date'] = pd.to_datetime(df['Order Date'])
  
  #filtra por periodo selecionado
  if data_inicial is not None and data_final is not None:
    df = filtroPeriodo(data_inicial, data_final, df)
    
  freq = df["Order ID"].value_counts()

  order = freq.value_counts()
  normalized_order = order / order.sum()
  plt.figure(figsize=(10, 6))
  plt.bar(normalized_order.index, normalized_order.values, color='red')
  plt.xlabel('Quantidade de Produtos distintos')
  plt.ylabel('Proporção de pedidos (%)')
  plt.title('Histograma ')
  plt.gca().yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))
  for i, value in enumerate(normalized_order.values):
    plt.text(normalized_order.index[i], value + 0.01, f'{value:.2%}', ha='center')
  
  # Salva o gráfico em um buffer de imagem
  img_buffer = io.BytesIO()
  plt.savefig(img_buffer, format='png')
  img_buffer.seek(0)
  
  # Codifica o buffer da imagem em base64
  return send_file(img_buffer, mimetype='image/png')




@app.route('/produtos', methods=['GET'])
def getAllProdutos():
  df = pd.read_csv(url)
  produtos_distintos = df[['Product', 'Price Each']].drop_duplicates()
  produtos_distintos.rename(columns={'Price Each': 'Preco'}, inplace=True)
  
  produtos_list = produtos_distintos.to_dict(orient='records')

  return jsonify(produtos_list)
  
  
@app.route('/vendas', methods=['GET'])
def getAllVendas():
  df = pd.read_csv(url)

  # Selecionar os campos solicitados e os primeiros 100 registros
  vendas_data = df[['Product', 'Quantity Ordered', 'Purchase Address', 'Order Date', 'Sales']].head(100)
  vendas_data.rename(columns={'Price Each': 'Preco'}, inplace=True)
  vendas_data.rename(columns={'Quantity Ordered': 'Quantity'}, inplace=True)
  vendas_data.rename(columns={'Purchase Address': 'Address'}, inplace=True)
  vendas_data.rename(columns={'Order Date': 'Order'}, inplace=True)
  # Converter o DataFrame em uma lista de dicionários
  vendas_list = vendas_data.to_dict(orient='records')

  return jsonify(vendas_list)

  
  


@app.route('/produto', methods=['GET'])
def getAllProduto():
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
  serie_temporal = serie_temporal.loc['2019-01-01':'2019-12-31']
  plt.figure(figsize=(10, 6))
  serie_temporal.plot(kind='line', marker='o', color='red')
  plt.title( # title
    "Serie temporal de Arrecadação.", 
    weight="bold", # weight
    fontsize=15, # font-size
    pad=30
  )
  plt.xlabel('Tempo')
  img_buffer = io.BytesIO()
  plt.savefig(img_buffer, format='png')
  img_buffer.seek(0)

  # Retorna a imagem diretamente como resposta
  return send_file(img_buffer, mimetype='image/png')



@app.route('/ordens-serie', methods=['GET'])
def getSeriesOrdens():
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
  
  serie_temporal = df.resample(periodo)['Order ID'].count()
  serie_temporal = serie_temporal.loc['2019-01-01':'2019-12-31']
  plt.figure(figsize=(10, 6))
  serie_temporal.plot(kind='line', marker='o')
  plt.title( # title
    "Serie temporal de ordens de compra.", 
    weight="bold", # weight
    fontsize=15, # font-size
    pad=30
  )
  plt.xlabel('Tempo')
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
  
  if data_inicial is not None and data_final is not None:
      df = filtroPeriodo(data_inicial, data_final, df)

  df['Cities'] = df['Purchase Address'].apply(lambda x: f"{get_city(x)} ") 

  cidades_mais_vendas = df.groupby('Cities')['Sales'].sum().sort_values(ascending=True)
  
  # Cria o gráfico de barras horizontal
  plt.figure(figsize=(12, 8))
  ax = cidades_mais_vendas.plot(kind='barh', color=plt.cm.Paired.colors)
  plt.xlabel('Arrecadação (Em Milhões)')
  plt.ylabel('Cidades')
  plt.title('Cidades com Mais Vendas')
  
  # Salva o gráfico em um buffer de imagem
  img_buffer = io.BytesIO()
  plt.savefig(img_buffer, format='png')
  img_buffer.seek(0)
  
  # Codifica o buffer da imagem em base64
  return send_file(img_buffer, mimetype='image/png')



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




@app.route('/vendas-por-horario', methods=['GET'])
def getDistVendas():
  data_inicial = request.args.get('data_inicial', None)  # Padrão: None
  data_final = request.args.get('data_final', None)

  df = pd.read_csv(url)
  df['Order Date'] = pd.to_datetime(df['Order Date'])
  
  if data_inicial is not None and data_final is not None:
      df = filtroPeriodo(data_inicial, data_final, df)

  df['Hour'] = df['Order Date'].dt.hour 

# let's prepare the value for the x-axis
  hours = [hour for hour, df in df.groupby('Hour')]
  # let's plot it
  plt.figure(figsize=(15, 6)) # figuring the size
  # makes bar plot 
  plt.plot( # plot
      hours, # x-axis
      df.groupby(['Hour']).count() # data
  )
  # let's add grid
  plt.grid(True)
  plt.title( # title
      "Distribuição de pedidos por horário.", 
      weight="bold", # weight
      fontsize=20, # font-size
      pad=30
  )
  plt.xlabel( # x-label
      "Hora do Dia", 
      weight="bold", # weight
      color="purple", # color
      fontsize=20, # font-size
      loc="center" # location
  )
  plt.xticks( # x-ticks
      ticks=hours, # labels
      weight="bold", # weight
      fontsize=15 # font-size
  )
  plt.ylabel( # y-label
      "Numero de Pedidos", 
      weight="bold", # weight
      color="black", # color
      fontsize=20 # font-size
  )
  plt.yticks( # y-ticks
      weight="bold", # weight 
      fontsize=15 # font-size
  )
    
  # Salva o gráfico em um buffer de imagem
  img_buffer = io.BytesIO()
  plt.savefig(img_buffer, format='png')
  img_buffer.seek(0)
  
  # Codifica o buffer da imagem em base64
  return send_file(img_buffer, mimetype='image/png')

@app.route('/vendas-por-valor', methods=['GET'])
def getVendasByValor():
  data_inicial = request.args.get('data_inicial', None)  # Padrão: None
  data_final = request.args.get('data_final', None)

  df = pd.read_csv(url)
  df['Order Date'] = pd.to_datetime(df['Order Date'])
  
  if data_inicial is not None and data_final is not None:
      df = filtroPeriodo(data_inicial, data_final, df)

  univariate_analysis(df['Sales'],'blue','Distribuição de quantidade de vendas por valor total')
  
  # Salva o gráfico em um buffer de imagem
  img_buffer = io.BytesIO()
  plt.savefig(img_buffer, format='png')
  img_buffer.seek(0)
  
  # Codifica o buffer da imagem em base64
  return send_file(img_buffer, mimetype='image/png')

if __name__ == '__main__':
  app.run(port=5000)
