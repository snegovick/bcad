.PHONY: initenv
initenv:
	-echo "Running initenv"; bash ./build_initenv.sh

.PHONY: build-opencascade
build-opencascade: initenv
	-echo "Building opencascade"; bash ./build_opencascade.sh

.PHONY: build-pyocc
build-pyocc: build-opencascade
	-echo "Building python-occ"; bash ./build_pyocc.sh

.PHONY: build-deb-package
build-deb-package: build-pyocc
	-echo "Building deb package"; bash ./packaging/build_deb.sh

.PHONY: clean
clean:
	rm -rf ext
	git clean -fd
