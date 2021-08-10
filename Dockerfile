FROM python:3-alpine

# RUN apk add postgresql-dev gcc python3-dev musl-dev
COPY requirements*.txt ./
RUN apk update && \
 apk add postgresql-libs && \
 apk add --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 python3 -m pip install -r requirements-postgres.txt --no-cache-dir && \
 apk --purge del .build-deps

# RUN addgroup -S lmgroup && adduser -S lmuser -G lmgroup
# USER lmuser

# WORKDIR /usr/src/app
# env PATH=${PATH}:/home/lmuser/.local/bin

# RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --no-cache-dir -r requirements-postgres.txt

COPY . .
COPY lmsite/settings_prod.py ./lmsite/settings.py

EXPOSE 8000/tcp
# ENTRYPOINT [ "python", "manage.py" ]
# CMD [ "runserver" ]
