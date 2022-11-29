from django.http import HttpRequest
from ninja import NinjaAPI

api = NinjaAPI()


@api.get("/add")
def add(request: HttpRequest, a: int, b: int):
    return {"result": a + b}
