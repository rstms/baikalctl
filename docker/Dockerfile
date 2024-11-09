FROM debian:bookworm-slim

RUN apt update

RUN apt update && \
    apt install -y tigervnc-standalone-server tigervnc-common x11vnc fluxbox

RUN apt install -y procps vim net-tools && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

RUN adduser xbot

RUN mkdir /home/xbot/.vnc

COPY xstartup /home/xbot/.vnc/xstartup


RUN echo "vnc" | vncpasswd -f >/home/xbot/.vnc/passwd && \
    chmod 700 /home/xbot/.vnc/xstartup && \
    chmod 600 /home/xbot/.vnc/passwd && \
    chown -R xbot:xbot /home/xbot/.vnc

EXPOSE 5901


USER xbot
WORKDIR /home/xbot


ENV DISPLAY=:1
CMD ["sh", "-c", "vncserver :1 -geometry 1280x800 -depth 24 && sleep inf"]
