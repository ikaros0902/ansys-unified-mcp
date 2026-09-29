import System
import clr
clr.AddReference("System.Web.Extensions")
import System.Web.Script.Serialization
import System.Threading
import System.Net
import System.Net.Sockets
import System.Text
import os
import sys
import __builtin__
import traceback

# Port configuration from environment variable, default to 9885
PORT = int(os.environ.get("WORKBENCH_MCP_PORT", 9885))

class MechanicalSocketServer(object):
    """
    TCP Socket Server running inside ANSYS Mechanical ACT environment.
    Provides low-latency communication for external MCP server.
    """
    def __init__(self, port):
        self.port = port
        self.running = False
        self.listener = None
        self.serializer = System.Web.Script.Serialization.JavaScriptSerializer()

    def start(self):
        """
        Start the TCP listener loop.
        """
        self.running = True
        try:
            ip_address = System.Net.IPAddress.Parse("127.0.0.1")
            self.listener = System.Net.Sockets.TcpListener(ip_address, self.port)
            self.listener.Start()
            if 'ExtAPI' in globals():
                ExtAPI.Log.WriteMessage("MCP Socket Server started on port {}".format(self.port))
            
            while self.running:
                if not self.listener.Pending():
                    System.Threading.Thread.Sleep(50)
                    continue
                
                client = self.listener.AcceptTcpClient()
                self.handle_client(client)
        except Exception as e:
            if 'ExtAPI' in globals():
                ExtAPI.Log.WriteError("MCP Socket Server error: " + str(e))
        finally:
            if self.listener:
                self.listener.Stop()

    def handle_client(self, client):
        """
        Handle incoming TCP client connection, read until null-byte,
        process request and return serialized response with null-byte.
        """
        stream = client.GetStream()
        buffer = System.Array.CreateInstance(System.Byte, 4096)
        data = ""
        
        try:
            while True:
                bytes_read = stream.Read(buffer, 0, buffer.Length)
                if bytes_read == 0:
                    break
                
                chunk = System.Text.Encoding.UTF8.GetString(buffer, 0, bytes_read)
                data += chunk
                
                if data.endswith("\0"):
                    data = data[:-1]
                    break
            
            response = self.process_request(data)
            
            response_json = self.serializer.Serialize(response) + "\0"
            response_bytes = System.Text.Encoding.UTF8.GetBytes(response_json)
            stream.Write(response_bytes, 0, response_bytes.Length)
        except Exception as e:
            if 'ExtAPI' in globals():
                ExtAPI.Log.WriteError("Error handling client: " + str(e))
        finally:
            client.Close()

    def process_request(self, json_data):
        """
        Process the deserialized JSON request dictionary.
        """
        try:
            req = self.serializer.DeserializeObject(json_data)
            
            # IronPython .NET Dictionary compatibility
            action = req["action"] if req.ContainsKey("action") else None
            
            if action == "execute_script":
                script = req["script"] if req.ContainsKey("script") else ""
                
                # Expose Mechanical APIs to the script context
                local_vars = {}
                if 'ExtAPI' in globals():
                    local_vars["ExtAPI"] = ExtAPI
                if 'DataModel' in globals():
                    local_vars["DataModel"] = DataModel
                if 'Tree' in globals():
                    local_vars["Tree"] = Tree
                if 'Model' in globals():
                    local_vars["Model"] = Model
                    
                exec script in globals(), local_vars
                result = local_vars.get("result", "Script executed successfully. Assign 'result' variable to return data.")
                return {"status": "success", "result": result}
                
            elif action == "ping":
                return {"status": "success", "result": "pong"}
                
            else:
                return {"status": "error", "message": "Unknown action"}
                
        except Exception as e:
            tb = traceback.format_exc()
            return {"status": "error", "message": str(e), "traceback": tb}

    def stop(self):
        """
        Stop the server listener.
        """
        self.running = False


def start_server():
    """
    Ensure only one instance of the server runs by utilizing __builtin__ state storage.
    """
    global PORT
    
    # Check if a server is already running to prevent duplicates
    if hasattr(__builtin__, "_WORKBENCH_MCP_SOCKET_STATE"):
        state = getattr(__builtin__, "_WORKBENCH_MCP_SOCKET_STATE")
        if type(state) is dict and state.get("running", False):
            server = state.get("server")
            if server:
                server.stop()
            thread = state.get("thread")
            if thread and thread.IsAlive:
                thread.Join(1000)
                
    server = MechanicalSocketServer(PORT)
    thread = System.Threading.Thread(System.Threading.ThreadStart(server.start))
    thread.IsBackground = True
    thread.Start()
    
    # Save state reference
    setattr(__builtin__, "_WORKBENCH_MCP_SOCKET_STATE", {
        "running": True,
        "server": server,
        "thread": thread
    })

start_server()
