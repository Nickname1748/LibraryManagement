FROM python:3-alpine

COPY requirements*.txt ./
RUN apk update && \
 apk add postgresql-libs && \
 apk add --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 python3 -m pip install -r requirements-postgres.txt --no-cache-dir && \
 apk --purge del .build-deps

COPY . .
COPY lmsite/settings_prod.py ./lmsite/settings.py

EXPOSE 8000/tcp
CMD [ "python", "manage.py", "runserver" ]
