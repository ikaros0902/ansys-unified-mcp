import socket
import json
import os
from typing import Dict, Any

def send_request(payload: Dict[str, Any], host: str = "127.0.0.1", port: int = None, timeout: float = 10.0) -> Dict[str, Any]:
    """
    Send a JSON request to the Mechanical ACT socket server.
    The communication protocol relies on a trailing null-byte ('\\0') for payload separation.
    
    Args:
        payload (dict): The data to send. Should contain at least an 'action' key.
        host (str): The host address.
        port (int): The port. Defaults to WORKBENCH_MCP_PORT env var or 9885.
        timeout (float): Socket connection and read timeout.
        
    Returns:
        dict: The parsed JSON response from Mechanical.
    """
    if port is None:
        port = int(os.environ.get("WORKBENCH_MCP_PORT", 9885))
        
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(timeout)
    
    try:
        client_socket.connect((host, port))
        
        # Serialize payload and add null byte terminator
        request_data = json.dumps(payload) + "\0"
        client_socket.sendall(request_data.encode('utf-8'))
        
        # Read response until null byte
        response_data = bytearray()
        while True:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
                
            response_data.extend(chunk)
            if b"\0" in chunk:
                # Remove null byte and trailing data
                response_data = response_data[:response_data.find(b"\0")]
                break
                
        return json.loads(response_data.decode('utf-8'))
        
    except socket.timeout:
        return {"status": "error", "message": "Socket connection or read timed out."}
    except ConnectionRefusedError:
        return {"status": "error", "message": f"Connection refused on {host}:{port}. Ensure Mechanical Socket Server is running."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        client_socket.close()
