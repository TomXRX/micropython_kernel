FROM micropython/unix:latest

USER root

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 git -y
RUN apt-get install python3 python3-pip -y

RUN mkdir /app
ADD requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip3 install --upgrade pip \
  && pip3 install -r requirements.txt

CMD jupyter lab  --NotebookApp.token=abcd --allow-root --ip="0.0.0.0"

RUN pip3 install notebook

RUN echo "jovyan ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
#abc ALL=(ALL:ALL) ALL


EXPOSE 8888

USER ${NB_UID}

WORKDIR "/home/jovyan"
