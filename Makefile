BASE_URL?=http://archive.main.int
OCC_NAME=opencascade-7.4.0
OCC_ARC_NAME=$(OCC_NAME).tgz
OCC740_URL=$(BASE_URL)/archive/$(OCC_ARC_NAME)
OCC_BUILD_DIR=occ_build
PYOCC_BUILD_DIR=pyocc_build
PYOCC_GIT=pythonocc-core
PYOCC_GIT_URL=https://github.com/snegovick/pythonocc-core.git
PKG?=deb
DIR_DEB=ext
DIR_APPIMAGE=bcad.AppDir
ifeq ($(PKG),deb)
	BUILD_DIR=$(DIR_DEB)
endif
ifeq ($(PKG),appimage)
	BUILD_DIR=$(DIR_APPIMAGE)
endif


$(BUILD_DIR)/usr:
	@echo "Creating build directories" && mkdir -p $(BUILD_DIR)/usr

$(BUILD_DIR)/$(OCC_NAME): $(BUILD_DIR)/usr
	@echo "Obtaining OpenCASCADE" && curl $(OCC740_URL) -o $(BUILD_DIR)/$(OCC_ARC_NAME) && tar -C $(BUILD_DIR) -xf $(BUILD_DIR)/$(OCC_ARC_NAME)

$(BUILD_DIR)/$(OCC_BUILD_DIR): $(BUILD_DIR)/$(OCC_NAME)
	echo "Building OpenCASCADE" && cdir=$$(pwd) && mkdir $(BUILD_DIR)/$(OCC_BUILD_DIR) && cd $(BUILD_DIR)/$(OCC_BUILD_DIR) && cmake -DINSTALL_DIR=$${cdir}/$(BUILD_DIR)/usr -DUSE_VTK=yes -DUSE_RAPIDJSON=yes -DUSE_FREEIMAGE=yes -DUSE_FFMPEG=yes ../$(OCC_NAME) && make -j $$(nproc) && make install -j $$(nproc)

$(BUILD_DIR)/$(PYOCC_GIT): $(BUILD_DIR)/usr
	echo "Obtaining Python-OCC" && cd $(BUILD_DIR) && git clone ${PYOCC_GIT_URL}

$(BUILD_DIR)/$(PYOCC_BUILD_DIR): $(BUILD_DIR)/$(OCC_BUILD_DIR) $(BUILD_DIR)/$(PYOCC_GIT)
	echo "Building Python-OCC" && cdir=$$(pwd) && mkdir $(BUILD_DIR)/$(PYOCC_BUILD_DIR) && cd $(BUILD_DIR)/$(PYOCC_BUILD_DIR) && PATH=$${cdir}/$(BUILD_DIR)/usr/bin:$${PATH} cmake -DCMAKE_INSTALL_PREFIX=$${cdir}/$(BUILD_DIR)/usr -DPYTHONOCC_INSTALL_DIRECTORY=$${cdir}/$(BUILD_DIR)/usr/lib/python3/site-packages/OCC -DOpenCASCADE_DIR=$${cdir}/$(BUILD_DIR)/usr/lib/cmake/opencascade -DPython3_ROOT_DIR=$${cdir}/$(BUILD_DIR)/usr ../$(PYOCC_GIT) && make -j $$(nproc) && make install -j $$(nproc)

.PHONY: build-deb-package
build-deb-package:
	@echo "Building deb package"; bash ./packaging/build_deb.sh

.PHONY: build-appimage
build-appimage:
	@echo "Building appimage"; bash ./packaging/build_appimage.sh

.PHONY: build-package
build-package: $(BUILD_DIR)/$(PYOCC_BUILD_DIR)
ifeq ($(PKG), deb)
	$(MAKE) PKG=deb build-deb-package
endif
ifeq ($(PKG), appimage)
	$(MAKE) PKG=appimage build-appimage
endif

.PHONY: clean
clean:
	rm -rf $(DIR_DEB)
	rm -rf $(DIR_APPIMAGE)

.PHONY: dist-clean
dist-clean:
	rm -rf $(DIR_DEB)
	rm -rf $(DIR_APPIMAGE)
	git clean -fd
