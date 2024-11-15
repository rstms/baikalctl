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
COPY --chmod=0755 run /usr/local/bin/run

USER xbot
WORKDIR /home/xbot
RUN echo "export PATH=$HOME/.local/bin:$PATH" >>.bashrc

COPY --chmod=0444 VERSION VERSION
RUN export PATH=${HOME}/.local/bin:${PATH}; pipx install baikalctl

RUN echo VERSION=$(cat VERSION) 
RUN echo baikalctl=$(env BAIKAL_PASSWORD=. run version)
RUN if [ "$(cat VERSION)" != "$(env BAIKAL_PASSWORD=. run version)" ]; then { echo "Version mismatch failure."; exit 1; }; fi

ENV DISPLAY=:1


ENTRYPOINT ["/sbin/tini", "--"]

CMD /usr/local/bin/run
