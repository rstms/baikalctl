FROM alpine:latest

RUN apk add \
    bash \
    tini \
    tigervnc \
    firefox \
    xfce4 \
    xfce4-terminal \
    py3-pip \
    pipx 

ARG USER=bot
ARG UID=1000
ARG GID=1000

RUN \
    adduser ${USER} -D -s /bin/bash && \
    echo "permit nopass keepenv ${USER}" >/etc/doas.conf

RUN mkdir /home/${USER}/.vnc
COPY xstartup /home/${USER}/.vnc/xstartup

RUN \
    echo vncvnc | vncpasswd -f >/home/${USER}/.vnc/passwd && \
    chmod 700 /home/${USER}/.vnc/xstartup && \
    chmod 600 /home/${USER}/.vnc/passwd && \
    chown -R ${USER}:${USER} /home/${USER}/.vnc

#EXPOSE 5901
EXPOSE 8000

COPY --chmod=0755 entrypoint /usr/local/bin/entrypoint

USER ${USER}
WORKDIR /home/${USER}
RUN echo "export PATH=/home/${USER}/.local/bin:$PATH" >>.bashrc
ENV PATH=/home/${USER}/.local/bin:${PATH}

# ensure rebuild when version changes
COPY --chmod=0666 VERSION VERSION

ARG WHEEL
ENV WHEEL=$WHEEL
COPY --chmod=0644 ${WHEEL} .

RUN pipx install ${WHEEL} && rm ${WHEEL}
#RUN pip install --user --break-system-packages $WHEEL

RUN baikalctl --version

# ensure VERSION file matches installed app version
RUN [ $(head -1 VERSION) = $(baikalctl version) ]

# ensure VERSION arg match
ARG VERSION
RUN [ ${VERSION} = $(baikalctl version) ]

#ENTRYPOINT ["/sbin/tini", "--"]
ENTRYPOINT ["/bin/sh", "-c", "/usr/local/bin/entrypoint"]
CMD "server"
