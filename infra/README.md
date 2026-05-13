# Infra

## Lokaler Start Mit Docker Compose

Voraussetzungen:

- Docker Desktop muss laufen.
- `.env` muss im Repo-Root existieren.

Einmalig im Repo-Root:

```powershell
Copy-Item .env.example .env
```

Start:

```powershell
docker compose -f infra/docker-compose.yml up --build
```

Services:

- Web: `http://localhost:3000`
- API Health: `http://localhost:8000/api/health`
- Postgres: interner Docker-Service `postgres`

Smoke-Check:

```powershell
Invoke-RestMethod http://localhost:8000/api/health
```

Stop:

```powershell
docker compose -f infra/docker-compose.yml down
```

Stop inklusive lokaler Volumes:

```powershell
docker compose -f infra/docker-compose.yml down --volumes
```

## Proxy-Profil Mit Caddy

```powershell
docker compose -f infra/docker-compose.yml --profile proxy up --build
```

Dann routet Caddy ueber `APP_DOMAIN` auf Web und API.
