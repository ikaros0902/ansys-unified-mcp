# -*- coding: utf-8 -*-
"""
SpaceClaim gRPC & AddIns Auto-Starter Script.
"""
import socket

def check_spaceclaim_grpc_status(port=50051):
    """
    檢查 SpaceClaim gRPC 服務連接狀況。
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2.0)
    res = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    if res == 0:
        print("SpaceClaim gRPC 服務在 Port {} 運作中。".format(port))
        return True
    else:
        print("SpaceClaim gRPC 服務在 Port {} 未回應 (連線拒絕或尚未啟動)。".format(port))
        return False

if __name__ == "__main__":
    check_spaceclaim_grpc_status()
