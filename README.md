# Setup Artifactory instance

Setup an Artifactory instance locally to avoid rebuild binaries at each build and to do immutable build:

sudo docker compose up -d

https://jfrog.com/help/r/jfrog-installation-setup-documentation/install-artifactory-single-node-with-docker

http://localhost:8082/ui/

Create a conan remote repository named conancenter to https://center.conan.io/
Create a local repository named local

sudo docker exec -it alicevision-conan_client-1 bash

conan remote add conancenter http://artifactory:8081/artifactory/api/conan/conancenter
conan remote login -p password conancenter admin

conan remote add local http://localhost:8081/artifactory/api/conan/local
conan remote login -p password local admin

conan profile detect 
set Debug
set 17 instead of gnu14

https://www.baeldung.com/linux/shared-library-exported-functions
nm -D --demangle

# Standard build using conan 2.x

Currently works only with shared:

`docker run --memory=10g --cpus=10 --rm -ti -v conan_cache:~/.conan2/ debian:bullseye
apt -y update
apt install -y python3-pip cmake ninja-build git vim pkg-config
pip install --upgrade "conan"
git clone https://github.com/EstebanDugueperoux2/AliceVision.git
cd /AliceVision
git switch feature/AddConanSupport
export CC="ccache gcc"
export CXX="ccache g++"
export CMAKE_CXX_COMPILER_LAUNCHER=ccache
export CCACHE_DEBUG=true

#GCC
time conan create . --build missing -o */*:shared=True -o opencolorio/*:shared=False -s build_type=Debug --profile:build .conan/profiles/build_profile --profile:host .conan/profiles/build_profile -c tools.system.package_manager:mode=install &> build_shared.log

#Clang
time conan create . --build missing -o */*:shared=True -o opencolorio/*:shared=False -s build_type=Debug --profile:build .conan/profiles/build_profile --profile:host .conan/profiles/build_profile_clang -c tools.system.package_manager:mode=install &> build_shared.log

conan graph info . -o */*:shared=True -s build_type=Debug --profile:build .conan/profiles/build_profile --profile:host .conan/profiles/build_profile -c tools.system.package_manager:mode=install --format=html > graph.html

conan install --requires=alicevision/3.2.0 --deployer=direct_deploy --deployer-package=* --deployer-folder ../alice_vision_deploy/ -o */*:shared=True -s build_type=Debug --profile:build .conan/profiles/build_profile --profile:host .conan/profiles/build_profile

conan upload -r local -c "*/*"

`

See https://github.com/rymut/cuda-toolkit-conan-package for cuda support

## Build opencolorio to allow shared build (See https://github.com/conan-io/conan-center-index/pull/24395)

To fix https://github.com/conan-io/conan-center-index/issues/23421
git clone https://github.com/irieger/conan-center-index.git /conan-center-index-irieger
cd /conan-center-index-irieger/recipes
git switch opencolorio/fix-conanfile
cd opencolorio/all/
conan create . --version 2.3.2 --build missing

## Build coin:

git clone https://github.com/valgur/conan-center-index.git /conan-center-index-valgur
cd /conan-center-index-valgur/recipes/glpk/all/
git switch update/glpk
conan create . --version 4.48 --build missing
conan create . --version 4.65 --build missing

git switch new/coin-buildtools
cd /conan-center-index-valgur/recipes/coin-buildtools/all/
conan create . --version 0.8.11 --build missing

git switch update/coin-utils
cd /conan-center-index-valgur/recipes/coin-utils/all/
conan create . --version 2.11.11 --build missing

git switch update/coin-osi
cd /conan-center-index-valgur/recipes/coin-osi/all/
conan create . --version 0.108.10 --build missing

apt install -y liblapack-dev
apt install -y libopenblas64-dev

apt install -y coinor-libclp-dev
apt install -y coinor-libcoinutils-dev
apt install -y liblemon-dev

cd /
git clone https://github.com/alicevision/CoinUtils
cd CoinUtils
cmake .
make 
make install

cd /
git clone https://github.com/alicevision/Osi
cd Osi
cmake .
make 
make install

cd /
git clone https://github.com/alicevision/Clp
cd Clp
cmake .
make
make install

git switch update/coin-clp
cd /conan-center-index-valgur/recipes/coin-clp/all/
conan create . --version 1.17.9 --build missing

git switch update/coin-cgl
cd /conan-center-index-valgur/recipes/coin-cgl/all/
conan create . --version 0.60.8 --build missing

git switch update/coin-cbc
cd /conan-center-index-valgur/recipes/coin-cbc/all/
conan create . --version 2.10.11 --build missing

git clone https://github.com/EstebanDugueperoux2/conan-center-index.git /conan-center-index-estebandugueperoux
cd /conan-center-index-estebandugueperoux/recipes/
git switch feature/AddGeogram
cd geogram/all/
conan create . --version 1.9.0 --build missing

git switch feature/AddOpenUSD
cd ../../openusd/all/
conan create . --version 24.08 --build missing -o "openusd/*:shared=True" -c tools.system.package_manager:mode=install


cd /conan-center-index-valgur/recipes/pcl/all/
git switch update/pcl
conan create . --version 1.14.1 --build missing -c tools.system.package_manager:mode=install

# As build with static assimp failed because of "undefined symbol" error witht zlib symbos, we build with shared assimp lib:
conan create . --build missing -o assimp/*:shared=True  -c tools.system.package_manager:mode=install &> build.log

export LD_LIBRARY_PATH=/root/.conan2/p/b/assim5e00d8fc0748f/p/lib/
export ALICEVISION_ROOT=/root/.conan2/p/b/alice7290e4b9f1aac/p
$ALICEVISION_ROOT/bin/aliceVision_LdrToHdrCalibration


Inside docker container we get a segfault:

[2024-08-11 11:54:00.279389] [0x00007fd98c2cbcc0] [trace]   Embedded OCIO configuration file: '/root/.conan2/p/b/alicecf851d9218975/p/share/aliceVision/config.ocio' found.
Segmentation fault (core dumped)

Outside docker container:
mkdir test
cd test
docker cp alicevision_conan_client_1:/root/.conan2/p/b/assim5e00d8fc0748f/p/lib/ .
docker cp alicevision_conan_client_1:/root/.conan2/p/b/alice7290e4b9f1aac/p/bin/ .
export ALICEVISION_ROOT=$PWD
./bin/aliceVision_applyCalibration

[2024-08-12 11:34:31.985701] [0x00007f29f5a9ccc0] [error]   Embedded OCIO configuration file: '/home/estebandugueperoux/Documents/git/AliceVision/test/share/aliceVision/config.ocio' cannot be accessed.
terminate called after throwing an instance of 'std::runtime_error'
  what():  Embedded OCIO configuration file: '/home/estebandugueperoux/Documents/git/AliceVision/test/share/aliceVision/config.ocio' cannot be accessed.
Abandon (core dumped)

# Cross building instructions targeting Raspberry PI 4 having Raspberry Pi OS (64 bits)

`
docker run --rm -ti debian:bullseye
apt -y update
apt install -y crossbuild-essential-arm64 python3-pip cmake ninja-build ssh git vim pkg-config
dpkg --add-architecture arm64


# Cuda arm jetson
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/cross-linux-aarch64/cuda-keyring_1.1-1_all.deb
dpkg -i cuda-keyring_1.1-1_all.deb
apt-get update
apt-get -y install cuda-cross-aarch64

pip install --upgrade "conan"
git clone https://github.com/EstebanDugueperoux2/AliceVision.git
#openblas crosscompile support: https://github.com/conan-io/conan-center-index/pull/21485
git clone https://github.com/exyntech/conan-center-index.git
cd conan-center-index/
git switch openblas-cross-compile
cd recipes/openblas/all
conan profile detect
conan create . --version 0.3.26

cd /AliceVision
git switch feature/AddConanSupport
conan create . --build missing -s build_type=Debug -o \*:shared=True --profile:build .conan/profiles/build_profile --profile:host .conan/profiles/linux-armv7hf-gcc7 -c tools.system.package_manager:mode=install

with shared option failed because coin\* project doesn't supports cross-compilation with this option

without shared option

FIXME:
openimageio has an hard requirement on libtiff which doesn't crosscompile:

CMake Error at /root/.conan2/p/cmakecf6b18ccaa9f5/p/share/cmake-3.28/Modules/FindPackageHandleStandardArgs.cmake:230 (message):
Could NOT find CMath (missing: CMath_pow)
Call Stack (most recent call first):
/root/.conan2/p/cmakecf6b18ccaa9f5/p/share/cmake-3.28/Modules/FindPackageHandleStandardArgs.cmake:600 (\_FPHSA_FAILURE_MESSAGE)
cmake/FindCMath.cmake:51 (FIND_PACKAGE_HANDLE_STANDARD_ARGS)
CMakeLists.txt:136 (find_package)

See https://gitlab.com/libtiff/libtiff/-/blob/master/cmake/FindCMath.cmake?ref_type=heads

conan graph info . &> dependencies_graph.txt
conan graph info . --format=html > dependencies_graph.html

`

# Test with meshroom

`cd Documents/git/Meshroom/
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ALICEVISION*INSTALL=~/.conan/data/alicevision/3.1.0/*/\_/package/48534226977c123544c066ac59ba1f907802a9e7/
export ALICEVISION*ROOT=$ALICEVISION_INSTALL
export ALICEVISION_SENSOR_DB=${ALICEVISION_INSTALL}/share/aliceVision/cameraSensors.db
export LD_LIBRARY_PATH=${ALICEVISION_INSTALL}/lib:/home/estebandugueperoux/.conan/data/boost/1.84.0/*/\_/package/7009ed669f95f7c2d308b844558689f6bb6e501b/lib/:$LD_LIBRARY_PATH
export MESHROOMPATH=$PWD
export PYTHONPATH=${MESHROOMPATH}
export PATH=$PATH:${ALICEVISION_INSTALL}/bin
export QML2_IMPORT_PATH=/home/estebandugueperoux/Téléchargements/Meshroom-2023.3.0/qtPlugins/qml/
export ALICEVISION_LENS_PROFILE_INFO=""
export ALICEVISION_VOCTREE=/home/estebandugueperoux/Documents/git/trainedVocabularyTreeData/vlfeat_K80L3.SIFT.tree
export ALICEVISION_SPHERE_DETECTION_MODEL=/home/estebandugueperoux/Documents/git/SphereDetectionModel/sphereDetection_Mask-RCNN.onnx
export ALICEVISION_SEMANTIC_SEGMENTATION_MODEL=/home/estebandugueperoux/Documents/git/semanticSegmentationModel/fcn_resnet50.onnx
python meshroom/ui
python -m pdb meshroom/ui/**main**.py

aliceVision*cameraInit --sensorDatabase "/home/estebandugueperoux/.conan/data/alicevision/3.1.0/*/\_/package/48534226977c123544c066ac59ba1f907802a9e7//share/aliceVision/cameraSensors.db" --lensCorrectionProfileInfo "" --lensCorrectionProfileSearchIgnoreCameraModel True --defaultFieldOfView 45.0 --groupCameraFallback folder --allowedCameraModels pinhole,radial1,radial3,brown,fisheye4,fisheye1,3deanamorphic4,3deradial4,3declassicld --rawColorInterpretation LibRawWhiteBalancing --viewIdMethod metadata --verboseLevel info --output "/tmp/tmpt9ncjha9/CameraInit/961e54591174ec5a2457c66da8eadc0cb03d89ba/cameraInit.sfm" --allowSingleView 1 --input "/tmp/tmpt9ncjha9/CameraInit/961e54591174ec5a2457c66da8eadc0cb03d89ba/viewpoints.sfm"

gdb aliceVision\*cameraInit
`

# ![AliceVision - Photogrammetric Computer Vision Framework](https://github.com/alicevision/AliceVision/raw/develop/docs/logo/AliceVision_banner.png)

[AliceVision](http://alicevision.github.io) is a Photogrammetric Computer Vision Framework which provides a 3D Reconstruction and Camera Tracking algorithms.
AliceVision aims to provide strong software basis with state-of-the-art computer vision algorithms that can be tested, analyzed and reused.
The project is a result of collaboration between academia and industry to provide cutting-edge algorithms with the robustness and the quality required for production usage.

Learn more details about the pipeline and tools based on it on [AliceVision website](http://alicevision.github.io).

See [results of the pipeline on sketchfab](http://sketchfab.com/AliceVision).

## Photogrammetry

Photogrammetry is the science of making measurements from photographs.
It infers the geometry of a scene from a set of unordered photographies or videos.
Photography is the projection of a 3D scene onto a 2D plane, losing depth information.
The goal of photogrammetry is to reverse this process.

See the [presentation of the pipeline steps](http://alicevision.github.io/#photogrammetry).

## License

The project is released under MPLv2, see [**COPYING.md**](COPYING.md).

## Citation

If you use this project for a publication, please cite the [paper](https://hal.archives-ouvertes.fr/hal-03351139):

```
@inproceedings{alicevision2021,
  title={{A}liceVision {M}eshroom: An open-source {3D} reconstruction pipeline},
  author={Carsten Griwodz and Simone Gasparini and Lilian Calvet and Pierre Gurdjos and Fabien Castan and Benoit Maujean and Gregoire De Lillo and Yann Lanthony},
  booktitle={Proceedings of the 12th ACM Multimedia Systems Conference - {MMSys '21}},
  doi = {10.1145/3458305.3478443},
  publisher = {ACM Press},
  year = {2021}
}
```

## Bibliography

See [**Bibliography**](BIBLIOGRAPHY.md) for the list of research papers and tools used in this project.

## Get the project

Get the source code: `git clone --recursive git://github.com/alicevision/AliceVision`

See [**INSTALL.md**](INSTALL.md) to build the project.

Continuous integration status: [![Build Status](https://travis-ci.org/alicevision/AliceVision.png?branch=develop)](https://travis-ci.org/alicevision/AliceVision) [![Coverage Status](https://coveralls.io/repos/github/alicevision/AliceVision/badge.png?branch=develop)](https://coveralls.io/github/alicevision/AliceVision?branch=develop).

## Launch 3D reconstructions

Use [Meshroom](https://github.com/alicevision/meshroom) to launch the AliceVision pipeline.

- Meshroom provides a User Interface to create 3D reconstructions.
- Meshroom provides a command line to launch all the steps of the pipeline.
- Meshroom is written in python and can be used to create your own python scripts to customize the pipeline or create custom automation.

The User Interface of Meshroom relies on Qt and PySide. The Meshroom engine and command line has no dependency to Qt.

## Contact

Use the public mailing-list to ask questions or request features. It is also a good place for informal discussions like sharing results, interesting related technologies or publications:

> [alicevision@googlegroups.com](mailto:alicevision@googlegroups.com) > [http://groups.google.com/group/alicevision](http://groups.google.com/group/alicevision)

You can also contact the core team privately on: [alicevision-team@googlegroups.com](mailto:alicevision-team@googlegroups.com).

## Contributing

[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/2995/badge)](https://bestpractices.coreinfrastructure.org/projects/2995)

Beyond open source interest to foster developments, open source is a way of life. The project has started as a collaborative project and aims to continue. We love to exchange ideas, improve ourselves while making improvements for other people and discover new collaboration opportunities to expand everybody’s horizon.
Contributions are welcome. We integrate all contributions as soon as it is useful for someone, don't create troubles for others and the code quality is good enough for maintainance.

Please have a look at the [project code of conduct](CODE_OF_CONDUCT.md) to provide a friendly, motivating and welcoming environment for all.
Please have a look at the [project contributing guide](CONTRIBUTING.md) to provide an efficient workflow that minimize waste of time for contributors and maintainers as well as maximizing the project quality and efficiency.

Use github Pull Requests to submit contributions:

> [http://github.com/alicevision/AliceVision/issues](http://github.com/alicevision/AliceVision/issues)

Use the public mailing-list to ask questions or request features and use github issues to report bugs:

> [http://github.com/alicevision/AliceVision/pulls](http://github.com/alicevision/AliceVision/pulls)

## Project history

In 2009, CMP research team from CTU started the PhD thesis of Michal Jancosek supervised by Tomas Pajdla. They released windows binaries of their MVS pipeline, called CMPMVS, in 2012.
In 2009, Toulouse INP, INRIA and Duran Duboi started a French ANR project to create a model based Camera Tracking solution based on natural features and a new marker design called CCTag.
In 2010, Mikros Image and IMAGINE research team (a joint research group between Ecole des Ponts ParisTech and Centre Scientifique et Technique du Batiment) started a partnership around Pierre Moulon’s thesis, supervised by Renaud Marlet and Pascal Monasse on the academic side and Benoit Maujean on the industrial side. In 2013, they released an open source SfM pipeline, called openMVG (“Multiple View Geometry”), to provide the basis of a better solution for the creation of visual effects matte-paintings.
In 2015, Simula, Toulouse INP and Mikros Image joined their efforts in the EU project POPART to create a Previz system based on AliceVision.
In 2017, CTU join the team in the EU project LADIO to create a central hub with structured access to all data generated on set based on AliceVision.

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for the full list of contributors. We hope to see you in this list soon!
