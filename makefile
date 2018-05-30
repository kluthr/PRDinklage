.PHONY: default install clean
default: build.zip

install:
	pip3 install -q -r requirements.txt

build.zip: clean
	cp -R src build
	pip3 install -q -r requirements.txt -t build
	cd build; zip -r ../build.zip . -x "*__pycache__*"
	rm -r build

clean:
	find . -name '__pycache__' -exec rm -rf {} +
	rm -rf htmlcov/ build/ build.zip
