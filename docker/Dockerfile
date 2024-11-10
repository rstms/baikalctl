FROM debian:bookworm-slim

RUN apt update

RUN apt update && \
    apt install -y tigervnc-standalone-server tigervnc-common x11vnc fluxbox pipx tini firefox-esr

#RUN apt install -y procps vim net-tools sudo less man-db manpages doas && \
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
CMD ["/bin/bash", "-ic", "vncserver :1 -geometry 1280x800 -depth 24 -localhost no && baikalctl server"]
