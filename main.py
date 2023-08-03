from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/as', methods=['GET'])
def indexs():
  x=[1,2,3]
  return x

if __name__ == '__main__':
  app.run(port=5000)
