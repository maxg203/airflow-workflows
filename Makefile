build:
	docker build --no-cache -t workflows-testing .

test:
	docker run -it workflows-testing bash -c "rm -rf tests/__pycache__ && pytest"

setup: build test

.DEFAULT_GOAL := setup
