#!/bin/bash

echo "======================"
echo "Getting version"
echo "======================"

set -e

PYPKG_NAME="bcad"
VSTRING=$(grep version setup.py | sed "s/ *version = \"//" | sed "s/\",//")
echo "VSTRING: ${VSTRING}"
PKG_VERSION=$( git rev-list --all --count )
echo "PKG_VERSION: ${PKG_VERSION}"

APPIMAGE="bcad-${PKG_VERSION}-x86_64.AppImage"

if [ ! -e bcad.AppDir_t ]; then
    mkdir bcad.AppDir_t
fi
if [ -e bcad.AppDir ]; then
    rm -rf bcad.AppDir
fi

ROOTDIR=$(pwd)

APPDIR=${ROOTDIR}/drone/src/bcad.AppDir

BASE_URL=http://archive.main.int

echo "======================"
echo "Obtain appimagetool"
echo "======================"

pushd /tmp
if [ -e appimagetool-x86_64.AppImage ]; then
    rm appimagetool-x86_64.AppImage
fi
#wget https://github.com/probonopd/AppImageKit/releases/download/12/appimagetool-x86_64.AppImage
wget http://archive.main.int/archive/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
popd

MINICONDA_PKG=Miniconda3-py38_4.8.3-Linux-x86_64.sh

${APPDIR}/usr/bin/python3.8 setup.py build -j$(nproc) install --prefix ${APPDIR}/usr

cat >"AppRun" <<\EOF
#!/bin/sh
set -e
APPDIR="$(dirname "$(readlink -e "$0")")"
export LD_LIBRARY_PATH="${APPDIR}/usr/lib/:${APPDIR}/lib/x86_64-linux-gnu:${APPDIR}/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}"
export PATH="${APPDIR}/usr/bin:${PATH}"
exec "${APPDIR}/usr/bin/python3.8" -m bcad.binterpreter.scl "$@"
EOF
chmod +x "AppRun"

echo "======================"
echo "Copy desktop files"
echo "======================"

cp ./AppRun ${APPDIR}
cp ${ROOTDIR}/bcad.desktop ${APPDIR}
cp ${ROOTDIR}/bcad.png ${APPDIR}
cp ${ROOTDIR}/bcad-launcher ${APPDIR}/usr/bin/

/tmp/appimagetool-x86_64.AppImage --appimage-extract
./squashfs-root/AppRun ${APPDIR}
echo "======================"
echo "Cleaning up"
echo "======================"
#rm -rf ${APPDIR}
