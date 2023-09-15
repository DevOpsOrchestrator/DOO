# base image  
FROM python:3.10

RUN apt-get update && \
    apt-get install -y sshpass vim bash tcpdump iperf busybox \
    net-tools iproute2 ethtool iputils-ping

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# setup environment variable  
ENV DockerHOME=/home/app/doo
ENV Repository=/home/app/repository

# set work directory  
RUN mkdir -p $DockerHOME  
RUN mkdir -p $Repository

# install dependencies  
RUN pip install --upgrade pip 

# copy whole project to your docker home directory. 
COPY . $DockerHOME

COPY docker/docker-entrypoint.sh $DockerHOME

# where your code lives  
WORKDIR $DockerHOME 

RUN chmod 777 docker-entrypoint.sh

# run this command to install all dependencies  
RUN pip install -r requirements.txt  
# port where the Django app runs  
EXPOSE 8000 

# start server  
CMD [ "/home/app/doo/docker-entrypoint.sh"]