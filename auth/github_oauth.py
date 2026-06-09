"""
Flujo OAuth 2.0 con PKCE para aplicaciones de escritorio (GitHub).
Requiere internet SOLO durante el inicio de sesión.
"""
import hashlib
import base64
import secrets
import urllib.parse
import webbrowser
import http.server
import threading
from urllib.parse import urlparse, parse_qs

import httpx

# Reemplaza con tu Client ID real de GitHub OAuth App
CLIENT_ID = "TU_CLIENT_ID_AQUI"
REDIRECT_PORT = 8765
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}/callback"


def generate_pkce_pair():
    """Genera code_verifier y code_challenge para PKCE."""
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
        .decode()
        .rstrip("=")
    )
    return code_verifier, code_challenge


def start_flow():
    """Inicia el flujo OAuth y devuelve un objeto Session."""
    code_verifier, code_challenge = generate_pkce_pair()

    auth_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={CLIENT_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&scope=user&state={secrets.token_hex(16)}"
        f"&code_challenge={code_challenge}&code_challenge_method=S256"
    )

    # Abrir navegador
    webbrowser.open(auth_url)

    # Variable para almacenar el código
    auth_code = None
    server_started = threading.Event()
    server = None

    class CallbackHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal auth_code
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            if "code" in params:
                auth_code = params["code"][0]
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Inicio de sesion exitoso. Puedes cerrar esta ventana.")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Error: no se recibio el codigo de autorizacion.")
            # Detener el servidor en un hilo separado
            threading.Thread(target=server.shutdown).start()

    server = http.server.HTTPServer(("localhost", REDIRECT_PORT), CallbackHandler)
    server.timeout = 60  # 1 minuto para recibir callback
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
    server_started.set()

    server_thread.join()

    if auth_code is None:
        raise RuntimeError("No se obtuvo el código de autorización.")

    # Intercambiar código por token
    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": CLIENT_ID,
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier,
    }
    with httpx.Client() as client:
        resp = client.post(token_url, headers=headers, data=data)
        resp.raise_for_status()
        token_data = resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise RuntimeError(f"Error al obtener token: {token_data}")

        # Obtener información del usuario
        user_resp = client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {access_token}"}
        )
        user_resp.raise_for_status()
        username = user_resp.json()["login"]

    from auth.session import Session
    return Session(github_user=username, access_token=access_token)