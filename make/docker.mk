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
 --build-arg BASE_IMAGE=$(base_image):$(base_version) \
 --build-arg VERSION=$(version) \
 --build-arg WHEEL=$(docker_wheel) \
 --build-arg SERVICE_EXEC=$(cli) \
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
	docker build $(build_opts) docker | tee build.log
	docker tag $(image) $(image_tag):$(version)
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
push: build release
	docker push $(image_tag):$(version)
	docker push $(image)

docker_opts = -p 5999:5901 -p 8000:8000 -v $(HOME)/.baikalctl:/home/xbot/.baikalctl

### run docker image
run:
	docker run -it --rm $(docker_opts) $(image)

ps:
	docker ps

start:
	docker run $(docker_opts) -d $(image)

stop:
	id=$(shell docker ps | awk '/$(image)/{print $$1}'); docker stop $$id && docker rm $$id

shell:
	docker exec -it $(shell docker ps | awk '/$(image)/{print $$1}') /bin/bash
