# Copyright (c) Alex Ellis 2017. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

from flask import Flask, request
from function import handler
from waitress import serve
import os
import importlib
import time
#import traceback

app = Flask(__name__)

# distutils.util.strtobool() can throw an exception
def is_true(val):
    return len(val) > 0 and val.lower() == "true" or val == "1"

@app.before_request
def fix_transfer_encoding():
    """
    Sets the "wsgi.input_terminated" environment flag, thus enabling
    Werkzeug to pass chunked requests as streams.  The gunicorn server
    should set this, but it's not yet been implemented.
    """

    transfer_encoding = request.headers.get("Transfer-Encoding", None)
    if transfer_encoding == u"chunked":
        request.environ["wsgi.input_terminated"] = True

@app.route("/", defaults={"path": ""}, methods=["POST", "GET"])
@app.route("/<path:path>", methods=["POST", "GET"])
def main_route(path):
    raw_body = os.getenv("RAW_BODY", "false")

    as_text = True

    if is_true(raw_body):
        as_text = False
    
    #try:
    ret = None
    #print("request", request)
    if 'update' in request.headers:
        try:
            with open("/home/app/function/handler.py", "w+") as f:
                f.writelines(request.get_data(as_text=as_text))
            ret = "Done"
            importlib.reload(handler)
        except Exception as e:
            ret = str(e)
        finally:
            return ret
    else:
        ret = handler.handle(request.get_data(as_text=as_text))
        return ret
    #except Exception e:
       #traceback.print_exc()
       #return str(e)

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
