FROM alpine:latest

RUN apk upgrade --no-cache

RUN apk add --no-cache \
    tigervnc \
    ratpoison \
    firefox \
    py3-pip \
    nss-tools \
    openssl

RUN apk add --no-cache pipx

ARG USER=bot
ARG UID=1000
ARG GID=1000

RUN \
    adduser ${USER} -D -s /bin/sh && \
    echo "permit nopass keepenv ${USER}" >/etc/doas.conf

RUN mkdir /home/${USER}/.vnc
COPY xstartup /home/${USER}/.vnc/xstartup

RUN \
    dd if=/dev/random count=1 | base64 | head -1 | cut -b-32 | vncpasswd -f >/home/${USER}/.vnc/passwd && \
    chmod 700 /home/${USER}/.vnc/xstartup && \
    chmod 600 /home/${USER}/.vnc/passwd && \
    chown -R ${USER}:${USER} /home/${USER}/.vnc

EXPOSE 8000

USER ${USER}
WORKDIR /home/${USER}
ENV PATH=/home/${USER}/.local/bin:${PATH}

# ensure rebuild when version changes
COPY --chmod=0666 VERSION VERSION

ARG WHEEL
ENV WHEEL=$WHEEL
COPY --chmod=0644 ${WHEEL} .
RUN mkdir -p .cache/baikalctl/profile

RUN \
    pipx install ${WHEEL} && \
    baikalctl --version && \
    rm ${WHEEL}

# ensure VERSION file matches installed app version
RUN [ $(head -1 VERSION) = $(baikalctl version) ]

# ensure VERSION arg match
ARG VERSION
RUN [ ${VERSION} = $(baikalctl version) ]

USER root
COPY --chmod=0755 entrypoint /usr/local/bin/entrypoint
COPY --chmod=0755 show-config /usr/local/bin/show-config
COPY --chmod=0755 docker-compose /usr/local/bin/docker-compose
USER ${USER}
ENV DISPLAY=:1

# first run creates firefox profile
RUN env BAIKALCTL_PASSWORD=. baikalctl --debug --verbose --log-level DEBUG status

COPY --chmod=0644 docker-compose.yaml /home/${USER}/

ENTRYPOINT ["/usr/local/bin/entrypoint"]
CMD ["server"]
