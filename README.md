# starting the python environment

## Dans le repertoire api créer l'environnement python:
```bash
python3 -m venv .venv
```

## Install packages
```bash
pip install -r requirements.txt 
```

## Puis l'activer
```bash
. .venv/bin/activate
```

* penser à quitter l'environement une fois terminé qui prend des ressources pour rien *
```bash
deactivate
```

## Lancer les containers du docker compose

```bash
docker-compose up -d
```

## Run l'app

```bash
flask --app app run --debug
```

## Tester

[ app-status ]:(http://127.0.0.1:5000/api/health)

[ db-status ]:(http://127.0.0.1:5000/api/db-check)

## Inspecter la db

```bash
docker exec -it <postgres_container_name> psql -U metabase -d metabase
```

## Commandes Postgres
```sql
\dt
```

## Stop/Reset la db
```bash
docker-compose down -v
```

## Migrations
```bash
flask db init
```
```bash
flask db migrate -m "Initial migration"
```
```bash
flask db upgrade
```

## Accéder à metabase

[metabase]:(http://127.0.0.1:3030/)
