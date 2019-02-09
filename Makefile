.PHONY: clean virtualenv test docker dist dist-upload lint view-coverage setupaws

clean:
	find . -name '*.py[co]' -delete
	find ./cluster_funk -name __pycache__ |xargs rm -rf

virtualenv:
	virtualenv --prompt '|> cluster_funk <| ' env
	env/bin/pip install -r requirements-dev.txt
	env/bin/python setup.py develop
	@echo
	@echo "VirtualENV Setup Complete. Now run: source env/bin/activate"
	@echo

test:
	python -m pytest \
		-v \
		--cov=cluster_funk \
		--cov-report=term \
		--cov-report=xml \
		--cov-report=html:coverage-report \
		tests/

lint:
	python -m pycodestyle tests
	python -m pycodestyle cluster_funk/core/jobs

docker: clean
	docker build -t cluster_funk:latest .

dist: clean
	rm -rf dist/*
	python -B setup.py sdist
	python -B setup.py bdist_wheel

dist-upload:
	twine upload dist/*

view-coverage:
	open ./coverage-report/index.html
	
setupaws:
	mkdir -p ~/.aws
	touch ~/.aws/credentials
	touch ~/.aws/config
	echo '[default]\naws_secret_access_key = my-40-digit-secret-key\naws_access_key_id = my-20-digit-id' >> ~/.aws/credentials
	echo '[default]\nregion = us-east-1' >> ~/.aws/config
