# client_manager.py
import http.server
import socketserver
import threading
import webbrowser
import requests
import urllib.parse
import json
import time

from src.utils import check_token, Logger

class OAuthTokenReceiver:
    def __init__(self, server_url: str | None, local_port: int = 8080):
        self.logger = Logger("OAuthTokenReceiver")
        self.server_url = server_url
        self.local_port = local_port
        self.redirect_uri = f"http://localhost:{self.local_port}"
        self.token_data = None
        self._httpd = None

    def set_server_url(self, server_url: str) -> None:
        self.server_url = server_url

    def _get_auth_url(self):
        if self.server_url is None:
            raise ValueError("server_url is None")
        r = requests.get(f"{self.server_url}/auth_url")
        r.raise_for_status()
        return r.json()['auth_url']
    
    def _get_exchange(self, code:str):
        if self.server_url is None:
            raise ValueError("server_url is None")
        r = requests.post(f"{self.server_url}/exchange", json={"code": code})
        r.raise_for_status()
        return r.json()
    
    def _get_refresh_token(self, code:str):
        if self.server_url is None:
            raise ValueError("server_url is None")
        r = requests.post(f"{self.server_url}/refresh", json={"refresh_token": code})
        r.raise_for_status()
        return r.json()
    


    def _start_local_server(self):
        handler = self._make_handler()
        with socketserver.TCPServer(("", self.local_port), handler) as self._httpd:
            self.logger.info(f"Ожидаю Google Redirect на http://localhost:{self.local_port} ...")
            self._httpd.serve_forever()

    def _make_handler(self):
        receiver = self

        class OAuthHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                query = urllib.parse.urlparse(self.path).query
                params = urllib.parse.parse_qs(query)

                if 'code' in params:
                    code = params['code'][0]
                    receiver.logger.info(f"Получен код авторизации: {code}")

                    try:
                        # r = requests.post(token_url, data=data)
                        receiver.token_data = receiver._get_exchange(code)
                        receiver.logger.info("Токен получен.")
                    except Exception as e:
                        receiver.logger.info("Ошибка получения токена:", e)
                        receiver.token_data = {'error': str(e)}

                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b"Success! You can close the window.")

                    # Остановка сервера после получения токена
                    threading.Thread(target=receiver.stop).start()
                else:
                    self.send_error(400, "Нет параметра 'code' в URL")

        return OAuthHandler

    def refresh_token(self):
        """
        Обновляет токен используя refresh_token из token.json и обновляет файл.
        """
        if not check_token():
            self.logger.info("Нет файла token.json для обновления токена")
            return False

        with open("token.json", "r") as f:
            token_data = json.load(f)

        refresh_token = token_data.get("refresh_token")
        if not refresh_token:
            self.logger.info("В token.json нет refresh_token")
            return False

        

        try:
            
            new_tokens = self._get_refresh_token(refresh_token)
            # Обновляем access_token и expires_at
            token_data.update(new_tokens)
            token_data['expires_at'] = time.time() + new_tokens.get('expires_in', 3600)

            with open("token.json", "w") as f:
                json.dump(token_data, f)
            self.logger.info("Токен успешно обновлён.")
            return True
        except Exception as e:
            self.logger.info(f"Ошибка обновления токена: {e}")
            return False
        

    def stop(self):
        if self._httpd:
            self._httpd.shutdown()

    def run(self, open_browser=True) -> dict:
        thread = threading.Thread(target=self._start_local_server)
        thread.daemon = True
        thread.start()

        # Получаем ссылку авторизации
        auth_url = self._get_auth_url()
        self.logger.info("URL авторизации получен.")

        if open_browser:
            self.logger.info("Открываю браузер...")
            webbrowser.open(auth_url)
        else:
            self.logger.info("Перейдите по ссылке:")
            print(auth_url)

        # Ожидаем завершения потока сервера
        thread.join()

        return self.token_data or {}
