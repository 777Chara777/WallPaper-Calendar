# client_manager.py
import http.server
import socketserver
import threading
import webbrowser
import requests
import urllib.parse
import json

class OAuthTokenReceiver:
    def __init__(self, server_url: str, local_port: int = 8080):
        self.server_url = server_url
        self.local_port = local_port
        self.redirect_uri = f"http://localhost:{self.local_port}"
        self.token_data = None
        self._httpd = None

    def _get_auth_url(self):
        r = requests.get(f"{self.server_url}/auth_url")
        r.raise_for_status()
        return r.json()['auth_url']
    
    def _get_exchange(self, code:str):
        r = requests.post(f"{self.server_url}/exchange", json={"code": code})
        r.raise_for_status()
        return r.json()
    


    def _start_local_server(self):
        handler = self._make_handler()
        with socketserver.TCPServer(("", self.local_port), handler) as self._httpd:
            print(f"[ClientManager] Ожидаю Google Redirect на http://localhost:{self.local_port} ...")
            self._httpd.serve_forever()

    def _make_handler(self):
        receiver = self

        class OAuthHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                query = urllib.parse.urlparse(self.path).query
                params = urllib.parse.parse_qs(query)

                if 'code' in params:
                    code = params['code'][0]
                    print(f"[ClientManager] Получен код авторизации: {code}")

                    try:
                        # r = requests.post(token_url, data=data)
                        receiver.token_data = receiver._get_exchange(code)
                        print("[ClientManager] Токен получен.")
                    except Exception as e:
                        print("[ClientManager] Ошибка получения токена:", e)
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

    def stop(self):
        if self._httpd:
            self._httpd.shutdown()

    def run(self, open_browser=True) -> dict:
        thread = threading.Thread(target=self._start_local_server)
        thread.daemon = True
        thread.start()

        # Получаем ссылку авторизации
        auth_url = self._get_auth_url()
        print("[ClientManager] URL авторизации получен.")

        if open_browser:
            print("[ClientManager] Открываю браузер...")
            webbrowser.open(auth_url)
        else:
            print("[ClientManager] Перейдите по ссылке:")
            print(auth_url)

        # Ожидаем завершения потока сервера
        thread.join()

        return self.token_data or {}
