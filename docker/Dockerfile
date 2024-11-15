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

EXPOSE 5901
EXPOSE 8000

COPY --chmod=0755 client /usr/local/bin/client
COPY --chmod=0755 server /usr/local/bin/server

USER xbot
WORKDIR /home/xbot
RUN echo "export PATH=/home/xbot/.local/bin:$PATH" >>.bashrc

COPY --chmod=0444 VERSION VERSION

ENV PATH=/home/xbot/.local/bin:${PATH}

ARG WHEEL
ENV WHEEL=$WHEEL
COPY --chmod=0644 $WHEEL .
RUN pipx install -v $WHEEL 

RUN which baikalctl
RUN env BAIKAL_PASSWORD=. baikalctl --version || true

RUN \
    V="$(cat VERSION | head -1)"; \
    B="$({ env BAIKAL_PASSWORD=. baikalctl --version || true; } | awk -F '[v ]*' '{print $2}' | head -1)"; \
    echo "VERSION File: $V"; \
    echo "Installed: $B"; \
    if [ "$V" != "$B" ]; then echo "Version mismatch failure"; exit 1; fi

ENV DISPLAY=:1

ENTRYPOINT ["/sbin/tini", "--"]

CMD /usr/local/bin/server
