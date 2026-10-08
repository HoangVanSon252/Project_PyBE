# Database migrations

Run from the `app` directory:

```bash
alembic upgrade head
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```
