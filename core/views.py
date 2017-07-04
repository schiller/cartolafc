from django.http import HttpResponse

from core.services import CartolafcAPIClient


def index(request):
    return HttpResponse('Index')


def clubes(request):
    client = CartolafcAPIClient()
    clube_list = client.clubes()
    return HttpResponse(', '.join([clube.abreviacao for clube in clube_list]))
