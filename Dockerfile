FROM ubuntu:16.04

LABEL maintainer="seanpaulfenton@gmail.com"

RUN apt update && \
apt upgrade -y && \
apt install -y curl unzip sudo software-properties-common python3.5 usbutils && \
apt clean

# users
RUN echo "mpf ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN useradd mpf -m -G sudo -u 1000
USER mpf
WORKDIR /home/mpf

# install mpf

RUN bash -c "curl -L https://github.com/missionpinball/mpf-debian-installer/archive/dev.zip --output mpf.zip && \
unzip mpf.zip && \
cd mpf-debian-installer-dev && \
chmod +x install && sudo ./install && \
chmod +x install-proc && ./install-proc"

COPY . /home/mpf
