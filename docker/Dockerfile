FROM debian:bookworm-slim

RUN apt update

RUN apt update && \
    apt install -y tigervnc-standalone-server tigervnc-common x11vnc fluxbox && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

RUN adduser xbot

USER xbot
WORKDIR /home/xbot

ENV DISPLAY=:1

RUN mkdir .vnc && \
    echo "howdy" | vncpasswd -f >.vnc/passwd && \
    chmod 600 .vnc/passwd

COPY xstartup .vnc/xstartup

EXPOSE 5901

CMD ["sh", "-c", "vncserver :1 -geometry 1280x800 -depth 24 && /bin/bash"]
