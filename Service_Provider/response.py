from rest_framework.response import Response


def CustomResponse(data, message):
    return Response({"data": data, "message": message})
