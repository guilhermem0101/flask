from flask import Flask

import mysql.connector
app = Flask(__name__)



def conecta_db():
  conn = mysql.connector.connect(
    host="aws.connect.psdb.cloud",
    database="analises",
    user="30rxlcu5v3hjy2titdi5",
    password="pscale_pw_Ww7W8E6Mk4GxS2N69j4DSdxt0AqBuppwAhlVRXTiF7Z"

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
