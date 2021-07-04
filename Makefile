DIR_APPIMAGE=bcad.AppDir_t
BUILD_DIR=$(DIR_APPIMAGE)

$(BUILD_DIR)/usr:
	@echo "Creating build directories" && mkdir -p $(BUILD_DIR)/usr

.PHONY: prepare:
prepare:
	wget http://archive.main.int/archive/drone/bcad_base_image/ci-names-fix_bcad.AppDir-0.0.0-11-g63fee56.tar.gz -O - | tar xz

.PHONY: build-appimage
build-appimage: prepare
	@echo "Building appimage"; bash ./packaging/build_appimage.sh

.PHONY: clean
clean:
	rm -rf $(DIR_APPIMAGE)

.PHONY: dist-clean
dist-clean:
	rm -rf $(DIR_APPIMAGE)
	git clean -fd
