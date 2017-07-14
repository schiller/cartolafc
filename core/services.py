import requests
from core.models import Clube


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
        # TODO: usar partidas para popular clubes (so clubes que importam)
        url = '{}clubes'.format(self.base_url)
        response = self._get(url)

        clube_list = []
        for key in response:
            value = response[key]
            clube = Clube(value["id"], value["nome"], value["abreviacao"])
            clube_list.append(clube)

        return clube_list


    # 'X-GLB-Token'

## Url's da API obtidas do site oficial do CartolaFC 2017.

## BEING USED
# mercado: "//api.cartolafc.globo.com/atletas/mercado",
# clubes: "//api.cartolafc.globo.com/clubes",
# partidas: "//api.cartolafc.globo.com/partidas/{rodada}",

## AUTH
# auth: "//api.cartolafc.globo.com/auth/time/info",
# amigos_cartola: "//api.cartolafc.globo.com/auth/amigos",
# atleta_pontuacao: "//api.cartolafc.globo.com/auth/mercado/atleta/{idAtleta}/pontuacao",
# banir_times: "//api.cartolafc.globo.com/auth/liga/{slugLiga}/banir",
# clear_cartoleiro_pro: "//api.cartolafc.globo.com/auth/time/pro",
# convidar_times: "//api.cartolafc.globo.com/auth/liga/{slugLiga}/convidar",
# convite: "//api.cartolafc.globo.com/auth/mensagem/{id}/",
# historico_transacoes: "//api.cartolafc.globo.com/auth/time/historico/",
# liga: "//api.cartolafc.globo.com/auth/liga/{slug}",
# liga_associacao: "//api.cartolafc.globo.com/auth/liga/{slug}/associacao",
# liga_criar: "//api.cartolafc.globo.com/auth/liga/criar",
# ligas_do_usuario: "//api.cartolafc.globo.com/auth/ligas",
# noticias: "//api.cartolafc.globo.com/auth/noticias",
# performance_time: "//api.cartolafc.globo.com/auth/stats/historico",
# reativar_ligas_acao: "//api.cartolafc.globo.com/auth/reativar/liga/{slug}",
# reativar_ligas: "//api.cartolafc.globo.com/auth/reativar/ligas",
# salvarTime: "//api.cartolafc.globo.com/auth/time/salvar",
# time: "//api.cartolafc.globo.com/auth/time",

## LOGGED
# campeoes_ligas_nacionais: "//api.cartolafc.globo.com/logged/ligas/campeoes-nacionais",
# check_slug_time: "//api.cartolafc.globo.com/logged/time/?search=",
# check_slug_liga: "//api.cartolafc.globo.com/logged/liga/?search=",
# criar_time: "//api.cartolafc.globo.com/logged/time/criar",
# performance_atletas: "//api.cartolafc.globo.com/logged/stats/atletas",
# validarAssinaturaUsuarioSemTime: "//api.cartolafc.globo.com/logged/time/validar-pro",

## OTHER
# atletas_parciais: "//api.cartolafc.globo.com/atletas/pontuados",
# busca_ligas: "//api.cartolafc.globo.com/ligas?q=",
# busca_times: "//api.cartolafc.globo.com/times?q=",
# ligasPatrocinadores: "//api.cartolafc.globo.com/patrocinadores",
# mercado_destaques: "//api.cartolafc.globo.com/mercado/destaques",
# posrodada_destaques: "//api.cartolafc.globo.com/pos-rodada/destaques",
# rodadas: "//api.cartolafc.globo.com/rodadas",
# status_mercado: "//api.cartolafc.globo.com/mercado/status",
# time_adv: "//api.cartolafc.globo.com/time/slug/{slug}/{rodada}", // opcionalmente aceita a rodada
# time_id: "//api.cartolafc.globo.com/time/id/{id}/{rodada}" // opcionalmente aceita a rodada
