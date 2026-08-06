"""ANSYS API/scripting documentation retrieval.

Cleans the API/scripting markdown docs (removing PDF-conversion noise) and
builds a local SQLite FTS5 index for fast keyword lookup, exposed to the AI via
the tools in tools/docs_tools.py. No network, no extra dependencies (sqlite3 is
in the standard library).
"""
