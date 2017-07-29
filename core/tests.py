import requests
import csv
from datetime import datetime
from django.test import TestCase, mock
from core.services import CartolafcAPIClient, CartolaCsvReader
from core.models import Clube, Partida, Atleta, Posicao, Status, Scout


class CustomHTTPException(Exception):
    pass


class CustomConnException(Exception):
    pass


class CartolafcAPIClientTests(TestCase):
    def setUp(self):
        self.client = CartolafcAPIClient()
        Clube.objects.create(
            id=262, nome='Flamengo', abreviacao='FLA',
            escudo_30x30='https://s.glbimg.com/es/sde/f/equipes/2013/12/16/flamengo_30x30.png',
            escudo_45x45='https://s.glbimg.com/es/sde/f/equipes/2013/12/16/flamengo_45x45.png',
            escudo_60x60='https://s.glbimg.com/es/sde/f/equipes/2014/04/14/flamengo_60x60.png')
        Clube.objects.create(
            id=263, nome='Botafogo', abreviacao='BOT',
            escudo_30x30='https://s.glbimg.com/es/sde/f/equipes/2013/12/16/botafogo_30x30.png',
            escudo_45x45='https://s.glbimg.com/es/sde/f/equipes/2013/12/16/botafogo_45x45.png',
            escudo_60x60='https://s.glbimg.com/es/sde/f/equipes/2014/04/14/botafogo_60x60.png')
        Atleta.objects.create(
            id=68698,
            nome='Bruno César Pereira da Silva',
            apelido='Bruno Silva',
            foto='https://s.glbimg.com/es/sde/f/2016/05/20/473777983ee50165bf691b0f029cac11_FORMATO.png')
        Posicao.objects.create(id=4, nome='Meia', abreviacao='mei')
        Status.objects.create(id=7, nome='Provável')

    @mock.patch('core.services.requests.get')
    def test_get(self, mock_get):
        """Test getting a 200 OK response from the _get method of
        MyAPIClient."""
        # Construct our mock response object, giving it relevant
        # expected behaviours
        mock_response = mock.Mock()
        expected_dict = {
            "spam": [
                "eggs",
                "sausage",
            ]
        }
        mock_response.json.return_value = expected_dict

        # Assign our mock response as the result of our patched function
        mock_get.return_value = mock_response

        url = 'http://api.spam.com/eggs/'
        response_dict = self.client._get(url=url)

        # Check that our function made the expected internal calls
        mock_get.assert_called_once_with(url=url)
        self.assertEqual(1, mock_response.json.call_count)

        # If we want, we can check the contents of the response
        self.assertEqual(response_dict, expected_dict)

    @mock.patch('core.services.CartolafcAPIClient._handle_http_error')
    @mock.patch('core.services.requests.get')
    def test_get_http_error(self, mock_get, mock_http_error_handler):
        """Test getting a HTTP error in the _get method of
        CartolafcAPIClient."""
        # Construct our mock response object, giving it relevant
        # expected behaviours
        mock_response = mock.Mock()
        http_error = requests.exceptions.HTTPError()
        mock_response.raise_for_status.side_effect = http_error

        # Assign our mock response as the result of our patched function
        mock_get.return_value = mock_response

        # Make our patched error handler raise a custom exception
        mock_http_error_handler.side_effect = CustomHTTPException()

        url = 'http://api.spam.com/eggs/'
        with self.assertRaises(CustomHTTPException):
            self.client._get(url=url)

        # Check that our function made the expected internal calls
        mock_get.assert_called_once_with(url=url)
        self.assertEqual(1, mock_response.raise_for_status.call_count)

        # Make sure we did not attempt to deserialize the response
        self.assertEqual(0, mock_response.json.call_count)

        # Make sure our HTTP error handler is called
        mock_http_error_handler.assert_called_once_with(http_error)

    @mock.patch('core.services.CartolafcAPIClient._handle_connection_error')
    @mock.patch('core.services.requests.get')
    def test_get_connection_error(self, mock_get, mock_conn_error_handler):
        """Test getting a persistent connection error in the _get
        method of CartolafcAPIClient."""
        # Make our patched `requests.get` raise a connection error
        conn_error = requests.exceptions.ConnectionError()
        mock_get.side_effect = conn_error

        # Make our patched error handler raise a custom exception
        mock_conn_error_handler.side_effect = CustomConnException()

        url = 'http://api.spam.com/eggs/'
        with self.assertRaises(CustomConnException):
            self.client._get(url=url)

        # Check that our function made the expected internal calls
        expected_calls = [mock.call(url=url)] * 3
        self.assertEqual(expected_calls, mock_get.call_args_list)

        # Make sure our connection error handler is called
        mock_conn_error_handler.assert_called_once_with(conn_error)

    @mock.patch('core.services.requests.get')
    def test_get_connection_error_then_success(self, mock_get):
        """Test getting a connection error, then a successful response,
        in the _get method of CartolafcAPIClient."""
        # Construct our mock response object for the success case
        mock_response = mock.Mock()
        expected_dict = {
            "spam": [
                "eggs",
                "sausage",
            ]
        }
        mock_response.json.return_value = expected_dict

        # Make an instance of ConnectionError for our failure case
        conn_error = requests.exceptions.ConnectionError()

        # Give our patched get a list of behaviours to display
        mock_get.side_effect = [conn_error, conn_error, mock_response]

        url = 'http://api.spam.com/eggs/'
        response_dict = self.client._get(url=url)

        # Check that our function made the expected internal calls
        expected_calls = [mock.call(url=url)] * 3
        self.assertEqual(expected_calls, mock_get.call_args_list)
        self.assertEqual(1, mock_response.json.call_count)

        # Check the result
        self.assertEqual(response_dict, expected_dict)

    @mock.patch('core.services.CartolafcAPIClient._handle_http_error')
    @mock.patch('core.services.requests.get')
    def test_get_connection_error_then_http_error(
            self, mock_get, mock_http_error_handler):
        """Test getting a connection error, then a http error, in the
        _get method of CartolafcAPIClient."""
        http_error = requests.exceptions.HTTPError()
        conn_error = requests.exceptions.ConnectionError()

        # Construct our mock response object, giving it relevant
        # expected behaviours
        mock_response = mock.Mock()
        mock_response.raise_for_status.side_effect = http_error
        mock_get.side_effect = [conn_error, mock_response]
        # Make our patched error handler raise a custom exception
        mock_http_error_handler.side_effect = CustomHTTPException()

        url = 'http://api.spam.com/eggs/'
        with self.assertRaises(CustomHTTPException):
            self.client._get(url=url)

        expected_calls = [mock.call(url=url)] * 2
        self.assertEqual(expected_calls, mock_get.call_args_list)
        self.assertEqual(1, mock_response.raise_for_status.call_count)
        # Assert there was no attempt to deserialize the response
        self.assertEqual(0, mock_response.json.call_count)

        # Make sure our HTTP error handler is called
        mock_http_error_handler.assert_called_once_with(http_error)

    @mock.patch('core.services.requests.post')
    def test_login(self, mock_post):
        email = 'spam'
        password = 'eggs'
        url = 'https://login.globo.com/api/authentication'
        data = {
            "payload": {
                "email": email,
                "password": password,
                "serviceId": 4728
            },
            "captcha": ""
        }
        expected_return = 'spam eggs'
        mock_response = mock.Mock()
        mock_response.json.return_value = {'glbId': expected_return}
        mock_post.return_value = mock_response

        return_value = self.client.login(email, password)

        mock_post.assert_called_once_with(url=url, json=data)
        self.assertEqual(1, mock_response.json.call_count)
        self.assertEqual(return_value, expected_return)

    @mock.patch('core.services.CartolafcAPIClient._get')
    def test_clubes(self, mock_get):
        """Test getting a list of Clube from the clubes method of
        CartolafcAPIClient."""
        expected_response = {
            "clubes": {
                "262": {
                    "id": 262,
                    "nome": "Flamengo",
                    "abreviacao": "FLA",
                    "posicao": 3,
                    "escudos": {
                        "60x60": "https://s.glbimg.com/es/sde/f/equipes/2014/04/14/flamengo_60x60.png",
                        "45x45": "https://s.glbimg.com/es/sde/f/equipes/2013/12/16/flamengo_45x45.png",
                        "30x30": "https://s.glbimg.com/es/sde/f/equipes/2013/12/16/flamengo_30x30.png"}},
                "263": {
                    "id": 263,
                    "nome": "Botafogo",
                    "abreviacao": "BOT",
                    "posicao": 7,
                    "escudos": {
                        "60x60": "https://s.glbimg.com/es/sde/f/equipes/2014/04/14/botafogo_60x60.png",
                        "45x45": "https://s.glbimg.com/es/sde/f/equipes/2013/12/16/botafogo_45x45.png",
                        "30x30": "https://s.glbimg.com/es/sde/f/equipes/2013/12/16/botafogo_30x30.png"}}}}
        expected_output = [
            Clube(262, "Flamengo", "FLA",
                  "https://s.glbimg.com/es/sde/f/equipes/2013/12/16/flamengo_30x30.png",
                  "https://s.glbimg.com/es/sde/f/equipes/2013/12/16/flamengo_45x45.png",
                  "https://s.glbimg.com/es/sde/f/equipes/2014/04/14/flamengo_60x60.png"),
            Clube(263, "Botafogo", "BOT",
                  "https://s.glbimg.com/es/sde/f/equipes/2013/12/16/botafogo_30x30.png",
                  "https://s.glbimg.com/es/sde/f/equipes/2013/12/16/botafogo_45x45.png",
                  "https://s.glbimg.com/es/sde/f/equipes/2014/04/14/botafogo_60x60.png")]
        mock_get.return_value = expected_response
        expected_url = 'https://api.cartolafc.globo.com/partidas/1'

        output = self.client.clubes()

        mock_get.assert_called_once_with(expected_url)
        self.assertEqual(1, mock_get.call_count)
        self.assertEqual(output, expected_output)

    @mock.patch('core.services.CartolafcAPIClient._get')
    def test_partidas(self, mock_get):
        """Tests getting a list of Partida from the partidas method of
        CartolafcAPIClient."""
        expected_response = {
            "partidas": [{
                'clube_casa_id': 262,
                'clube_visitante_id': 263,
                'clube_casa_posicao': 4,
                'clube_visitante_posicao': 7,
                'aproveitamento_mandante': ['v', 'd', 'e', 'e', 'v'],
                'aproveitamento_visitante': ['e', 'v', 'v', 'e', 'e'],
                'placar_oficial_mandante': 0,
                'placar_oficial_visitante': 0,
                'partida_data': '2017-06-04 11:00:00',
                'local': 'Raulino de Oliveira',
                'valida': True,
                'url_confronto': 'http://globoesporte.globo.com/rj/futebol/brasileirao-serie-a/jogo/04-06-2017/flamengo-botafogo',
                'url_transmissao': ''}],
            "rodada": 4
        }

        clube_casa = Clube.objects.get(pk=262)
        clube_visitante = Clube.objects.get(pk=263)
        expected_output = [
            Partida(
                clube_casa=clube_casa,
                clube_visitante=clube_visitante,
                clube_casa_posicao=4,
                clube_visitante_posicao=7,
                aproveitamento_mandante="vdeev",
                aproveitamento_visitante="evvee",
                placar_oficial_mandante=0,
                placar_oficial_visitante=0,
                partida_data=datetime(year=2017, month=6, day=4, hour=11),
                local='Raulino de Oliveira',
                valida=True,
                url_confronto='http://globoesporte.globo.com/rj/futebol/brasileirao-serie-a/jogo/04-06-2017/flamengo-botafogo',
                rodada=4
            )
        ]

        expected_url = 'https://api.cartolafc.globo.com/partidas/4'
        mock_get.return_value = expected_response

        output = self.client.partidas(4)

        mock_get.assert_called_once_with(expected_url)
        self.assertEqual(1, mock_get.call_count)
        self.assertEqual(output[0].clube_casa, expected_output[0].clube_casa)
        self.assertEqual(output[0].partida_data,
                         expected_output[0].partida_data)

    @mock.patch('core.services.CartolafcAPIClient._get')
    def test_atletas(self, mock_get):
        """Test getting a list of Atleta from the atletas method of
        CartolafcAPIClient."""
        expected_response = {"atletas": [{
            "nome": "Rodrigo Baldasso da Costa",
            "apelido": "Rodrigo",
            "foto": "https://s.glbimg.com/es/sde/f/2017/06/13/a5cb57a41ef2b2308c98b76ba24b430a_FORMATO.png",
            "atleta_id": 37644,
            "rodada_id": 12,
            "clube_id": 303,
            "posicao_id": 3,
            "status_id": 2,
            "pontos_num": 5.2,
            "preco_num": 9.04,
            "variacao_num": 1.31,
            "media_num": 3.17,
            "jogos_num": 8,
            "scout": {
                "CA": 2, "CV": 1, "FC": 5, "FD": 2, "FF": 5, "FS": 15, "I": 1,
                "PE": 14, "RB": 8, "SG": 3}}]}

        expected_output = [Atleta(
            id=37644, nome='Rodrigo Baldasso da Costa', apelido='Rodrigo',
            foto='https://s.glbimg.com/es/sde/f/2017/06/13/a5cb57a41ef2b2308c98b76ba24b430a_FORMATO.png')]

        mock_get.return_value = expected_response
        expected_url = 'https://api.cartolafc.globo.com/atletas/mercado'

        output = self.client.atletas()

        mock_get.assert_called_once_with(expected_url)
        self.assertEqual(1, mock_get.call_count)
        self.assertEqual(output, expected_output)

    @mock.patch('core.services.CartolafcAPIClient._get')
    def test_posicoes(self, mock_get):
        """Test getting a list of Posicao from the posicoes method of
        CartolafcAPIClient."""
        expected_response = {"posicoes": {
            "1": {"id": 1, "nome": "Goleiro", "abreviacao": "gol"},
            "2": {"id": 2, "nome": "Lateral", "abreviacao": "lat"}}}

        expected_output = [
            Posicao(id=1, nome='Goleiro', abreviacao='gol'),
            Posicao(id=2, nome='Lateral', abreviacao='lat')]

        mock_get.return_value = expected_response
        expected_url = 'https://api.cartolafc.globo.com/atletas/mercado'

        output = self.client.posicoes()

        mock_get.assert_called_once_with(expected_url)
        self.assertEqual(1, mock_get.call_count)
        self.assertEqual(output, expected_output)

    @mock.patch('core.services.CartolafcAPIClient._get')
    def test_status(self, mock_get):
        """Test getting a list of Status from the status method of
        CartolafcAPIClient."""
        expected_response = {"status": {
            "2": {"id": 2, "nome": "Dúvida"},
            "3": {"id": 3, "nome": "Suspenso"}}}

        expected_output = [
            Status(id=2, nome='Dúvida'),
            Status(id=3, nome='Suspenso')]

        mock_get.return_value = expected_response
        expected_url = 'https://api.cartolafc.globo.com/atletas/mercado'

        output = self.client.status()

        mock_get.assert_called_once_with(expected_url)
        self.assertEqual(1, mock_get.call_count)
        self.assertEqual(output, expected_output)

    @mock.patch('core.services.CartolafcAPIClient._get')
    def test_scouts(self, mock_get):
        """Tests getting a list of Scout from the scouts method of
        CartolafcAPIClient."""
        expected_response = {"atletas": [{
            "nome": "Bruno César Pereira da Silva",
            "apelido": "Bruno Silva",
            "foto": "https://s.glbimg.com/es/sde/f/2016/05/20/473777983ee50165bf691b0f029cac11_FORMATO.png",
            "atleta_id": 68698,
            "rodada_id": 12,
            "clube_id": 263,
            "posicao_id": 4,
            "status_id": 7,
            "pontos_num": 3.6,
            "preco_num": 13.04,
            "variacao_num": 0.46,
            "media_num": 5.83,
            "jogos_num": 11,
            "scout": {
                "A": 2, "CA": 5, "FC": 18, "FD": 3, "FF": 7, "FS": 19, "G": 4,
                "PE": 40, "RB": 21}}]}

        atleta = Atleta.objects.get(pk=68698)
        clube = Clube.objects.get(pk=263)
        posicao = Posicao.objects.get(pk=4)
        status = Status.objects.get(pk=7)

        expected_output = [Scout(ano=2017,
                                 rodada=12,
                                 atleta=atleta,
                                 clube=clube,
                                 posicao=posicao,
                                 status=status,
                                 pontos_num=3.6,
                                 preco_num=13.04,
                                 variacao_num=0.46,
                                 media_num=5.83,
                                 jogos_num=11,
                                 scouts_A=2, scouts_CA=5, scouts_FC=18,
                                 scouts_FD=3, scouts_FF=7, scouts_FS=19,
                                 scouts_G=4, scouts_PE=40, scouts_RB=21)]

        expected_url = 'https://api.cartolafc.globo.com/atletas/mercado'
        mock_get.return_value = expected_response

        output = self.client.scouts()

        mock_get.assert_called_once_with(expected_url)
        self.assertEqual(1, mock_get.call_count)
        self.assertEqual(output[0].atleta, expected_output[0].atleta)
        self.assertEqual(output[0].clube, expected_output[0].clube)
        self.assertEqual(output[0].posicao, expected_output[0].posicao)
        self.assertEqual(output[0].status, expected_output[0].status)


class CartolaCsvReaderTests(TestCase):
    def setUp(self):
        self.csv_reader = CartolaCsvReader()
        Clube.objects.create(
            id=262, nome='Flamengo', abreviacao='FLA',
            escudo_30x30='https://s.glbimg.com/es/sde/f/equipes/2013/12/16/flamengo_30x30.png',
            escudo_45x45='https://s.glbimg.com/es/sde/f/equipes/2013/12/16/flamengo_45x45.png',
            escudo_60x60='https://s.glbimg.com/es/sde/f/equipes/2014/04/14/flamengo_60x60.png')
        Clube.objects.create(
            id=263, nome='Botafogo', abreviacao='BOT',
            escudo_30x30='https://s.glbimg.com/es/sde/f/equipes/2013/12/16/botafogo_30x30.png',
            escudo_45x45='https://s.glbimg.com/es/sde/f/equipes/2013/12/16/botafogo_45x45.png',
            escudo_60x60='https://s.glbimg.com/es/sde/f/equipes/2014/04/14/botafogo_60x60.png')

    @mock.patch('core.services.csv.reader')
    def test_partidas(self, mock_read_csv):
        csv_path = '/core/sample_csv/partidas.csv'
        with open(csv_path) as csvfile:
            expected_reader = csv.reader(csvfile)

        clube_casa = Clube.objects.get(pk=262)
        clube_visitante = Clube.objects.get(pk=263)
        expected_output = [Partida(
            clube_casa=clube_casa,
            clube_visitante=clube_visitante,
            clube_casa_posicao=4,
            clube_visitante_posicao=7,
            aproveitamento_mandante="vdeev",
            aproveitamento_visitante="evvee",
            placar_oficial_mandante=0,
            placar_oficial_visitante=0,
            partida_data=datetime(year=2017, month=6, day=4, hour=11),
            local='Raulino de Oliveira',
            valida=True,
            url_confronto='http://globoesporte.globo.com/rj/futebol/brasileirao-serie-a/jogo/04-06-2017/flamengo-botafogo',
            rodada=4)]

        expected_path = 'spam/eggs'
        mock_read_csv.return_value = expected_reader

        output = self.csv_reader.partidas(expected_path)

        mock_read_csv.assert_called_once_with(expected_path)
        self.assertEqual(1, mock_read_csv.call_count)
        self.assertEqual(output[0].clube_casa, expected_output[0].clube_casa)
        self.assertEqual(
            output[0].partida_data, expected_output[0].partida_data)
