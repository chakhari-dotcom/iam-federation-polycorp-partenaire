from flask import Flask, redirect, request, session, jsonify
import requests
import jwt

app = Flask(__name__)
app.secret_key = "secret-demo-partenaire"

KEYCLOAK_B_URL = "http://broker.partenaire.test:8082/realms/partenaire"
CLIENT_ID = "app-partenaire"
CLIENT_SECRET = "VOTRE_CLIENT_SECRET_ICI" # À remplacer !
REDIRECT_URI = "http://app.partenaire.test:5000/callback"

@app.route("/")
def index():
    auth_url = (
        f"{KEYCLOAK_B_URL}/protocol/openid-connect/auth"
        f"?client_id={CLIENT_ID}&response_type=code&scope=openid%20partenaire:api"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return f'<h2>Portail Partenaire (Entreprise B)</h2><a href="{auth_url}">Se connecter via OIDC</a>'

@app.route("/callback")
def callback():
    code = request.args.get("code")
    token_url = f"{KEYCLOAK_B_URL}/protocol/openid-connect/token"
    resp = requests.post(token_url, data={
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }).json()

    access_token = resp.get("access_token")
    id_token = resp.get("id_token")

    # Appel automatique à l'API avec le Bearer token
    api_resp = requests.get(
        "http://app.partenaire.test:5000/api/ressource",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    return jsonify({
        "1_code_oidc_recu": code,
        "2_id_token_decode": jwt.decode(id_token, options={"verify_signature": False}),
        "3_access_token_decode": jwt.decode(access_token, options={"verify_signature": False}),
        "4_reponse_api_partenaire": {
            "status_code": api_resp.status_code,
            "body": api_resp.json()
        }
    })

@app.route("/api/ressource")
def api_ressource():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Token manquant"}), 401

    token = auth_header.split(" ")[1]
    payload = jwt.decode(token, options={"verify_signature": False})

    roles = payload.get("realm_access", {}).get("roles", [])
    scopes = payload.get("scope", "").split(" ")

    # Vérification du scope ET du rôle traduit depuis SAML
    if "partenaire:api" not in scopes or "api_partenaire_user" not in roles:
        return jsonify({
            "error": "Accès interdit (403 Forbidden) : Rôle 'api_partenaire_user' manquant",
            "utilisateur": payload.get("preferred_username"),
            "roles_actuels": roles
        }), 403

    return jsonify({
        "message": "Accès autorisé à l'API du Partenaire !",
        "utilisateur": payload.get("preferred_username"),
        "roles": roles,
        "scopes": scopes
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
