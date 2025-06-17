# RES-ELEC API

API backend pour la gestion des élections au Gabon.

## Technologies utilisées

- Python 3.8+
- Flask
- SQLAlchemy
- JWT pour l''authentification
- PostgreSQL (production) / SQLite (développement)

## Installation

1. Cloner le repository
2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer les variables d''environnement dans un fichier .env :
```
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=postgresql://user:password@localhost/res_elec
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

5. Initialiser la base de données :
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Lancer l''application :
```bash
python run.py
```

## Structure de l''API

### Authentification

- POST /api/auth/register : Inscription d''un directeur de campagne
- POST /api/auth/login : Connexion
- POST /api/auth/refresh : Rafraîchissement du token
- POST /api/auth/forgot-password : Réinitialisation du mot de passe
- GET /api/auth/profile : Obtenir le profil
- PUT /api/auth/profile : Mettre à jour le profil

### Élections

- POST /api/elections : Créer une élection
- GET /api/elections : Liste des élections
- GET /api/elections/<id> : Détails d''une élection
- PUT /api/elections/<id> : Modifier une élection
- DELETE /api/elections/<id> : Supprimer une élection
- GET /api/elections/<id>/results : Résultats d''une élection

### Candidats

- POST /api/candidates : Ajouter un candidat
- GET /api/candidates : Liste des candidats
- GET /api/candidates/<id> : Détails d''un candidat
- PUT /api/candidates/<id> : Modifier un candidat
- DELETE /api/candidates/<id> : Supprimer un candidat

### Centres et Bureaux de vote

- POST /api/elections/<id>/centers : Ajouter un centre de vote
- POST /api/centers/<id>/offices : Ajouter un bureau de vote
- POST /api/offices/<id>/results : Soumettre les résultats
- GET /api/offices/<id>/results : Obtenir les résultats d''un bureau
- PUT /api/offices/<id>/results : Mettre à jour les résultats

### Résultats en temps réel

- GET /api/voting/realtime/<election_id> : Obtenir les résultats en temps réel

## Sécurité

- Authentification JWT
- Protection CSRF
- Validation des données
- Gestion sécurisée des fichiers
- Hachage des mots de passe
- Rate limiting
- CORS configuré

## Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amazing-feature`)
3. Commit les changements (`git commit -m ''Add amazing feature''`)
4. Push la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## License

MIT
