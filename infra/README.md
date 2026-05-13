# Infra

Lokaler Start mit Docker Compose:

```powershell
Copy-Item .env.example .env
docker compose -f infra/docker-compose.yml up --build
```

Services:

- Web: `http://localhost:3000`
- API Health: `http://localhost:8000/api/health`
- Postgres: interner Docker-Service `postgres`

Proxy-Profil mit Caddy:

```powershell
docker compose -f infra/docker-compose.yml --profile proxy up --build
```

Dann routet Caddy ueber `APP_DOMAIN` auf Web und API.
