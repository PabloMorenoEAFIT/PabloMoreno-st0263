import argparse
import json
import threading
from flask import Flask, request, jsonify
import grpc
from concurrent import futures
import file_transfer_pb2
import file_transfer_pb2_grpc
import requests

app = Flask(__name__)
data_store = {}
peer_list = []
peer_lock = threading.Lock()

# Define gRPC service
class FileTransferService(file_transfer_pb2_grpc.FileTransferService):
    def GetFile(self, request, context):
        key = request.key
        value = data_store.get(key, None)
        if value:
            return file_transfer_pb2.FileResponse(content=value)
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('File not found')
            return file_transfer_pb2.FileResponse()

# Initialize gRPC server
def start_grpc_server(grpc_port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_transfer_pb2_grpc.add_FileTransferServiceServicer_to_server(FileTransferService(), server)
    server.add_insecure_port(f'[::]:{grpc_port}')
    server.start()
    server.wait_for_termination()

@app.route('/store_data', methods=['POST'])
def store_data():
    data = request.json
    key = data.get('key')
    value = data.get('value')
    if key and value:
        with peer_lock:
            data_store[key] = value
        # Notify other peers
        for peer in peer_list:
            try:
                requests.post(f'{peer}/store_data', json={'key': key, 'value': value})
            except requests.RequestException:
                continue
        return jsonify({"status": "success"}), 200
    return jsonify({"error": "Invalid data"}), 400

@app.route('/get_data/<key>', methods=['GET'])
def get_data(key):
    if key in data_store:
        return jsonify({"value": data_store[key]}), 200
    
    for peer in peer_list:
        try:
            response = requests.get(f'{peer}/get_data/{key}')
            if response.status_code == 200:
                return jsonify(response.json()), 200
        except requests.RequestException:
            continue

    return jsonify({"error": "Not found"}), 404

@app.route('/register_peer', methods=['POST'])
def register_peer():
    peer_address = request.json.get('address')
    if peer_address and peer_address not in peer_list:
        with peer_lock:
            peer_list.append(peer_address)
        # Notify new peer about existing peers
        try:
            existing_peers = peer_list.copy()
            existing_peers.remove(f'http://{args.host}:{args.port}/')
            requests.post(f'{peer_address}/update_peers', json={'peers': existing_peers})
        except requests.RequestException:
            pass
    return jsonify({"status": "success"}), 200

@app.route('/update_peers', methods=['POST'])
def update_peers():
    peers = request.json.get('peers', [])
    with peer_lock:
        for peer in peers:
            if peer not in peer_list:
                peer_list.append(peer)
    return jsonify({"status": "success"}), 200

@app.route('/get_peers', methods=['GET'])
def get_peers():
    with peer_lock:
        return jsonify({"peers": peer_list}), 200

def main(http_port, grpc_port, host):
    # Start gRPC server
    grpc_thread = threading.Thread(target=start_grpc_server, args=(grpc_port,))
    grpc_thread.start()
    
    # Start Flask server
    # app.run(host='0.0.0.0', port=http_port, debug=False, use_reloader=False)

    app.run(host, port=http_port, debug=False, use_reloader=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P2P Peer')
    parser.add_argument('--port', type=int, required=True, help='HTTP port for the peer')
    parser.add_argument('--grpc_port', type=int, required=True, help='gRPC port for the peer')
    parser.add_argument('--host', type=str, required=True, help='Host IP for the peer')
    args = parser.parse_args()
    
    # Initialize the peer and register with an existing node if provided
    existing_peer = input("Ingrese la dirección de un nodo existente (o presione Enter si este es el primer nodo): ")
    if existing_peer:
        try:
            # Register with an existing peer
            requests.post(f'{existing_peer}/register_peer', json={'address': f'http://{args.host}:{args.port}'})
            # Fetch additional peer information
            response = requests.get(f'{existing_peer}/get_peers')
            if response.status_code == 200:
                peers_data = response.json().get('peers', [])
                for peer in peers_data:
                    if peer != f'http://{args.host}:{args.port}':
                        try:
                            requests.post(f'http://{args.host}:{args.port}/update_peers', json={'peers': [peer]})
                        except requests.RequestException:
                            continue
        except requests.RequestException:
            pass
    
    main(args.port, args.grpc_port, args.host)
