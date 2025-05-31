# client_manager.py
import http.server
import socketserver
import threading
import webbrowser
import requests
import urllib.parse
import json
import time

from src.utils import check_token, Logger, get_token


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

    def _check_server(self) -> int:
        if not self.server_url:
            return
        try:
            r = requests.get(f"{self.server_url}/ping")
            r.raise_for_status()
            return r.status_code
        except:
            return 404

    def _get_auth_url(self) -> str:
        if not self.server_url:
            raise ValueError("server_url is None")
        r = requests.get(f"{self.server_url}/auth_url")
        r.raise_for_status()
        return r.json()["auth_url"]

    def _get_exchange(self, code: str) -> dict:
        if not self.server_url:
            raise ValueError("server_url is None")
        r = requests.post(f"{self.server_url}/exchange", json={"code": code})
        r.raise_for_status()
        return r.json()

    def _get_refresh_token(self, code: str) -> dict:
        if not self.server_url:
            raise ValueError("server_url is None")
        r = requests.post(f"{self.server_url}/refresh", json={"refresh_token": code})
        r.raise_for_status()
        return r.json()

    def _start_local_server(self) -> None:
        handler = self._make_handler()
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("", self.local_port), handler) as self._httpd:
            self.logger.info(f"Waiting for Google redirect on http://localhost:{self.local_port} ...")
            self._httpd.serve_forever()

    def _make_handler(self):
        receiver = self

        class OAuthHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                query = urllib.parse.urlparse(self.path).query
                params = urllib.parse.parse_qs(query)

                if "code" in params:
                    code = params["code"][0]
                    receiver.logger.info(f"Authorization code received: {code}")

                    try:
                        receiver.token_data = receiver._get_exchange(code)
                        receiver.logger.info("Token successfully received.")
                    except Exception as e:
                        receiver.logger.error(f"Error while exchanging code for token: {e}")
                        receiver.token_data = {"error": str(e)}

                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"Success! You can close the window.")

                    threading.Thread(target=receiver.stop).start()
                else:
                    self.send_error(400, "Missing 'code' parameter in URL")

        return OAuthHandler

    def refresh_token(self) -> bool:
        """
        Refresh the access token using the refresh_token from token.json.
        """
        if not check_token():
            self.logger.info("No token.json file found to refresh token.")
            return False

        token_data = get_token()

        refresh_token = token_data.get("refresh_token")
        if not refresh_token:
            self.logger.info("refresh_token not found in token.json.")
            return False

        try:
            new_tokens = self._get_refresh_token(refresh_token)
            token_data.update(new_tokens)
            token_data["expires_at"] = time.time() + new_tokens.get("expires_in", 3600)

            with open("token.json", "w") as f:
                json.dump(token_data, f)

            self.logger.info("Token successfully refreshed.")
            return True
        except Exception as e:
            self.logger.error(f"Error while refreshing token: {e}")
            return False

    def stop(self) -> None:
        if self._httpd:
            self._httpd.shutdown()

    def run(self, open_browser: bool = True) -> dict:
        thread = threading.Thread(target=self._start_local_server)
        thread.daemon = True
        thread.start()

        try:
            auth_url = self._get_auth_url()
            self.logger.info("Authorization URL successfully received.")
        except requests.exceptions.RequestException as ex:
            self.logger.error(f"Failed to get authorization URL: {ex}")
            return {"error": str(ex)}

        if open_browser:
            self.logger.info("Opening browser...")
            webbrowser.open(auth_url)
        else:
            self.logger.info("Please open the following link in your browser:")
            print(auth_url)

        thread.join()
        return self.token_data or {"error": "Token not received."}
