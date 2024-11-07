#
# docker makefile
#
 
$(if $(DOCKER_REGISTRY),,$(error DOCKER_REGISTRY is undefined))

registry := $(DOCKER_REGISTRY)
base_image := python
base_version := alpine

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

### run docker image
run:
	docker run -it --rm $(image) run
