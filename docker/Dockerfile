FROM alpine:latest

RUN apk add \
    bash \
    tini \
    tigervnc \
    firefox \
    pipx \
    xfce4 \
    xfce4-terminal

RUN adduser xbot -D -s /bin/bash

RUN echo "permit nopass keepenv xbot" >/etc/doas.conf

RUN mkdir /home/xbot/.vnc
COPY xstartup /home/xbot/.vnc/xstartup
RUN echo vncvnc | vncpasswd -f >/home/xbot/.vnc/passwd && \
    chmod 700 /home/xbot/.vnc/xstartup && \
    chmod 600 /home/xbot/.vnc/passwd && \
    chown -R xbot:xbot /home/xbot/.vnc

#EXPOSE 5901
EXPOSE 8000

USER xbot
WORKDIR /home/xbot
RUN echo "export PATH=$HOME/.local/bin:$PATH" >>.bashrc
COPY VERSION .
RUN pipx install baikalctl

#USER root
#RUN apk add doas less vim
#USER xbot

ENV DISPLAY=:1

COPY --chown=xbot:xbot --chmod=0700 run /home/xbot/run

ENTRYPOINT ["/sbin/tini", "--"]
CMD /home/xbot/run
#CMD ["/bin/bash", "-ic", "vncserver :1 -geometry 1280x800 -depth 24 -localhost no && baikalctl server"]
#CMD ["/bin/sh", "-c", "sleep inf"]
