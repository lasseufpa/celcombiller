# Build:
# docker build -t celcombiller-backend .

# Run:
# docker run -d -p 5000:5000  celcombiller-backe

FROM ubuntu:14.04
MAINTAINER jvnsoares@gmail.com

#Install Utilities
RUN apt-get update -q
RUN apt-get install -y python2.7 python-pip gunicorn python-dev sqlite

#Copy files
RUN mkdir /opt/backend
ADD . /opt/backend
WORKDIR /opt/backend

#Install requirements
RUN pip install --allow-external --allow-unverified -r requirements.txt

#Create admin
RUN python adduser.py

EXPOSE 5000:5000

CMD ["gunicorn","-w","4","--bind","0.0.0.0:5000","wsgi:app"]
