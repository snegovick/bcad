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

if [ ! -e bcad.AppDir ]; then
    mkdir bcad.AppDir
fi
ROOTDIR=$(pwd)
pushd bcad.AppDir
APPDIR=$(pwd)

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
popd

DEBOOTSTRAP=1

if [ ${DEBOOTSTRAP} -eq 1 ]; then
    echo "Running dbst"
    bash packaging/run-dbst.sh bcad.AppDir
    pushd ${APPDIR}
    appdir_python()
    {
        env LD_LIBRARY_PATH="${APPDIR}/usr/lib" "${APPDIR}/usr/bin/python3.8" -s "$@"
    }
    python='appdir_python'

    if [ ! -e ezdxf ]; then
        git clone git@github.com:snegovick/ezdxf.git
        pushd ezdxf
        git checkout 1070c67779f75c707c8817b2cc2eca87154fdab5 -b build
        ${APPDIR}/usr/bin/python3.8 setup.py build -j$(nproc) install --prefix ${APPDIR}/usr
        popd
        mv ${APPDIR}/usr/lib/python3.8/site-packages/ezdxf-0.11b1-py3.8.egg/ezdxf ${APPDIR}/usr/lib/python3.8
        mv ${APPDIR}/usr/lib/python3.8/site-packages/pyparsing-3.0.0a2-py3.8.egg/pyparsing ${APPDIR}/usr/lib/python3.8
    fi
    
    popd

    echo "Copy all modules into python3.8 path"
    rm -rf ${APPDIR}/usr/lib/python3/dist-packages/__pycache__
    mv ${APPDIR}/usr/lib/python3/dist-packages/* ${APPDIR}/usr/lib/python3.8
    mv ${APPDIR}/usr/lib/python3/site-packages/* ${APPDIR}/usr/lib/python3.8

    ${APPDIR}/usr/bin/python3.8 setup.py build -j$(nproc) install --prefix ${APPDIR}/usr
    
    pushd ${APPDIR}

    echo "Clean up image"
    
    rm -f bin
    rm -rf boot
    rm -rf etc
    rm -f dev
    rm -rf ezdxf
    rm -f lib
    rm -f lib32
    rm -f lib64
    rm -rf media
    rm -rf mnt
    rm -rf occ_build
    rm -rf opencascade-7.4.0
    rm -rf opencascade-7.4.0.tgz
    rm -rf opt
    rm -f proc
    rm -rf pyocc_build
    rm -rf pythonocc-core
    rm -rf root
    rm -rf run
    rm -f sbin
    rm -rf srv
    rm -rf sys
    rm -rf tmp
    rm -rf var

    pushd usr/bin
    find . ! -name python3.8 ! -name bcad-launcher -maxdepth 1 -type f -delete
    popd

    pushd usr/lib/x86_64-linux-gnu

    if [ -e ${ROOTDIR}/packaging/keep.list ]; then
        for i in *; do
            if ! grep -qxFe "$i" ${ROOTDIR}/packaging/keep.list; then
                echo "Deleting: $i"
                rm -rf "$i"
            fi
        done
    else
        echo "Error: ${ROOTDIR}/packaging/keep.list is missing"
        exit 1
    fi
    popd

    pushd usr/lib
    if [ -e ${ROOTDIR}/packaging/keep.list ]; then
        for i in *; do
            if ! grep -qxFe "$i" ${ROOTDIR}/packaging/keep.list; then
                echo "Deleting: $i"
                rm -rf "$i"
            fi
        done
    else
        echo "Error: ${ROOTDIR}/packaging/keep.list is missing"
        exit 1
    fi
    popd


    rm -rf usr/games
    rm -rf usr/include
    rm -rf usr/sbin
    rm -rf usr/local
    rm -rf usr/share
    rm -rf usr/src
else
    pushd ${APPDIR}
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
        make -j$(nproc) build_all
        make -j$(nproc) altinstall
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
        ${APPDIR}/usr/bin/python3.8 bootstrap.py
        ${APPDIR}/usr/bin/python3.8 setup.py build -j$(nproc) install --prefix ${APPDIR}/usr
        popd
    fi

    if [ ! -e cython ]; then
        git clone https://github.com/cython/cython.git
        pushd cython
        git checkout 6a30fecff5decdf20029763afea6183de3177dc3 -b build
        ${APPDIR}/usr/bin/python3.8 setup.py build -j$(nproc) install --prefix ${APPDIR}/usr
        popd
    fi

    if [ ! -e numpy ]; then
        git clone https://github.com/numpy/numpy.git
        pushd numpy
        git checkout 078ac01a85c4db46e7f148829c2e0d0e0f30c36f -b build
        ${APPDIR}/usr/bin/python3.8 setup.py build -j$(nproc) install --prefix ${APPDIR}/usr
        popd
    fi

    if [ ! -e watchdog ]; then
        git clone --recursive git://github.com/gorakhargosh/watchdog.git
        pushd watchdog
        git checkout 1675cb6988bdaab58b45cf3f5ddde0da572472ed -b build
        ${APPDIR}/usr/bin/python3.8 setup.py build -j$(nproc) install --prefix ${APPDIR}/usr
        popd
    fi

    if [ ! -e pyinotify ]; then
        git clone https://github.com/seb-m/pyinotify.git
        pushd pyinotify
        git checkout 0f3f8950d12e4a6534320153eed1a90a778da4ae -b build
        ${APPDIR}/usr/bin/python3.8 setup.py build -j$(nproc) install --prefix ${APPDIR}/usr
        popd
    fi

    if [ ! -e six ]; then
        git clone https://github.com/benjaminp/six.git
        pushd six
        git checkout 3a3db7510b33eb22c63ad94bc735a9032949249f -b build
        ${APPDIR}/usr/bin/python3.8 setup.py build -j$(nproc) install --prefix ${APPDIR}/usr
        popd
    fi

    if [ ! -e ezdxf ]; then
        git clone git@github.com:snegovick/ezdxf.git
        pushd ezdxf
        git checkout 1070c67779f75c707c8817b2cc2eca87154fdab5 -b build
        ${APPDIR}/usr/bin/python3.8 setup.py build -j$(nproc) install --prefix ${APPDIR}/usr
        popd
    fi

    set +e
    DL=http://archive.main.int/archive/qt-everywhere-src-5.13.2.tar.xz
    ARC=qt-everywhere-src-5.13.2.tar.xz
    PKG=qt-everywhere-src-5.13.2
    if [ ! -e ${PKG} ]; then
        if [ ! -e ${ARC} ]; then
            wget ${DL}
        fi
        tar xf ${ARC}
        pushd ${PKG}
        echo "Configuring qt"
        ./configure --prefix=${APPDIR}/usr --opensource --confirm-license
        echo "Building qt"
        make -j$(nproc)
        echo "Installing qt"
        make install
        popd
    fi

    DL=https://www.riverbankcomputing.com/static/Downloads/sip/sip-5.3.1.dev2006052202.tar.gz
    ARC=sip-5.3.1.dev2006052202.tar.gz
    PKG=sip-5.3.1.dev2006052202
    set -e
    if [ ! -e ${PKG} ]; then
        wget ${DL}
        tar xf ${ARC}
        pushd ${PKG}
        ${APPDIR}/usr/bin/python3.8 setup.py build -j$(nproc) install --prefix ${APPDIR}/usr
        popd
    fi

    set -e
    if [ ! -e PyQt5-5.13.2 ]; then
        wget https://www.riverbankcomputing.com/static/Downloads/PyQt5/5.13.2/PyQt5-5.13.2.tar.gz
        tar xf PyQt5-5.13.2.tar.gz
        pushd PyQt5-5.13.2
        PATH=${APPDIR}/usr/bin:${PATH} ${APPDIR}/usr/bin/python3.8 configure.py --destdir ${APPDIR}/usr --confirm-license --sysroot ${APPDIR}/usr --no-designer-plugin --no-qml-plugin --no-python-dbus --no-stubs --no-tools
        make -j $(nproc)
        make install
        popd
    fi

    set -e
    if [ -e ${APPDIR}/usr/lib/python3 ]; then
        echo "Moving ${APPDIR}/usr/lib/python3/ to ${APPDIR}/usr/lib/python3.8/"
        cp -pr ${APPDIR}/usr/lib/python3/* ${APPDIR}/usr/lib/python3.8/
        rm -rf ${APPDIR}/usr/lib/python3
    fi
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

echo "======================"
echo "Copy desktop files"
echo "======================"

cp ../bcad.desktop ./
cp ../bcad.png ./
cp ../bcad-launcher ./usr/bin/

popd

ARCH=x86_64 /tmp/appimagetool-x86_64.AppImage bcad.AppDir
