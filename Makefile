BUILD_DIR     =     $(shell pwd)
BIN=.venv_lambda/bin/

clean_env:
	rm -r -f $(BUILD_DIR)/.venv_lambda

create_env: clean_env
	python -m venv .venv_lambda 
	$(BIN)pip install --upgrade pip
	$(BIN)pip install -r requirements.txt

clean_deployment:
	rm -f $(BUILD_DIR)/deployment.zip

build_deployment: clean_deployment
	cd .venv_lambda/lib/python3.8/site-packages && \
    zip -r $(BUILD_DIR)/deployment.zip . -x \*/__pycache__/\* -x pip*/\* -x setuptools*/\* \
		-x pkg_resources*/\* -x easy_install.py -x __pycache__/\* -x docs/\* -x tests/\*

initial_load: clean_deployment build_deployment
	cd $(BUILD_DIR)/lambda && zip -ur $(BUILD_DIR)/deployment.zip initial_load.py

incremental_load: clean_deployment build_deployment
	cd $(BUILD_DIR)/lambda && zip -ur $(BUILD_DIR)/deployment.zip incremental_load.py
