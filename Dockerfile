FROM node:22-bookworm-slim AS frontend
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/index.html frontend/tsconfig.json frontend/vite.config.ts frontend/.env.django ./
COPY frontend/src ./src
COPY frontend/public ./public
RUN npm run build:server

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DJANGO_SERVE_FRONTEND=true
WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt && useradd --uid 10001 --create-home app
COPY backend /app/backend
COPY --from=frontend /app/dist /app/frontend/dist
RUN DJANGO_DEBUG=true python backend/manage.py collectstatic --noinput && mkdir -p /app/backend/data && chown -R app:app /app
USER app
WORKDIR /app/backend
EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 1 --threads 2 --timeout 60 --access-logfile -"]
