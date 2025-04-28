from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/getdatalampu', methods=['GET'])
def get_data():
    return jsonify({"message": "Ini data yg di GET, data lampu 1 mati"})

@app.route('/kirimdataorang', methods=['POST'])
def post_data():
    data = request.get_json()
    if data:
        return jsonify({"message": "Data berhasil diterima", "data": data})
    else:
        return jsonify({"message": "Tidak ada data yang dikirim"}), 400

if __name__ == '__main__':
    app.run(debug=True)
