FROM python:3.7.8

ENV FLASK_APP app
RUN apt-get update && apt install -y python-dev libldap2-dev libsasl2-dev libssl-dev
RUN mkdir /app
WORKDIR /app
ADD . /app/
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["flask", "run", "--host", "0.0.0.0"]
