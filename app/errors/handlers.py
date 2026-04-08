from flask import jsonify
from flask import Flask 
from app.shared import APIException
import traceback


def handle_api_exception(error):
    return jsonify({
        "success": False,
        "error": {
            "code": error.code,
            "message": error.message
        }
    }), error.status_code


def handle_unexpected_error(error):
    # Log full traceback (replace with proper logger later)
    print(traceback.format_exc())

    return jsonify({
        "success": False,
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Something went wrong"
        }
    }), 500


def register_error_handlers(app: Flask):
    app.register_error_handler(APIException, handle_api_exception)
    app.register_error_handler(Exception, handle_unexpected_error)