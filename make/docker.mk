#proxy 
# docker makefile
#
 
$(if $(DOCKER_REGISTRY),,$(error DOCKER_REGISTRY is undefined))

registry := $(DOCKER_REGISTRY)
base_image := alpine
base_version := latest

image_tag := $(project)
image := $(image_tag):latest
docker_wheel := $(notdir $(wheel))

proxy_tag := $(project)_proxy
proxy_image := $(proxy_tag):latest

build_opts := \
    --build-arg USER=$(project) \
    --build-arg VERSION=$(version) \
    --build-arg WHEEL=$(docker_wheel)  \
    --build-arg TZ=$(shell cat /etc/timezone) \

docker_deps := $(wildcard docker/*) docker/VERSION docker/$(docker_wheel)
proxy_deps := $(wildcard proxy/*) proxy/VERSION
	
cleanup_files := \
 docker/.build \
 docker/VERSION \
 docker/*.whl \
 docker/*.tar.gz \
 docker/docker-compose.yaml \
 proxy/.build \
 proxy/VERSION \
 docker/build_time \
 $(wildcard *build.log)

docker/$(docker_wheel): $(wheel)
	rm -f docker/*.whl
	cp $< $@

docker/VERSION: VERSION
	cp $< $@

proxy/VERSION: VERSION
	cp $< $@

proxy/.build: $(proxy_deps)
	docker compose --progress plain build $(cache_opts) $(build_opts) $(proxy_tag) 2>&1 | tee proxy_build.log
	@grep -q ^ERROR proxy_build.log && exit 1 || true
	docker tag $(registry)/$(proxy_tag):$(version) $(registry)/$(proxy_tag):latest
	touch $@
	
docker/.build: $(docker_deps) proxy/.build 
	date > docker/build_time
	cp docker-compose.yaml docker
	docker compose --progress plain build $(cache_opts) $(build_opts) $(image_tag) 2>&1 | tee build.log
	@grep -q ^ERROR build.log && exit 1 || true
	docker tag $(registry)/$(image_tag):$(version) $(registry)/$(image_tag):latest
	touch $@

build-proxy: proxy/.build

### build image
build: depends docker/.build


### rebuild image
full-rebuild: clean depends 
	$(MAKE) cache_opts="--no-cache" build

rebuild: 
	rm -f docker/.build
	$(MAKE) build


### docker-clean
docker-clean:
	rm -rf $(cleanup_files)

### docker-sterile
docker-sterile: docker-clean

netboot = netboot.rstms.net
tarball = $(image_tag)_$(version).tgz
proxy_tarball = $(proxy_tag)_$(version).tgz

### upload image to netboot server
netboot-push:
	rm -f *.tgz
	ssh $(netboot) 'mkdir -p ./docker/images && rm -f ./docker/images/*.tgz' 
	ssh $(netboot) find ./docker/
	docker image save $(registry)/$(image_tag):$(version) -o $(tarball)
	docker image save $(registry)/$(proxy_tag):$(version) -o $(proxy_tarball)
	scp *.tgz $(netboot):docker/images/
	ssh $(netboot) 'chmod 0644 ./docker/images/*'
	ssh $(netboot) 'ls -al ./docker/images'
	rm -f *.tgz

### push image to docker registry
dockerhub-push:
	docker push $(registry)/$(image_tag):$(version)
	docker push $(registry)/$(image_tag):latest
	docker push $(registry)/$(proxy_tag):$(version)
	docker push $(registry)/$(proxy_tag):latest

push: release build dockerhub-push
	bin/write-docker-index | ssh $(netboot) 'cat ->./docker/images/$(image_tag).latest && chmod 0644 ./docker/images/*'

docker_opts = 

fqdn := $(shell hostname -f)

certs/$(fqdn).key:
	cd certs; openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
	    -keyout $(fqdn).key -out $(fqdn).fullchain.pem \
	    -subj "/CN=$(fqdn)"

certs/client.key:
	cd certs; mkcert -d 1y client

certs: certs/$(fqdn).key certs/client.key


### run docker image
run: certs
	env BAIKALCTL_VERSION=latest docker compose $(docker_opts) up --force-recreate 

ps:
	docker compose ps 

start: certs
	docker compose $(docker_opts) up --force-recreate -d 

stop:
	docker compose $(docker_opts) down --timeout 3

shell:
	docker compose exec baikalctl /bin/bash

tail:
	while true; do { docker compose logs --follow; sleep 3; }; done

restart:
	$(MAKE) stop
	$(MAKE) start

prune:
	docker system prune --all --force

scan:
	docker run -v /var/run/docker.sock:/var/run/docker.sock -v $$HOME/Library/Caches:/root/.cache/ aquasec/trivy:0.57.0 image baikalctl:latest

dockerclean:
	docker ps -a | awk '/baikalctl/{print $$1}' | xargs -r -n 1 docker rm --force
	docker images | awk '/baikalctl/{print $$3}' | xargs -r -n 1 docker rmi --force
	docker system prune --force
