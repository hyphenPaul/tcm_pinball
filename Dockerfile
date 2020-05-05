FROM ubuntu:16.04

LABEL maintainer="seanpaulfenton@gmail.com"

RUN apt update
RUN apt upgrade -y
RUN apt install -y curl
RUN apt install -y unzip
RUN apt install -y sudo
RUN apt install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt update
RUN apt install -y python3.6

# users

ADD /etc/sudoers.txt /etc/sudoers
RUN chmod 440 /etc/sudoers
RUN useradd mpf -m -g sudo -u 1000
USER mpf
WORKDIR /home/mpf

# install mpf

RUN curl -L https://github.com/missionpinball/mpf-debian-installer/archive/dev.zip --output mpf.zip
RUN unzip mpf.zip
RUN cd mpf-debian-installer-dev && chmod +x install && sudo ./install
RUN cd mpf-debian-installer-dev && chmod +x install-proc && sudo ./install-proc

COPY . /mpf/home
