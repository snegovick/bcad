BASE_URL?=http://archive.main.int
OCC_NAME=opencascade-7.4.0
OCC_ARC_NAME=$(OCC_NAME).tgz
OCC740_URL=$(BASE_URL)/archive/$(OCC_ARC_NAME)
OCC_BUILD_DIR=occ_build
PYOCC_BUILD_DIR=pyocc_build
PYOCC_GIT=pythonocc-core
PYOCC_GIT_URL=https://github.com/snegovick/pythonocc-core.git

ext/usr:
	@echo "Creating build directories" && mkdir -p ext/usr

ext/$(OCC_NAME): ext/usr
	@echo "Obtaining OpenCASCADE" && curl $(OCC740_URL) -o ext/$(OCC_ARC_NAME) && tar -C ext -xf ext/$(OCC_ARC_NAME)

ext/$(OCC_BUILD_DIR): ext/$(OCC_NAME)
	echo "Building OpenCASCADE" && cdir=$$(pwd) && mkdir ext/$(OCC_BUILD_DIR) && cd ext/$(OCC_BUILD_DIR) && cmake -DINSTALL_DIR=$${cdir}/ext/usr -DUSE_VTK=yes -DUSE_RAPIDJSON=yes -DUSE_FREEIMAGE=yes -DUSE_FFMPEG=yes ../$(OCC_NAME) && make -j $$(nproc) && make install -j $$(nproc)

ext/$(PYOCC_GIT): ext/usr
	echo "Obtaining Python-OCC" && cd ext && git clone ${PYOCC_GIT_URL}

ext/$(PYOCC_BUILD_DIR): ext/$(OCC_BUILD_DIR) ext/$(PYOCC_GIT)
	echo "Building Python-OCC" && cdir=$$(pwd) && mkdir ext/$(PYOCC_BUILD_DIR) && cd ext/$(PYOCC_BUILD_DIR) && PATH=$${cdir}/ext/usr/bin:$${PATH} cmake -DCMAKE_INSTALL_PREFIX=$${cdir}/ext/usr -DPYTHONOCC_INSTALL_DIRECTORY=$${cdir}/ext/usr/lib/python3/site-packages/OCC -DOpenCASCADE_DIR=$${cdir}/ext/usr/lib/cmake/opencascade -DPython3_ROOT_DIR=$${cdir}/ext/usr ../$(PYOCC_GIT) && make -j $$(nproc) && make install -j $$(nproc)

.PHONY: build-deb-package
build-deb-package: ext/$(PYOCC_BUILD_DIR)
	@echo "Building deb package"; bash ./packaging/build_deb.sh

.PHONY: clean
clean:
	rm -rf ext
	git clean -fd
