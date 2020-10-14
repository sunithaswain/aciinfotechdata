FROM python:3.6-stretch
RUN apt-get update --fix-missing && apt-get install -y wget bzip2 ca-certificates \
libglib2.0-0 libxext6 libsm6 libxrender1
RUN pip3 install uwsgi
##################################################################################
# Set the working directory to /app
##################################################################################
ADD . /b2b-claim-portal-api
WORKDIR /b2b-claim-portal-api
##################################################################################
# Install dependencies
# Couchbase dependencies
##################################################################################
RUN apt-cache policy lsb-release
RUN apt-get -y install lsb-release
RUN wget http://packages.couchbase.com/releases/couchbase-release/couchbase-release-1.0-6-amd64.deb && \
dpkg -i couchbase-release-1.0-6-amd64.deb && \
apt-get update && \
apt-get install libcouchbase-dev libcouchbase2-bin build-essential -y
##################################################################################
# Couchbase
##################################################################################
#RUN apt-get install build-essential 
RUN pip3 install couchbase
##################################################################################
# Python dependencies
##################################################################################
RUN pip3 install -r  requirements.txt
RUN pip3 install -e .
EXPOSE 5010
CMD ["uwsgi", "--ini", "/b2b-claim-portal-api/uwsgi.ini"]
#CMD ["ddtrace-run", "python","app/index.py"]
#CMD ["python","app/index.py"]
