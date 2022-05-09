FROM python:3.8

COPY . .

RUN pip3 install --no-cache-dir --requirement requirements.txt

ENTRYPOINT [ "python3", "-m", "gunicorn", "app:create_app()" ]

CMD [ "--preload", "--access-logfile", "'-'", "--error-logfile", "'-'"]

