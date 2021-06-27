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
APPDIR=${ROOTDIR}/bcad.AppDir
pushd bcad.AppDir_t
APPDIR_T=$(pwd)

BASE_URL=http://archive.main.int

OCC_NAME=opencascade-7.4.0
OCC_ARC_NAME=${OCC_NAME}.tgz
OCC740_URL=${BASE_URL}/archive/${OCC_ARC_NAME}
OCC_BUILD_DIR=occ_build

PYOCC_BUILD_DIR=pyocc_build
PYOCC_GIT=pythonocc-core
PYOCC_GIT_URL=https://github.com/snegovick/pythonocc-core.git

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
popd

DEBOOTSTRAP=0
MINICONDA=1

MINICONDA_PKG=Miniconda3-py38_4.8.3-Linux-x86_64.sh

if [ ${MINICONDA} -eq 1 ]; then
    echo "Checking miniconda"
    pushd ${APPDIR_T}
    if [ ! -e usr/bin ]; then
        echo "Installing miniconda"
        PKG=${MINICONDA_PKG}
        if [ ! -e ${PKG} ]; then
            wget http://archive.main.int/archive/${PKG}
            bash ${PKG} -b -p usr -f
        fi
        # appdir_python()
        # {
        #     env LD_LIBRARY_PATH="${APPDIR}/usr/lib" "${APPDIR}/usr/bin/python3.8" -s "$@"
        # }
        # python='appdir_python'
        echo "Activating envinronment"
        source usr/bin/activate
        echo "Installing deps"
        usr/bin/pip install --force-reinstall PyOpenGL PyOpenGL_accelerate numpy watchdog pyinotify ply glfw imgui[glfw]
        echo "pip: $(which -a pip)"

        # if [ ! -e ply ]; then
        #     git clone https://github.com/dabeaz/ply.git
        #     pushd ply
        #     git checkout e5d40872956764a47dbf9df6a455568f61f92173 -b build
        #     cp -pr ply ${APPDIR}/usr/lib/python3.8/site-packages
        #     popd
        # fi
    else
        echo "Miniconda already installed, skip"
        echo "Activating envinronment"
        source usr/bin/activate
    fi

    if [ ! -e ${OCC_NAME} ]; then
    	  echo "Obtaining OpenCASCADE"
        curl ${OCC740_URL} -o ${OCC_ARC_NAME}
        tar -xf ${OCC_ARC_NAME}
    else
        echo "OpenCASCADE already unpacked, skip"
    fi

    if [ ! -e ${OCC_BUILD_DIR} ]; then
    	  echo "Building OpenCASCADE"
        mkdir ${OCC_BUILD_DIR}
        pushd ${OCC_BUILD_DIR}
        cmake -DINSTALL_DIR=${APPDIR_T}/usr -DUSE_VTK=yes -DUSE_RAPIDJSON=yes -DUSE_FREEIMAGE=yes -DUSE_FFMPEG=yes ../${OCC_NAME}
        make -j $(nproc)
        make install -j $(nproc)
        popd
    else
        echo "OpenCASCADE already built, skip"
    fi

    if [ ! -e ${PYOCC_GIT} ]; then
    	  echo "Obtaining Python-OCC"
        git clone ${PYOCC_GIT_URL} -b bcad_noswap_7.4.0
    else
        echo "Python-OCC git already cloned, skip"
    fi

    # if [ ! -e ${APPDIR_T}/usr/share/cmake ]; then
    #     echo "Copying cmake stuff"
    #     cp -pr /usr/share/cmake* ${APPDIR_T}/usr/share
    #     if [ ! -e ${APPDIR_T}/usr/bin/cmake ]; then
    #        ln -s /usr/bin/cmake ${APPDIR_T}/usr/bin/cmake
    #     fi
    #     if [ ! -e ${APPDIR_T}/usr/bin/make ]; then
    #         ln -s /usr/bin/make ${APPDIR_T}/usr/bin/make
    #     fi
    #     if [ ! -e ${APPDIR_T}/usr/bin/gcc ]; then
    #         ln -s /usr/bin/gcc ${APPDIR_T}/usr/bin/gcc
    #     fi
    #     if [ ! -e ${APPDIR_T}/usr/bin/g++ ]; then
    #         ln -s /usr/bin/g++ ${APPDIR_T}/usr/bin/g++
    #     fi
    #     if [ ! -e ${APPDIR_T}/usr/bin/as ]; then
    #         ln -s /usr/bin/as ${APPDIR_T}/usr/bin/as
    #     fi
    #     if [ ! -e ${APPDIR_T}/usr/bin/ld ]; then
    #         ln -s /usr/bin/ld ${APPDIR_T}/usr/bin/ld
    #     fi
    # fi

    if [ ! -e ${PYOCC_BUILD_DIR} ]; then
    	  echo "Building Python-OCC"
        mkdir ${PYOCC_BUILD_DIR}
        pushd ${PYOCC_BUILD_DIR}
        PATH=${APPDIR_T}/usr/bin:${PATH} /usr/bin/cmake -DCMAKE_INSTALL_PREFIX=${APPDIR_T}/usr -DPYTHONOCC_INSTALL_DIRECTORY=${APPDIR_T}/usr/lib/python3/site-packages/OCC -DOpenCASCADE_DIR=${APPDIR_T}/usr/lib/cmake/opencascade -DPython3_FIND_VIRTUALENV=ONLY  ../${PYOCC_GIT}
        make -j $(nproc)
        make install -j $(nproc)
        popd
    else
        echo "Python-OCC already built, skip"        
    fi

    if [ ! -e ezdxf ]; then
        git clone https://github.com/snegovick/ezdxf.git
        pushd ezdxf
        git checkout 1070c67779f75c707c8817b2cc2eca87154fdab5 -b build
        ${APPDIR_T}/usr/bin/python3.8 setup.py build -j$(nproc) install --prefix ${APPDIR_T}/usr
        popd
        #mv ${APPDIR}/usr/lib/python3.8/site-packages/ezdxf-0.11b1-py3.8.egg/ezdxf ${APPDIR}/usr/lib/python3.8
        #mv ${APPDIR}/usr/lib/python3.8/site-packages/pyparsing-3.0.0a2-py3.8.egg/pyparsing ${APPDIR}/usr/lib/python3.8
    fi

    popd

    if [ ! -n "$(find ${APPDIR_T}/usr/lib/python3/site-packages/ -maxdepth 0 -empty)" ]; then
        echo "Copy all modules into python3.8 path"
        # rm -rf ${APPDIR}/usr/lib/python3/dist-packages/__pycache__
        # mv ${APPDIR}/usr/lib/python3/dist-packages/* ${APPDIR}/usr/lib/python3.8
        mv ${APPDIR_T}/usr/lib/python3/site-packages/* ${APPDIR_T}/usr/lib/python3.8
    else
        echo "Modules are already moved into python3.8 path"
    fi

    ${APPDIR_T}/usr/bin/python3.8 setup.py build -j$(nproc) install --prefix ${APPDIR_T}/usr
    pushd ${APPDIR_T}/usr/lib/python3.8/site-packages
    # unzip bcad-*.egg
    # mv bcad ${APPDIR}/usr/lib/python3.8
    popd

    cp -pr ${APPDIR_T} ${APPDIR}
    
    pushd ${APPDIR}

    echo "Clean up image"
    
    # rm -f bin
    # rm -rf boot
    # rm -rf etc
    # rm -f dev
    rm -rf ezdxf
    # rm -f lib32
    # #rm -f lib64
    # rm -rf media
    # rm -rf mnt
    rm -rf occ_build
    rm -rf opencascade-7.4.0
    rm opencascade-7.4.0.tgz
    # rm -rf opt
    # rm -f proc
    rm -rf pyocc_build
    rm -rf pythonocc-core
    rm  ${MINICONDA_PKG}
    # rm -rf run
    # rm -f sbin
    # rm -rf srv
    # rm -rf sys
    # rm -rf tmp
    # rm -rf var
    # rm -rf home
    # rm -f libx32

    pushd usr/bin
    find . ! -name python3.8 ! -name bcad-launcher -maxdepth 1 -type f -delete
    popd

    ACTUALLY_RM=0

    # pushd usr/lib/x86_64-linux-gnu
    # if [ -e ${ROOTDIR}/packaging/keep.list ]; then
    #     for i in *; do
    #         if ! grep -qxFe "$i" ${ROOTDIR}/packaging/keep.list; then
    #             if [ ${ACTUALLY_RM} -eq 1 ]; then
    #                 echo "Deleting: $i"
    #                 rm -rf "$i"
    #             else
    #                 echo "Pretending to delete $i"
    #             fi
    #         fi
    #     done
    # else
    #     echo "Error: ${ROOTDIR}/packaging/keep.list is missing"
    #     exit 1
    # fi
    # popd

    ACTUALLY_RM=1
    pushd usr/lib
    if [ -e ${ROOTDIR}/packaging/keep.list ]; then
        for i in *; do
            if ! grep -qxFe "$i" ${ROOTDIR}/packaging/keep.list; then
                if [ ${ACTUALLY_RM} -eq 1 ]; then
                    echo "Deleting: $i"
                    rm -rf "$i"
                else
                    echo "Pretending to delete $i"
                fi
            fi
        done
    else
        echo "Error: ${ROOTDIR}/packaging/keep.list is missing"
        exit 1
    fi
    popd


    rm -rf usr/compiler_compat
    rm -rf usr/conda-meta
    rm -rf usr/condabin
    rm -rf usr/envs
    rm -rf usr/etc
    rm -rf usr/include
    rm -rf usr/pkgs
    rm -rf usr/share
    rm -rf usr/shell
    rm -rf usr/ssl
    mv usr/LICENSE.txt usr/CONDA_LICENSE.txt
elif [ ${DEBOOTSTRAP} -eq 1 ]; then
    echo "Running dbst"
    bash packaging/run-dbst.sh bcad.AppDir_t
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
    pushd ${APPDIR}/usr/lib/python3.8/site-packages
    unzip bcad-*.egg
    mv bcad ${APPDIR}/usr/lib/python3.8
    popd
    
    pushd ${APPDIR}

    echo "Clean up image"
    
    rm -f bin
    rm -rf boot
    rm -rf etc
    rm -f dev
    rm -rf ezdxf
    rm -f lib32
    #rm -f lib64
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
    rm -rf home
    rm -f libx32

    pushd usr/bin
    find . ! -name python3.8 ! -name bcad-launcher -maxdepth 1 -type f -delete
    popd

    pushd usr/lib/x86_64-linux-gnu
    ACTUALLY_RM=0

    if [ -e ${ROOTDIR}/packaging/keep.list ]; then
        for i in *; do
            if ! grep -qxFe "$i" ${ROOTDIR}/packaging/keep.list; then
                if [ ${ACTUALLY_RM} -eq 1 ]; then
                    echo "Deleting: $i"
                    rm -rf "$i"
                else
                    echo "Pretending to delete $i"
                fi
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
                if [ ${ACTUALLY_RM} -eq 1 ]; then
                    echo "Deleting: $i"
                    rm -rf "$i"
                else
                    echo "Pretending to delete $i"
                fi
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

# cat >"AppRun" <<\EOF
# #!/bin/sh
# set -e
# APPDIR="$(dirname "$(readlink -e "$0")")"
# export LD_LIBRARY_PATH="${APPDIR}/usr/lib/:${APPDIR}/lib/x86_64-linux-gnu:${APPDIR}/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}"
# export PATH="${APPDIR}/usr/bin:${PATH}"
# exec "${APPDIR}/usr/bin/python3.8" -m bcad.binterpreter.glfw_display "$@"
# EOF
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

cp ../bcad.desktop ./
cp ../bcad.png ./
cp ../bcad-launcher ./usr/bin/

popd

#ARCH=x86_64 /tmp/appimagetool-x86_64.AppImage ${APPDIR}
/tmp/appimagetool-x86_64.AppImage --appimage-extract
./squashfs-root/AppRun ${APPDIR}
echo "======================"
echo "Cleaning up"
echo "======================"
#rm -rf ${APPDIR}
