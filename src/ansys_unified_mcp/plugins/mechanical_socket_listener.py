"""Backward-compatibility shim for ansys_unified_mcp.plugins.mechanical_socket_listener."""
# Forward all symbols
with open(__file__.replace("plugins\\mechanical_socket_listener.py", "products\\mechanical\\plugins\\mechanical_socket_listener.py").replace("plugins/mechanical_socket_listener.py", "products/mechanical/plugins/mechanical_socket_listener.py"), "r", encoding="utf-8") as _f:
    exec(_f.read())
