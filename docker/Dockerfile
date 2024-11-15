FROM alpine:latest

RUN apk add \
    bash \
    tini \
    tigervnc \
    firefox \
    xfce4 \
    xfce4-terminal \
    pipx 

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

COPY --chmod=0755 client /usr/local/bin/client

USER xbot
WORKDIR /home/xbot
RUN echo "export PATH=$HOME/.local/bin:$PATH" >>.bashrc

RUN export PATH=${HOME}/.local/bin:${PATH}; pipx install baikalctl

COPY --chmod=0444 VERSION VERSION
RUN echo VERSION=$(cat VERSION) 
RUN ./local/bin/baikalctl version
RUN if [ "$(cat VERSION)" != "$(.local/bin/baikalctl version)" ]; then { echo "Version mismatch failure."; exit 1; }; fi

ENV DISPLAY=:1

COPY --chown=xbot:xbot --chmod=0700 run /home/xbot/run

ENTRYPOINT ["/sbin/tini", "--"]

CMD /home/xbot/run
