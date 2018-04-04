from flask import Flask, request

app = Flask(__name__)

@app.route('/',methods=['POST', 'GET'])
def hello():
    text = request.args.get('text')
    return '<h1>'+text+'<h1>'

if __name__ == '__main__':
    app.run(debug=True, threaded=True)