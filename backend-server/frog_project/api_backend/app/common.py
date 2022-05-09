

def make_json_response(status="success", msg=None, code=None):
    response = {}
    if status is True:
        status = "success"
    elif status is False:
        status = "error"
    response["status"] = status
    if msg is not None:
        response["message"] = msg
    if type(code) is str:
        code = str(code).lower()
        if code in http_response_code:
            return response, http_response_code[code]
    elif type(code) is int:
        return response, code
    return response


http_response_code = {
    "ok": 200,
    "success": 200,
    "created": 201,
    "bad request": 400,
    "unauthorized": 401,
    "unauthenticated": 401,
    "forbidden": 403,
    "not found": 404,
}


# print function that is viewable in Gunicorn log
def _print(*args, **kwargs):
    kwargs['flush'] = True
    print(*args, **kwargs)


