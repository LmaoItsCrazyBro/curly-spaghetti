from flask import Flask, request, jsonify
import hashlib
import time

app = Flask(__name__)

keys = {}
banned_ips = {}

def generate_key(hwid):
    return hashlib.sha256((hwid + str(time.time())).encode()).hexdigest()[:32]

@app.route('/generate_key', methods=['POST'])
def generate():
    hwid = request.json.get('hwid')
    ip = request.remote_addr

    if not hwid:
        return jsonify({"error": "Missing HWID"}), 400

    for key, stored_hwid in list(keys.items()):
        if stored_hwid == hwid:
            del keys[key]

    new_key = generate_key(hwid)
    keys[new_key] = hwid

    return jsonify({"message": "Key generated", "key": new_key})

@app.route('/validate_key', methods=['GET'])
def validate():
    key = request.args.get('key')
    hwid = request.args.get('hwid')
    ip = request.remote_addr

    if ip in banned_ips and time.time() < banned_ips[ip]:
        return jsonify({"error": "You are temporarily blacklisted. Try again later."}), 403

    if key in keys and keys[key] == hwid:
        return jsonify({"status": "success", "message": "Key is valid"})
    else:
        banned_ips[ip] = time.time() + 86400
        return jsonify({"error": "Invalid key/HWID detected."}), 403

@app.route('/reset_hwid', methods=['POST'])
def reset():
    key = request.json.get('key')
    new_hwid = request.json.get('hwid')

    if key in keys:
        del keys[key]

        new_key = generate_key(new_hwid)
        keys[new_key] = new_hwid
        return jsonify({"message": "HWID reset successful", "new_key": new_key})
    else:
        return jsonify({"error": "Invalid key"}), 403

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
