import time


def make_resp(result=None, err_code="", msg="Success"):
    return {
        "result": result,
        "err_code": err_code,
        "msg": msg,
        "timestamp": int(time.time()),
    }
