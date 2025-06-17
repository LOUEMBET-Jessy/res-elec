# RES-ELEC API

API backend pour la gestion des �lections au Gabon.

## Technologies utilis�es

- Python 3.8+
- Flask
- SQLAlchemy
- JWT pour l''authentification
- PostgreSQL (production) / SQLite (d�veloppement)

## Installation

1. Cloner le repository
2. Cr�er un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Installer les d�pendances :
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

5. Initialiser la base de donn�es :
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
- POST /api/auth/refresh : Rafra�chissement du token
- POST /api/auth/forgot-password : R�initialisation du mot de passe
- GET /api/auth/profile : Obtenir le profil
- PUT /api/auth/profile : Mettre � jour le profil

### �lections

- POST /api/elections : Cr�er une �lection
- GET /api/elections : Liste des �lections
- GET /api/elections/<id> : D�tails d''une �lection
- PUT /api/elections/<id> : Modifier une �lection
- DELETE /api/elections/<id> : Supprimer une �lection
- GET /api/elections/<id>/results : R�sultats d''une �lection

### Candidats

- POST /api/candidates : Ajouter un candidat
- GET /api/candidates : Liste des candidats
- GET /api/candidates/<id> : D�tails d''un candidat
- PUT /api/candidates/<id> : Modifier un candidat
- DELETE /api/candidates/<id> : Supprimer un candidat

### Centres et Bureaux de vote

- POST /api/elections/<id>/centers : Ajouter un centre de vote
- POST /api/centers/<id>/offices : Ajouter un bureau de vote
- POST /api/offices/<id>/results : Soumettre les r�sultats
- GET /api/offices/<id>/results : Obtenir les r�sultats d''un bureau
- PUT /api/offices/<id>/results : Mettre � jour les r�sultats

### R�sultats en temps r�el

- GET /api/voting/realtime/<election_id> : Obtenir les r�sultats en temps r�el

## S�curit�

- Authentification JWT
- Protection CSRF
- Validation des donn�es
- Gestion s�curis�e des fichiers
- Hachage des mots de passe
- Rate limiting
- CORS configur�

## Contribution

1. Fork le projet
2. Cr�er une branche (`git checkout -b feature/amazing-feature`)
3. Commit les changements (`git commit -m ''Add amazing feature''`)
4. Push la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## License

MIT
