BUILD_DIR     =     $(shell pwd)

clean_deployment:
	rm -f $(BUILD_DIR)/deployment.zip

build_deployment: clean_deployment
	cd .venv_lambda/lib/python3.8/site-packages && \
    zip -r $(BUILD_DIR)/deployment.zip . -x \*/__pycache__/\* -x pip*/\* -x setuptools*/\* \
		-x pkg_resources*/\* -x easy_install.py -x __pycache__/\*
	cd $(BUILD_DIR)/lambda && zip -ur $(BUILD_DIR)/deployment.zip initial_load.py