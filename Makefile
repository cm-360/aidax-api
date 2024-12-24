.PHONY: api docker-build docker-export clean

IMAGE_NAME := aidax
TAG := $(shell date +'%Y-%m-%d')

all: api docker-build

api:
	poetry export -f requirements.txt --output requirements.txt

docker-build:
	docker build -t $(IMAGE_NAME):$(TAG) .
	docker image tag $(IMAGE_NAME):$(TAG) $(IMAGE_NAME):latest

docker-export:
	rm -f $(IMAGE_NAME).tar
	docker image save $(IMAGE_NAME):latest -o $(IMAGE_NAME).tar

clean:
	rm -f api/requirements.txt
	rm -f $(IMAGE_NAME).tar
