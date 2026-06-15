#!/usr/bin/env python3
"""Simple OAuth callback server"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import json
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv()

_client_id = os.environ.get("GOOGLE_OAUTH_CLIENT_ID") or os.environ.get("GA4_OAUTH_CLIENT_ID", "")
_client_secret = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET") or os.environ.get("GA4_OAUTH_CLIENT_SECRET", "")

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)

        if 'code' in query:
            code = query['code'][0]

            # Exchange code for tokens
            from google_auth_oauthlib.flow import Flow

            CLIENT_CONFIG = {
                'installed': {
                    'client_id': _client_id,
                    'client_secret': _client_secret,
                    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                    'token_uri': 'https://oauth2.googleapis.com/token',
                    'redirect_uris': ['http://localhost:8080']
                }
            }

            flow = Flow.from_client_config(
                CLIENT_CONFIG,
                scopes=['https://www.googleapis.com/auth/adwords'],
                redirect_uri='http://localhost:8080'
            )

            try:
                flow.fetch_token(code=code)
                refresh_token = flow.credentials.refresh_token

                # Save to file
                token_data = {
                    "refresh_token": refresh_token,
                    "client_id": CLIENT_CONFIG["installed"]["client_id"],
                    "client_secret": CLIENT_CONFIG["installed"]["client_secret"],
                    "developer_token": os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", ""),
                    "login_customer_id": os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "2538328866")
                }

                with open("google_ads_credentials.json", "w") as f:
                    json.dump(token_data, f, indent=2)

                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()

                html = f"""
                <html>
                <head><title>Sukces!</title></head>
                <body style="font-family: Arial; padding: 50px; text-align: center;">
                <h1 style="color: green;">SUKCES!</h1>
                <p>Refresh token wygenerowany!</p>
                <div style="background: #f0f0f0; padding: 20px; margin: 20px; word-break: break-all;">
                <strong>REFRESH_TOKEN:</strong><br><br>
                <code>{refresh_token}</code>
                </div>
                <p>Token zapisany do: google_ads_credentials.json</p>
                <p>Mozesz zamknac to okno.</p>
                </body>
                </html>
                """
                self.wfile.write(html.encode())

                print()
                print("=" * 70)
                print("SUKCES! REFRESH TOKEN:")
                print("=" * 70)
                print(refresh_token)
                print("=" * 70)
                print()
                print("Zapisano do: google_ads_credentials.json")

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f"<h1>Blad: {e}</h1>".encode())
                print(f"Error: {e}")
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>Brak kodu autoryzacyjnego</h1>")

    def log_message(self, format, *args):
        pass  # Suppress logs

if __name__ == "__main__":
    print("Serwer nasłuchuje na http://localhost:8080")
    print("Czekam na autoryzację...")
    server = HTTPServer(('localhost', 8080), OAuthHandler)
    server.handle_request()  # Handle single request then exit
