#!/bin/bash

echo "======================"
echo "Getting version"
echo "======================"

PYPKG_NAME="bcad"
VSTRING=$(grep version setup.py | sed "s/ *version = \"//" | sed "s/\",//")
echo "VSTRING: ${VSTRING}"
PKG_VERSION=$( git rev-list --all --count )
echo "PKG_VERSION: ${PKG_VERSION}"

APPIMAGE="bcad-${PKG_VERSION}-x86_64.AppImage"

pushd bcad.AppDir
APPDIR=$(pwd)

echo "======================"
echo "Copy desktop files"
echo "======================"

cp ../bcad.desktop ./
cp ../bcad.png ./
cp ../bcad-launcher ./usr/bin/

echo "======================"
echo "Obtain appimagetool"
echo "======================"

pushd /tmp
if [ -e appimagetool-x86_64.AppImage ]; then
    rm appimagetool-x86_64.AppImage
fi
wget https://github.com/probonopd/AppImageKit/releases/download/12/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
popd

if [ ! -e Python-3.8.2.tar.xz ]; then
    echo "======================"
    echo "Obtain python"
    echo "======================"

    wget https://www.python.org/ftp/python/3.8.2/Python-3.8.2.tar.xz
    wget https://bootstrap.pypa.io/get-pip.py

    echo "======================"
    echo "Unpack python"
    echo "======================"
    
    tar xf "Python-3.8.2.tar.xz"
    pushd Python-3.8.2
    ./configure --prefix="${APPDIR}/usr" --enable-ipv6 --enable-loadable-sqlite-extensions --enable-shared --with-threads --without-ensurepip --enable-optimizations
    make -j$(nproc)
    make -j$(nproc) install
    popd
fi
    
appdir_python()
{
  env LD_LIBRARY_PATH="${APPDIR}/usr/lib" "${APPDIR}/usr/bin/python3.8" -s "$@"
}
python='appdir_python'

if [ ! -e ply ]; then
    git clone https://github.com/dabeaz/ply.git
    pushd ply
    git checkout e5d40872956764a47dbf9df6a455568f61f92173 -b build
    cp -pr ply ${APPDIR}/usr/lib/python3.8/site-packages
    popd
fi

if [ ! -e setuptools ]; then
    git clone https://github.com/pypa/setuptools.git
    pushd setuptools
    git checkout 3aeec3f0e989516e9229d9a75f5a038929dee6a6 -b build
    ${APPDIR}/usr/bin/python3 bootstrap.py
    ${APPDIR}/usr/bin/python3 setup.py build -j$(nproc) install --prefix ${APPDIR}/usr
    popd
fi

if [ ! -e cython ]; then
    git clone https://github.com/cython/cython.git
    pushd cython
    git checkout 6a30fecff5decdf20029763afea6183de3177dc3 -b build
    ${APPDIR}/usr/bin/python3 setup.py build -j$(nproc) install --prefix ${APPDIR}/usr
    popd
fi

if [ ! -e numpy ]; then
    git clone https://github.com/numpy/numpy.git
    pushd numpy
    git checkout 078ac01a85c4db46e7f148829c2e0d0e0f30c36f -b build
    ${APPDIR}/usr/bin/python3 setup.py build -j$(nproc) install --prefix ${APPDIR}/usr
    popd
fi

if [ ! -e watchdog ]; then
    git clone --recursive git://github.com/gorakhargosh/watchdog.git
    pushd watchdog
    git checkout 1675cb6988bdaab58b45cf3f5ddde0da572472ed -b build
    ${APPDIR}/usr/bin/python3 setup.py build -j$(nproc) install --prefix ${APPDIR}/usr
    popd
fi

if [ ! -e pyinotify ]; then
    git clone https://github.com/seb-m/pyinotify.git
    pushd pyinotify
    git checkout 0f3f8950d12e4a6534320153eed1a90a778da4ae -b build
    ${APPDIR}/usr/bin/python3 setup.py build -j$(nproc) install --prefix ${APPDIR}/usr
    popd
fi

if [ ! -e six ]; then
    git clone https://github.com/benjaminp/six.git
    pushd six
    git checkout 3a3db7510b33eb22c63ad94bc735a9032949249f -b build
    ${APPDIR}/usr/bin/python3 setup.py build -j$(nproc) install --prefix ${APPDIR}/usr
    popd
fi

if [ ! -e ezdxf ]; then
    git clone git@github.com:snegovick/ezdxf.git
    pushd ezdxf
    git checkout 1070c67779f75c707c8817b2cc2eca87154fdab5 -b build
    ${APPDIR}/usr/bin/python3 setup.py build -j$(nproc) install --prefix ${APPDIR}/usr
    popd
fi

if [ ! -e qt-everywhere-src-5.14.1 ]; then
    wget http://archive.main.int/archive/qt-everywhere-src-5.14.1.tar.xz
    tar xf qt-everywhere-src-5.14.1.tar.xz
    pushd qt-everywhere-src-5.14.1
    ./configure --prefix=${APPDIR}/usr
    popd
fi

if [ ! -e PyQt5-5.13.2 ]; then
    wget https://www.riverbankcomputing.com/static/Downloads/PyQt5/5.13.2/PyQt5-5.13.2.tar.gz
    tar xf PyQt5-5.13.2.tar.gz
    pushd PyQt5-5.13.2
    yes | ${APPDIR}/usr/bin/python3 configure.py --destdir ${APPDIR}/usr
    popd
fi

if [ -e ${APPDIR}/usr/lib/python3 ]; then
    echo "Moving ${APPDIR}/usr/lib/python3/ to ${APPDIR}/usr/lib/python3.8/"
    cp -pr ${APPDIR}/usr/lib/python3/* ${APPDIR}/usr/lib/python3.8/
    rm -rf ${APPDIR}/usr/lib/python3
fi

cat >"AppRun" <<\EOF
#!/bin/sh
set -e
APPDIR="$(dirname "$(readlink -e "$0")")"
export LD_LIBRARY_PATH="${APPDIR}/usr/lib/:${APPDIR}/usr/x86_64-linux-gnu${LD_LIBRARY_PATH+:$LD_LIBRARY_PATH}"
export PATH="${APPDIR}/usr/bin:${PATH}"
exec "${APPDIR}/usr/bin/python3.8" -m bcad.binterpreter.scl "$@"
EOF
chmod +x "AppRun"

popd

ARCH=x86_64 /tmp/appimagetool-x86_64.AppImage bcad.AppDir
