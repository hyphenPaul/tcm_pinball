FROM ubuntu:14.04

LABEL maintainer="seanpaulfenton@gmail.com"

RUN apt update
RUN apt upgrade -y
RUN apt install -y curl
RUN apt install -y unzip
RUN apt install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt update
RUN apt install -y python3.6
#RUN echo 'alias python=python3' >> ~/.bashrc
#RUN echo "()" && \
#python --version && \
#echo "()"
RUN curl -L https://github.com/missionpinball/mpf-debian-installer/archive/dev.zip --output mpf.zip
RUN unzip mpf.zip && \
cd mpf-debian-installer-dev && \
ls -l && \
chmod +x install && \
./install && \
chmod +x install-proc && \
./install-proc

COPY . /src

WORKDIR /src
