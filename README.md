# iam-federation-polycorp-partenaire

Architecture de fédération d'identités B2B (IAM) implémentant un SSO inter-entreprises entre **Polycorp** et un **Partenaire**, combinant OpenLDAP, SAML 2.0, OpenID Connect (OIDC) et une application Flask sécurisée par RBAC.

---

## 🚀 Architecture du Projet

Le projet met en œuvre une chaîne complète de fédération d'identités :
1. **OpenLDAP** : Annuaire centralisé de l'entreprise Polycorp (gestion des utilisateurs Alice, Bob et du groupe `partenaire-access`).
2. **Keycloak A (`polycorp`)** : Fournisseur d'identité (IdP) SAML 2.0 adossé à l'annuaire LDAP.
3. **Keycloak B (`partenaire`)** : Courtier d'identité (*Identity Broker*) traduisant le protocole SAML de Polycorp en OIDC/OAuth 2.0.
4. **Application Partenaire (`app.py`)** : Application Flask jouant le rôle de client OIDC et de serveur d'API sécurisé.

---

## 📁 Arborescence du Dépôt

```text
iam-federation-polycorp-partenaire/
├── docker-compose.yml              # Déploiement OpenLDAP + Keycloak A + Keycloak B
├── ldap/
│   └── bootstrap.ldif              # Unités, comptes (Alice, Bob) et groupe partenaire-access
├── keycloak-exports/
│   ├── sp-b-metadata.xml           # Métadonnées SAML du Broker B
│   └── idp-a-metadata.xml          # Métadonnées SAML de l'IdP A
└── app-partenaire/
    ├── Dockerfile                  # Conteneurisation de l'application Flask
    ├── requirements.txt            # Dépendances Python (flask, requests, pyjwt, cryptography)
    └── app.py                      # Client OIDC & API REST (Contrôle d'accès RBAC)

🛠️ Démarrage et DéploiementLancer l'infrastructure (Docker Compose) :Bashdocker-compose up -d
Lancer l'application Flask :Bashcd app-partenaire
pip install -r requirements.txt
python3 app.py
Tester les accès :Accéder à http://app.partenaire.test:5000Se connecter via le compte d'Alice (membre de partenaire-access) $\rightarrow$ Accès autorisé (200 OK).Se connecter via le compte de Bob (sans le groupe requis) $\rightarrow$ Accès refusé (403 Forbidden).🔒 Sécurité & GouvernanceMinimisation des données (RGPD) : Seuls les attributs strictement nécessaires (email, groups) sont transmis dans les assertions SAML et les jetons JWT.Séparation des rôles : Traduction du groupe LDAP partenaire-access en rôle local api_partenaire_user via les mappers Keycloak.
