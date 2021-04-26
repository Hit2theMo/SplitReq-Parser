from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/api/v1/cvparser/single', methods=['POST'])
def parseResume():
    data = request.get_json(force=False)
    print(request.headers)
    print(data)
    return data


@app.route('/api/v1/cvparser/batch', methods=['POST'])
def batchResumeParsing():
    return 'Under development'


if __name__ == '__main__':
    app.run(debug=True)
