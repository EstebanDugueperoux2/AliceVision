FROM debian:bullseye

RUN apt-get -y update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y crossbuild-essential-arm64 python3-pip cmake ccache ninja-build ssh git vim pkg-config wget software-properties-common && \
    pip install --upgrade conan pylint yamllint

COPY global.conf /root/.conan2/global.conf
RUN conan config install https://github.com/conan-io/hooks.git
RUN mkdir -p /root/.conan2/extensions/hooks/

# Cuda
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/debian10/x86_64/cuda-keyring_1.1-1_all.deb
RUN dpkg -i cuda-keyring_1.1-1_all.deb
RUN add-apt-repository contrib
RUN apt-get update
RUN apt-get -y install cuda-toolkit-12-4
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y cuda-drivers
RUN apt-get install -y nvidia-kernel-open-dkms
RUN apt-get install -y cuda-drivers
# Cuda arm jetson
# RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/cross-linux-aarch64/cuda-keyring_1.1-1_all.deb
# RUN dpkg -i cuda-keyring_1.1-1_all.deb
# RUN apt-get update
# RUN apt-get -y install cuda-cross-aarch64

RUN conan remote remove conancenter
RUN conan remote add local       http://artifactory:8081/artifactory/api/conan/local
RUN conan remote add conancenter http://artifactory:8081/artifactory/api/conan/conancenter
ENV CMAKE_CXX_COMPILER_LAUNCHER ccache
RUN apt-get install -y libfontenc-dev libfontenc1 libice-dev libice6 libpthread-stubs0-dev libsm-dev libsm6 libx11-dev libx11-xcb-dev libx11-xcb1 libxau-dev libxaw7 libxaw7-dev libxcb-composite0 libxcb-composite0-dev libxcb-cursor-dev libxcb-cursor0 libxcb-dri2-0 libxcb-dri2-0-dev libxcb-dri3-0 libxcb-dri3-dev libxcb-ewmh-dev libxcb-ewmh2 libxcb-glx0 libxcb-glx0-dev libxcb-icccm4 libxcb-icccm4-dev libxcb-image0 libxcb-image0-dev libxcb-keysyms1 libxcb-keysyms1-dev libxcb-present-dev libxcb-present0 libxcb-randr0 libxcb-randr0-dev libxcb-render-util0 libxcb-render-util0-dev libxcb-render0 libxcb-render0-dev libxcb-res0 libxcb-res0-dev libxcb-shape0 libxcb-shape0-dev libxcb-shm0 libxcb-shm0-dev libxcb-sync-dev libxcb-sync1 libxcb-util1 libxcb-xfixes0 libxcb-xfixes0-dev libxcb-xinerama0 libxcb-xinerama0-dev libxcb-xkb-dev libxcb-xkb1 libxcb1-dev libxcomposite-dev libxcomposite1 libxcursor-dev libxcursor1 libxdamage-dev libxdamage1 libxdmcp-dev libxext-dev libxfixes-dev libxfixes3 libxi-dev libxi6 libxinerama-dev libxinerama1 libxkbfile-dev libxkbfile1 libxmu-dev libxmu-headers libxmu6 libxmuu-dev libxpm-dev libxrandr-dev libxrandr2 libxrender-dev libxrender1 libxres-dev libxres1 libxss-dev libxss1 libxt-dev libxt6 libxtst-dev libxtst6 libxv-dev libxv1 libxxf86vm-dev libxxf86vm1 uuid-dev x11-common x11proto-dev x11proto-input-dev x11proto-randr-dev x11proto-record-dev x11proto-scrnsaver-dev x11proto-xext-dev x11proto-xf86vidmode-dev x11proto-xinerama-dev xorg-sgml-doctools xtrans-dev
# ARG DOCKER_USER=default_user
# RUN addgroup $DOCKER_USER && adduser $DOCKER_USER -G $DOCKER_USER
# USER $DOCKER_USER

# RUN git clone https://github.com/irieger/conan-center-index.git
# RUN conan profile detect
# RUN cd conan-center-index/recipes/openimageio/all/ && \
#     git switch oiio-v2.4.15.0-conan2.0 && conan create . --version 2.5.6.0 --build missing -c tools.system.package_manager:mode=install
# #openblas crosscompile support: https://github.com/conan-io/conan-center-index/pull/21485
# RUN cd / && \
#     git clone https://github.com/exyntech/conan-center-index.git conan-center-indexForOpenBlas 
# RUN cd conan-center-indexForOpenBlas/recipes/openblas/all/ && \
#     git switch openblas-cross-compile && \
#     conan create . --version 0.3.26

# RUN git clone https://github.com/EstebanDugueperoux2/AliceVision.git
# RUN cd /AliceVision && \
#     git switch feature/AddConanSupport && \
#     conan create . --build missing -s build_type=Debug -o \*:shared=True --profile:build .conan/profiles/build_profile --profile:host .conan/profiles/linux-armv7hf-gcc7 -c tools.system.package_manager:mode=install

# export GID=$(id -g)
# docker build --build-arg DOCKER_USER=$UID -f Dockerfile  context/  -t alicevision
# docker run -it --user $UID:$GID --workdir="/home/$USER" --volume="/etc/group:/etc/group:ro" \
#     --volume="/etc/passwd:/etc/passwd:ro" \
#     --volume="/etc/shadow:/etc/shadow:ro" \
#     -v $PWD:/home/$USER/alicevision/ alicevision bash
