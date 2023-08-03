from flask import Flask

import mysql.connector
app = Flask(__name__)



def conecta_db():
  conn = mysql.connector.connect(
    host="aws.connect.psdb.cloud",
    database="analises",
    user="dlo52g6lwmbn6rljgzk3",
    password="pscale_pw_LDivQlIGspBLTK8z7Ar0iVvmqLQpZXP9ArwFRBYGidf",
    ssl_verify_identity = True,
    ssl_ca='cacert-2023-05-30.pem',
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
