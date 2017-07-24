import requests
from datetime import datetime
from core.models import Clube, Partida


class CartolafcAPIClient():
    """A simple client for querying the CartolaFC API"""

    base_url = 'https://api.cartolafc.globo.com/'

    def _get(self, url, retries=3):
        """Make a GET request to an endpoint defined by 'url'"""
        while retries > 0:
            try:
                response = requests.get(url=url)
                try:
                    response.raise_for_status()
                    return response.json()
                except requests.exceptions.HTTPError as e:
                    self._handle_http_error(e)
            except (requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout) as e:
                retries -= 1
                if not retries:
                    self._handle_connection_error(e)

    def _handle_http_error(self, e):
        """Handle a HTTP error"""
        pass

    def _handle_connection_error(self, e):
        """Handle a persistent connection error or timeout"""
        pass

    def login(self, email, password):
        url = 'https://login.globo.com/api/authentication'
        data = {
            "payload": {
                "email": email,
                "password": password,
                "serviceId": 4728
            },
            "captcha": ""
        }
        r = requests.post(url=url, json=data)
        return r.json()['glbId']

    def clubes(self):
        """Retrieves a list of Clube from the CartolaFC API"""
        url = '{}partidas/1'.format(self.base_url)
        response = self._get(url)
        response_clubes = response["clubes"]
        clube_list = []
        for key in response_clubes:
            clube_json = response_clubes[key]
            clube = Clube(
                id=clube_json["id"],
                nome=clube_json["nome"],
                abreviacao=clube_json["abreviacao"],
                escudo_30x30=clube_json["escudos"]["30x30"],
                escudo_45x45=clube_json["escudos"]["45x45"],
                escudo_60x60=clube_json["escudos"]["60x60"])
            clube_list.append(clube)
        return clube_list

    def partidas(self, rodada):
        """Retrieves a list of Partida from the CartolaFC API"""
        url = '{}partidas/{}'.format(self.base_url, rodada)
        response = self._get(url)
        rodada = response['rodada']
        partida_list_json = response['partidas']
        partida_list = []
        for partida_json in partida_list_json:
            clube_casa_id = partida_json['clube_casa_id']
            clube_visitante_id = partida_json['clube_visitante_id']
            clube_casa = Clube.objects.get(pk=clube_casa_id)
            clube_visitante = Clube.objects.get(pk=clube_visitante_id)
            partida_data = datetime.strptime(partida_json['partida_data'],
                                             '%Y-%m-%d %H:%M:%S')
            partida = Partida(
                clube_casa=clube_casa,
                clube_visitante=clube_visitante,
                clube_casa_posicao=partida_json['clube_casa_posicao'],
                clube_visitante_posicao=partida_json['clube_visitante_posicao'],
                aproveitamento_mandante=''.join(partida_json['aproveitamento_mandante']),
                aproveitamento_visitante=''.join(partida_json['aproveitamento_visitante']),
                placar_oficial_mandante=partida_json['placar_oficial_mandante'],
                placar_oficial_visitante=partida_json['placar_oficial_visitante'],
                partida_data=partida_data,
                local=partida_json['local'],
                valida=partida_json['valida'],
                url_confronto=partida_json['url_confronto'],
                rodada=rodada)
            partida_list.append(partida)
        return partida_list


    # 'X-GLB-Token'
