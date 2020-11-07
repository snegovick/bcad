DIR_APPIMAGE=bcad.AppDir_t
BUILD_DIR=$(DIR_APPIMAGE)

$(BUILD_DIR)/usr:
	@echo "Creating build directories" && mkdir -p $(BUILD_DIR)/usr

.PHONY: build-appimage
build-appimage: $(BUILD_DIR)/usr
	@echo "Building appimage"; bash ./packaging/build_appimage.sh

.PHONY: clean
clean:
	rm -rf $(DIR_APPIMAGE)

.PHONY: dist-clean
dist-clean:
	rm -rf $(DIR_APPIMAGE)
	git clean -fd
