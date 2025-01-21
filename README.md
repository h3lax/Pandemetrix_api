# starting the python environment


## Dans le repertoire api créer l'environnement python:
```bash
python3 -m venv .venv
```

## Puis l'activer
```bash
. .venv/bin/activate
```

## Mettre Flask à jour / installer

```bash
pip install Flask
```

## Lancer les containers du docker compose

```bash
docker-compose up -d
```

## Run l'app

```bash
flask --app app run --debug
```

## Tester la conection à la DB

http://127.0.0.1:5000/test-db
