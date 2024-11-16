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

build_opts := \
 --build-arg USER=$(project) \
 --build-arg VERSION=$(version) \
 --build-arg WHEEL=$(docker_wheel) \
 --tag $(image_tag) \
 --progress plain

docker_deps := $(wildcard docker/*) docker/VERSION docker/$(docker_wheel)
	
cleanup_files := docker/.build docker/VERSION docker/*.whl

docker/$(docker_wheel): $(wheel)
	cp $< $@

docker/VERSION: VERSION
	cp $< $@

### build image
build: depends docker/.build

docker/.build: $(docker_deps) 
	cp docker-compose.yaml docker
	docker build $(build_opts) docker 2>&1 | tee build.log
	@grep -q ^ERROR build.log && exit 1 || true
	docker tag $(image) $(image_tag):$(version)
	docker tag $(image) rstms/$(image_tag):$(version)
	docker tag $(image) rstms/$(image_tag):latest
	touch $@

### rebuild image
rebuild: clean depends 
	$(MAKE) build_opts="$(build_opts) --no-cache" build

### docker-clean
docker-clean:
	rm -rf $(cleanup_files)

### docker-sterile
docker-sterile: docker-clean


### push image to docker registry
push: rebuild release
	docker tag $(image_tag):$(version) $(registry)/$(image_tag):$(version)
	docker tag $(image_tag):$(version) $(registry)/$(image_tag):latest
	docker push $(registry)/$(image_tag):$(version)
	docker push $(registry)/$(image_tag):latest

docker_opts = 

### run docker image
run:
	docker compose $(docker_opts) up --force-recreate baikalctl

ps:
	docker compose ps 

start:
	docker compose $(docker_opts) up --force-recreate -d baikalctl

stop:
	docker compose $(docker_opts) down --timeout 3 baikalctl

shell:
	docker compose exec baikalctl /bin/sh

tail:
	while true; do { docker compose logs --follow baikalctl; sleep 3; }; done

restart:
	$(MAKE) stop
	$(MAKE) start

prune:
	docker system prune --all --force

scan:
	docker run -v /var/run/docker.sock:/var/run/docker.sock -v $$HOME/Library/Caches:/root/.cache/ aquasec/trivy:0.57.0 image baikalctl:latest
