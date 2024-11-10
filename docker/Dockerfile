FROM debian:bookworm-slim

ARG DEVUAN_VERSION=daedalus
ENV DEVUAN_VERSION=${DEVUAN_VERSION}

RUN apt update && \
    apt upgrade -y && \
    apt install -y curl

COPY --chown=root.root --chmod=0644 apt_sources /etc/apt/sources.list.d/devuan.list
COPY --chown=root.root --chmod=0644 pinned_packages /etc/apt/preferences.d/pinned_packages

RUN sed -i -e "s/DEVUAN_VERSION/${DEVUAN_VERSION}/" /etc/apt/sources.list.d/devuan.list && \
    sed -i -e "s/DEVUAN_VERSION/${DEVUAN_VERSION}/" /etc/apt/preferences.d/pinned_packages 

RUN curl -o /tmp/keyring.deb http://deb.devuan.org/merged/pool/DEVUAN/main/d/devuan-keyring/devuan-keyring_2023.05.28_all.deb && \
    dpkg --install /tmp/keyring.deb && \
    rm /tmp/keyring.deb

RUN apt update
RUN apt install -y -t ${DEVUAN_VERSION} udisks2
RUN apt install -y -t ${DEVUAN_VERSION} libudisks2-0
RUN apt install -y -t ${DEVUAN_VERSION} cgmanager
RUN apt install -y -t ${DEVUAN_VERSION} libcgmanager0
RUN apt install -y -t ${DEVUAN_VERSION} libpolkit-agent-1-0
RUN apt install -y -t ${DEVUAN_VERSION} libpolkit-backend-1-0
RUN apt install -y -t ${DEVUAN_VERSION} libpolkit-gobject-1-0
RUN apt install -y -t ${DEVUAN_VERSION} policykit-1

RUN dieinflames

RUN apt update && \
    apt install -y tigervnc-standalone-server tigervnc-common x11vnc fluxbox pipx tini firefox-esr

RUN apt install -y procps vim net-tools sudo less man-db manpages doas 
#    apt clean && \
#    rm -rf /var/lib/apt/lists/*

RUN adduser xbot && \
    adduser xbot sudo && \
    echo "permit nopass keepenv :sudo" >/etc/doas.conf

RUN mkdir /home/xbot/.vnc

COPY xstartup /home/xbot/.vnc/xstartup

RUN echo vnc | vncpasswd -f >/home/xbot/.vnc/passwd && \
    chmod 700 /home/xbot/.vnc/xstartup && \
    chmod 600 /home/xbot/.vnc/passwd && \
    chown -R xbot:xbot /home/xbot/.vnc

EXPOSE 5901
EXPOSE 8000

USER xbot
WORKDIR /home/xbot

RUN echo "export PATH=$HOME/.local/bin:$PATH" >>.bashrc
COPY VERSION .
RUN pipx install baikalctl

ENV DISPLAY=:1
ENTRYPOINT ["/usr/bin/tini", "--"]
#CMD ["/bin/bash", "-ic", "vncserver :1 -geometry 1280x800 -depth 24 -localhost no && baikalctl server"]
CMD ["/bin/sh", "-c", "sleep inf"]
