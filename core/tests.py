import requests
from django.test import TestCase, mock
from core.services import CartolafcAPIClient
from core.models import Clube


class CustomHTTPException(Exception):
    pass


class CustomConnException(Exception):
    pass


class ServicesTests(TestCase):
    def setUp(self):
        self.client = CartolafcAPIClient()

    @mock.patch('core.services.requests.get')
    def test_get(self, mock_get):
        """
        Test getting a 200 OK response from the _get method of MyAPIClient.
        """
        # Construct our mock response object, giving it relevant expected
        # behaviours
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
        """
        Test getting a HTTP error in the _get method of CartolafcAPIClient.
        """
        # Construct our mock response object, giving it relevant expected
        # behaviours
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
        """
        Test getting a persistent connection error in the _get method of
        CartolafcAPIClient.
        """
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
        """
        Test getting a connection error, then a successful response,
        in the _get method of CartolafcAPIClient.
        """
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
    def test_get_connection_error_then_http_error(self,
                                                  mock_get,
                                                  mock_http_error_handler):
        """
        Test getting a connection error, then a http error, in the _get method
        of CartolafcAPIClient.
        """
        http_error = requests.exceptions.HTTPError()
        conn_error = requests.exceptions.ConnectionError()

        # Construct our mock response object, giving it relevant expected
        # behaviours
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
        """
        Test getting a list of Clube from the clubes method of
        CartolafcAPIClient.
        """
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
        expected_url = 'https://api.cartolafc.globo.com/partidas/0'

        output = self.client.clubes()

        mock_get.assert_called_once_with(expected_url)
        self.assertEqual(1, mock_get.call_count)
        self.assertEqual(output, expected_output)

    # @mock.patch('core.services.CartolafcAPIClient._get')
    # def test_mercado(self, mock_get):
    #     """
    #     Test getting a list of Jogador from the mercado method of
    #     CartolafcAPIClient.
    #     """
    #     expected_response = {
    #         "atletas":[
    #             {
    #                 "nome":"Thiago Neves Augusto",
    #                 "apelido":"Thiago Neves",
    #                 "foto":"https://s.glbimg.com/es/sde/f/2017/02/19/6bb6e70216d205ad23e44268eba27692_FORMATO.png",
    #                 "atleta_id":38277,
    #                 "rodada_id":11,
    #                 "clube_id":283,
    #                 "posicao_id":4,
    #                 "status_id":7,
    #                 "pontos_num":9.6,
    #                 "preco_num":18.06,
    #                 "variacao_num":0.07,
    #                 "media_num":6.65,
    #                 "jogos_num":8,
    #                 "scout":{"A":1,"CA":1,"FC":10,"FD":12,"FF":6,"FS":16,"G":4,"I":2,"PE":34,"RB":6}
    #             },
    #             {
    #                 "nome":"Fábio Santos Romeu",
    #                 "apelido":"Fábio Santos",
    #                 "foto":"https://s.glbimg.com/es/sde/f/2017/04/03/513ae4d7abe5f2024ee9a5cfa9c87bd4_FORMATO.png",
    #                 "atleta_id":38229,
    #                 "rodada_id":11,
    #                 "clube_id":282,
    #                 "posicao_id":2,
    #                 "status_id":7,
    #                 "pontos_num":0.1,
    #                 "preco_num":1.72,
    #                 "variacao_num":-0.09,
    #                 "media_num":0.82,
    #                 "jogos_num":9,
    #                 "scout":{"CA":4,"FC":12,"FF":3,"FS":16,"I":2,"PE":32,"RB":7,"SG":2}
    #             }],
    #         "clubes":{
    #             "262":{
    #                 "id":262,
    #                 "nome":"Flamengo",
    #                 "abreviacao":"FLA",
    #                 "posicao":3,
    #                 "escudos":{
    #                     "60x60":"https://s.glbimg.com/es/sde/f/equipes/2014/04/14/flamengo_60x60.png",
    #                     "45x45":"https://s.glbimg.com/es/sde/f/equipes/2013/12/16/flamengo_45x45.png",
    #                     "30x30":"https://s.glbimg.com/es/sde/f/equipes/2013/12/16/flamengo_30x30.png"}},
    #             "263":{
    #                 "id":263,
    #                 "nome":"Botafogo",
    #                 "abreviacao":"BOT",
    #                 "posicao":10,
    #                 "escudos":{
    #                     "60x60":"https://s.glbimg.com/es/sde/f/equipes/2014/04/14/botafogo_60x60.png",
    #                     "45x45":"https://s.glbimg.com/es/sde/f/equipes/2013/12/16/botafogo_45x45.png",
    #                     "30x30":"https://s.glbimg.com/es/sde/f/equipes/2013/12/16/botafogo_30x30.png"}}},
    #         "posicoes":{
    #             "1":{"id":1,"nome":"Goleiro","abreviacao":"gol"},
    #             "2":{"id":2,"nome":"Lateral","abreviacao":"lat"},
    #             "3":{"id":3,"nome":"Zagueiro","abreviacao":"zag"},
    #             "4":{"id":4,"nome":"Meia","abreviacao":"mei"},
    #             "5":{"id":5,"nome":"Atacante","abreviacao":"ata"},
    #             "6":{"id":6,"nome":"Técnico","abreviacao":"tec"}},
    #         "status":{
    #             "2":{"id":2,"nome":"Dúvida"},
    #             "3":{"id":3,"nome":"Suspenso"},
    #             "5":{"id":5,"nome":"Contundido"},
    #             "6":{"id":6,"nome":"Nulo"},
    #             "7":{"id":7,"nome":"Provável"}}}

    #     expected_output = [
    #         Clube(262, "Flamengo", "FLA"),
    #         Clube(263, "Botafogo", "BOT")
    #     ]
    #     mock_get.return_value = expected_response
    #     expected_url = 'https://api.cartolafc.globo.com/atletas/mercado'

    #     output = self.client.clubes()

    #     mock_get.assert_called_once_with(expected_url)
    #     self.assertEqual(1, mock_get.call_count)
    #     self.assertEqual(output, expected_output)




######### Django

# def create_question(question_text, days):
#     """
#     Create a question with the given `question_text` and published the
#     given number of `days` offset to now (negative for questions published
#     in the past, positive for questions that have yet to be published).
#     """
#     time = timezone.now() + datetime.timedelta(days=days)
#     return Question.objects.create(question_text=question_text, pub_date=time)


# class QuestionIndexViewTests(TestCase):
#     def test_no_questions(self):
#         """
#         If no questions exist, an appropriate message is displayed.
#         """
#         response = self.client.get(reverse('polls:index'))
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "No polls are available.")
#         self.assertQuerysetEqual(response.context['latest_question_list'], [])

#     def test_past_question(self):
#         """
#         Questions with a pub_date in the past are displayed on the
#         index page.
#         """
#         create_question(question_text="Past question.", days=-30)
#         response = self.client.get(reverse('polls:index'))
#         self.assertQuerysetEqual(
#             response.context['latest_question_list'],
#             ['<Question: Past question.>']
#         )
