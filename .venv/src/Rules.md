# FieldScreen AI v2 — Règles de Génération de Code

> Ces règles s'appliquent à TOUT le code généré pour ce projet. Elles sont impératives.

---

## R1. Fichiers complets et fonctionnels

- **Pas de `# TODO`**, `pass`, ou `...` sauf pour les stubs explicitement demandés dans le plan de développement
- Chaque fichier doit être syntaxiquement valide et prêt à l'exécution

## R2. Structure du projet

- Respecte **exactement** l'arborescence définie dans la section **Structure du Projet** de `Project_description.md`
- Ne crée pas de fichiers supplémentaires non listés
- Ne supprime pas de fichiers ou dossiers de la structure

## R3. Qualité du code

- **Type hints** Python obligatoires sur toutes les fonctions et méthodes
- **Docstrings** uniquement sur les fonctions publiques (pas de commentaires internes)
- **Pas de commentaires inutiles** — le code doit être auto-documenté
- Noms de variables, fonctions et classes explicites en anglais
- Respecter PEP 8 (conventions Python)

## R4. Dépendances et imports

- **Pas d'erreurs d'import** — tous les modules doivent s'importer correctement
- Utiliser des imports relatifs dans les packages (`from .module import ...`)
- Ne pas ajouter de dépendances non listées dans `requirements.txt`
- Ne pas importer de modules non installés

## R5. Bonnes pratiques API (FastAPI)

- Utiliser `APIRouter(prefix="/api")` pour toutes les routes
- Centraliser les routeurs dans `main.py` via `app.include_router()`
- Modèles Pydantic pour la validation des entrées/sorties
- Utiliser des réponses JSON standardisées
- Healthcheck sur `GET /api/health` retournant `{"status": "ok", "version": "0.1.0"}`

## R6. Frontend (Vanilla JS)

- **Pas de framework** JS lourd (React, Vue, Angular)
- Modules JS avec `type="module"` dans les scripts
- CDN pour les bibliothèques (Leaflet, Supabase JS, Turf.js)
- Organisation : 1 fichier JS par fonctionnalité (auth, map, api, etc.)
- Variables CSS pour le thème (couleurs, polices, espacements)

## R7. Configuration et environnement

- Toutes les clés API et URLs dans `.env` (`.env.example` fourni)
- Utiliser Pydantic Settings (`pydantic-settings`) pour la config backend
- Ne JAMAIS commit de `.env` avec des vraies clés (`.gitignore` doit inclure `.env`)

## R8. Base de données

- Le DDL SQL (`schema.sql`) doit être exécutable directement dans l'éditeur SQL Supabase
- PostGIS doit être activé : `CREATE EXTENSION IF NOT EXISTS postgis;`
- UUID comme clés primaires partout
- Index spatial GIST sur les colonnes de géolocalisation

## R9. Tests

- Tests unitaires pour chaque service (backend)
- Tests API avec `httpx` async et `pytest-asyncio`
- Les tests doivent passer sans nécessiter de connexion réelle à Supabase (mocker si nécessaire)

## R10. Général

- Ne pas générer de documentation ou README sauf si explicitement demandé
- Le projet doit pouvoir se lancer avec une seule commande après `pip install -r requirements.txt`
- Garder le code DRY — pas de duplication inutile
- Sécurité : ne jamais exposer de clés ou secrets dans le code

## R11. Historique des actions

- Après chaque phase ou action significative, ajouter une entrée dans la section **Historique des actions** de `Project_description.md`
- Chaque entrée doit inclure : la date (YYYY-MM-DD), les fichiers créés ou modifiés, les vérifications réussies, et les décisions techniques notables
- Le format est un bloc `### Phase N — Titre · YYYY-MM-DD` suivi d'un tableau de fichiers et d'une liste de points clés
- Ne jamais réécrire les entrées existantes — uniquement ajouter à la suite
