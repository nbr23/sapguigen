FROM python:3.6

EXPOSE 8000

COPY . /var/www/sapguigen
WORKDIR /var/www/sapguigen

RUN pip install -r /var/www/sapguigen/requirements.txt

CMD uwsgi --ini sapguigen.ini
