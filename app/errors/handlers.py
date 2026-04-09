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
    app.register_error_handler(APIException, handle_api_exception)      #Handles the expected errors and we have applied this first so the expected errors get stuck here first and the other errors will be handled by the function at the bottom
    app.register_error_handler(Exception, handle_unexpected_error)      #Handles any unexpected errors that might occur in the application and we have applied this after the expected error handler so that it can catch any errors that are not handled by the expected error handler.
                                                                        #If the unexpected error handler was registered before the expected error handler, then it would catch all exceptions, including the expected ones, and the expected error handler would never get a chance to handle its specific exceptions.