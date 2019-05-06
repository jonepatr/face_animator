FROM ubuntu

RUN apt-get update

RUN apt-get -y install blender python3-pip

WORKDIR /app
ADD . /app

RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD ["bash", "start.sh"]