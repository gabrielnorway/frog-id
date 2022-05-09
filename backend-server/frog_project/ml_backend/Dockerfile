FROM python:3.6

#COPY ./ml_backend \
#     ./api_backend/app/db_connector.py \
#     ./api_backend/app/secrets.py \
#     ./api_backend/app/settings.py \
#     ./api_backend/app/common.py \
#     ./api_backend/app/classes.py \
#     ./

COPY ./ml_backend .
COPY ./api_backend/app ./app

#WORKDIR ./ml_backend

RUN apt-get update && apt-get install -y --no-install-recommends libgl1 \
    && python3 -m pip install --upgrade pip \
    && pip3 install --no-cache-dir --requirement requirements.txt \
    && cd ./app/ && find . -maxdepth 1 \
    ! -name 'db_connector.py' \
    ! -name 'secrets.py' \
    ! -name 'settings.py' \
    ! -name 'common.py' \
    ! -name 'classes.py' \
    -type f -exec rm {} + && cd ..

ENTRYPOINT [ "python3", "main_ml.py" ]

#CMD [ "" ]