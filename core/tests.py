import requests
from datetime import datetime
from django.test import TestCase, mock
from core.services import CartolafcAPIClient
from core.models import Clube, Partida


class CustomHTTPException(Exception):
    pass


class CustomConnException(Exception):
    pass


class ServicesTests(TestCase):
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
