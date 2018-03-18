import base64
import time

from zeep import Client

MAX_QUERIES_IN_SINGLE_SESSION = 2500
TIME_BETWEEN_QUERIES_SEC = 0.5


class WoSClient:
    def __init__(self, user, password):
        self._user_password_base64 = base64.b64encode(str.encode(user + ":" + password)).decode("ascii")
        self._SID = ""
        self._search_queries_count = 0
        self._next_query_time = time.time()
        self._init_clients()
        self._init_types()

    def _init_types(self):
        self._query_params_type = self._search_client.get_type('ns0:queryParameters')
        self._retrive_params_type = self._search_client.get_type('ns0:retrieveParameters')

    def _init_clients(self):
        self._auth_client = Client("http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl")
        self._search_client = Client("http://search.webofknowledge.com/esti/wokmws/ws/WokSearchLite?wsdl")

    def __enter__(self):
        self.authenticate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_session()

    def authenticate(self):
        self._auth_client.transport.session.headers.update({"Authorization": "Basic " + self._user_password_base64})
        self._SID = self._auth_client.service.authenticate()
        self._search_client.transport.session.headers.update({"Cookie": 'SID ="' + self._SID + '"'})

    def close_session(self):
        self._auth_client.service.closeSession()
        self._SID = ""
        self._search_queries_count = 0

    def reauthenticate(self):
        self.close_session()
        self.authenticate()

    def search(self, user_query, raw_response=False):
        if not self._SID:
            raise ValueError("There is no session ID. Authenticate first.")

        if self._search_queries_count >= MAX_QUERIES_IN_SINGLE_SESSION:
            self.reauthenticate()

        query_params, retrive_params = self._prepare_parameters(user_query)
        search_results = self._send_search_query(query_params, raw_response, retrive_params)

        return search_results

    def _send_search_query(self, query_params, raw_response, retrive_params):
        self._sleep_to_next_query_time()
        with self._search_client.options(raw_response=raw_response):
            search_results = self._search_client.service.search(queryParameters=query_params,
                                                                retrieveParameters=retrive_params)
        self._next_query_time = time.time() + TIME_BETWEEN_QUERIES_SEC
        self._search_queries_count += 1
        return search_results

    def _sleep_to_next_query_time(self):
        to_sleep = self._next_query_time - time.time()
        if to_sleep > 0:
            time.sleep(to_sleep)

    def _prepare_parameters(self, user_query):
        query_params = self._query_params_type(databaseId='WOS', userQuery=user_query, queryLanguage='en')
        retrive_params = self._retrive_params_type(firstRecord=1, count=100)
        return query_params, retrive_params
