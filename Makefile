APP_NAME=srex

# Use this if using poetry; otherwise switch to pip
RUN=poetry run

.PHONY: all build run test clean shell

all: build

build:
	docker build -t $(APP_NAME) .

run:
	docker run --rm -v ${PWD}/examples:/app/examples -v ${PWD}/output:/app/output $(APP_NAME) generate examples/fallback_test.json output/fallback_output.json --template sli

test:
	pytest tests

shell:
	docker run --rm -it -v ${PWD}:/app $(APP_NAME) bash

clean:
	rm -rf __pycache__ .pytest_cache output/*.json debug/*.txt