#
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
 --build-arg WHEEL=$(docker_wheel) \
 --tag $(image_tag) \
 --progress plain

proxy_build_opts := \
 --tag $(proxy_tag) \
 --progress plain

docker_deps := $(wildcard docker/*) docker/VERSION docker/$(docker_wheel)
proxy_deps := $(wildcard proxy/*) proxy/VERSION
	
cleanup_files := \
 docker/.build docker/VERSION docker/*.whl docker/docker-compose.yaml \
 proxy/.build proxy/VERSION \
 $(wildcard *build.log)

docker/$(docker_wheel): $(wheel)
	cp $< $@

docker/VERSION: VERSION
	cp $< $@

proxy/VERSION: VERSION
	cp $< $@

### build image
build: depends docker/.build proxy/.build

docker/.build: $(docker_deps) 
	cp docker-compose.yaml docker
	docker build $(cache_opts) $(build_opts) docker 2>&1 | tee build.log
	@grep -q ^ERROR build.log && exit 1 || true
	docker tag $(image) $(image_tag):$(version)
	docker tag $(image) rstms/$(image_tag):$(version)
	docker tag $(image) rstms/$(image_tag):latest
	touch $@

proxy/.build: $(proxy_deps)
	docker build $(cache_opts) $(proxy_build_opts) proxy 2>&1 | tee proxy_build.log
	@grep -q ^ERROR proxy_build.log && exit 1 || true
	docker tag $(proxy_image) $(proxy_tag):$(version)
	docker tag $(proxy_image) rstms/$(proxy_tag):$(version)
	docker tag $(proxy_image) rstms/$(proxy_tag):latest
	
proxy: proxy/.build

### rebuild image
rebuild: clean depends 
	$(MAKE) cache_opts="--no-cache build" build

### docker-clean
docker-clean:
	rm -rf $(cleanup_files)

### docker-sterile
docker-sterile: docker-clean

netboot = netboot.rstms.net
tarball = $(image_tag)_$(version).tgz
proxy_tarball = $(proxy_tag)_$(version).tgz

### upload image to netboot server
upload:
	docker image save $(image_tag):$(version) -o $(tarball)
	scp $(tarball) $(netboot):docker/images/$(tarball)
	ssh $(netboot) chmod 0644 docker/images/$(tarball)
	rm $(tarball)

### push image to docker registry
push: rebuild release
	docker tag $(image_tag):$(version) $(registry)/$(image_tag):$(version)
	docker tag $(image_tag):$(version) $(registry)/$(image_tag):latest
	docker push $(registry)/$(image_tag):$(version)
	docker push $(registry)/$(image_tag):latest

docker_opts = 

### run docker image
run:
	docker compose $(docker_opts) up --force-recreate 

ps:
	docker compose ps 

start:
	docker compose $(docker_opts) up --force-recreate -d 

stop:
	docker compose $(docker_opts) down --timeout 3

shell:
	docker compose exec baikalctl /bin/sh

tail:
	while true; do { docker compose logs --follow; sleep 3; }; done

restart:
	$(MAKE) stop
	$(MAKE) start

prune:
	docker system prune --all --force

scan:
	docker run -v /var/run/docker.sock:/var/run/docker.sock -v $$HOME/Library/Caches:/root/.cache/ aquasec/trivy:0.57.0 image baikalctl:latest
