# utils/response.py
from flask import jsonify

def api_success(data=None):
    return jsonify({"success": True, "data": data or {}}), 200

def api_error(message, code=500):
    return jsonify({"success": False, "error": {"message": message}}), code
