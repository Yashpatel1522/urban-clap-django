from rest_framework import status, response


def DataResponse(status=200, message=None, data={}):
    context = {
        "status": status,
        "message": message,
        "data": data
    }
    return context
