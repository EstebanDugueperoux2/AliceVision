from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.system import package_manager
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
import os

class AliceVisionRecipe(ConanFile):
    name = "alicevision"
    description = "Photogrammetric Computer Vision Framework"
    version = "3.2.0"
    license = "MPL-2.0"
    author = "AliceVision"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://alicevision.org"
    topics = (
        "computer-vision",
        "structure-from-motion",
        "photogrammetry",
        "3d-reconstruction",
        "panorama-image",
        "camera-tracking",
        "panorama-stitching",
        "multiview-stereo",
        "meshroom",
        "alicevision",
        "hdri-image",
    )
    settings = "os", "compiler", "build_type", "arch"

    exports_sources = "CMakeLists.txt", "src/**", "docs/**", "**.md"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_sfm": [True, False],
        "with_mvs": [True, False],
        "with_hdr": [True, False],
        "with_segmentation": [True, False],
        "with_stereophometry": [True, False],
        "with_panorama": [True, False],
        "with_cli": [True, False],
        "with_openmp": [True, False],
        "with_cctag": [True, False],
        "with_apriltag": [True, False],
        "with_popsift": [True, False],
        "with_opengv": [True, False],
        "with_alembic": [True, False],
        "with_uncertaintype": [True, False],        
        "with_onnx": [True, False],
        "with_onnx_gpu": [True, False],
        "with_cuda": [True, False],
        "with_opencv": [True, False],
        "with_lidar": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        # TODO: make https://github.com/conan-io/conan-center-index/pull/23534 working to enable this option
        "with_sfm": True,
        "with_mvs": False,
        "with_hdr": False,
        "with_segmentation": False,
        "with_stereophometry": False,
        "with_panorama": False,
        "with_cli": True,
        "with_openmp": False,
        "with_cctag": False,
        "with_apriltag": False,
        "with_popsift": False,
        "with_opengv": False,
        "with_alembic": False,
        # TODO: will be removed in 3.3 release, see https://github.com/alicevision/AliceVision/pull/1550
        "with_uncertaintype": False,
        "with_onnx": False,
        "with_onnx_gpu": False,
        "with_cuda": False,
        "with_opencv": False,
        "with_lidar": False,
        # Needed by aliceVision/keyframe/KeyframeSelector.hpp
        "opencv/*:optflow": True,
        "opencv/*:ximgproc": True,
        # Needed by src/software/utils/main_colorCheckerCorrection.cpp     
        "opencv/*:mcc": True,
        
        # See https://github.com/bytedeco/javacpp-presets/issues/32
        # Need only for static build to avoid a openssl no found 
        # "ffmpeg/*:with_ssl": False,
        # Integrate https://github.com/conan-io/conan-center-index/issues/23421 to have shared works with opencolorio
        # "openimageio/*:with_opencolorio": False,
        # "openusd/*:build_opencolorio_plugin": False,
        "opencv/*:with_wayland": False,
        # To avoid https://stackoverflow.com/questions/12824134/undefined-reference-to-pow-in-c-despite-including-math-h
        # "openimageio/*:with_giflib": False,
        # "openblas/*:dynamic_arch": True,
        # "cctag/*:with_cuda": True,

        # "protobuf/*:upb": True
    }

    @property
    def _min_cppstd(self):
        return 17

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        # if self.options.with_stereophometry or self.options.with_sfm:
        #     self.options.with_mvs = True

    def layout(self):
        # cmake_layout(self, src_folder="src")
        cmake_layout(self)

    def requirements(self):
        # self.requires("zlib/[>=1.2.11 <2]")
        self.requires("assimp/5.4.2")
        # self.requires("libwebp/1.3.2")
        self.requires("openimageio/2.5.14.0", options={"with_ffmpeg":False})
        self.requires("hdf5/1.14.4.3", override=True)
        self.requires("opencolorio/2.3.2", override=True)
        self.requires("cpuinfo/cci.20231129", override=True)

        #To fix following error:
        # libprotocd.so.3.21.12.0: error: undefined reference to 'descriptor_table_google_2fprotobuf_2fdescriptor_2eproto' 

#         CMake Error at CMakeLists.txt:184 (find_package):
#   By not providing "Findutf8_range.cmake" in CMAKE_MODULE_PATH this project
        # self.requires("protobuf/5.27.0", override=True)

        # self.requires("xz_utils/5.4.5", override=True)
        # self.requires("freetype/2.13.2", override=True)
        # self.requires("expat/2.6.2", override=True)
        # self.requires("expat/2.4.8", override=True)
        # self.requires("pugixml/1.14", override=True)
        if self.options.with_alembic:
           self.requires("alembic/1.8.6")        
        self.requires("boost/1.86.0", override=True)
        # self.requires("onetbb/2019_u9", override=True)
        self.requires("eigen/3.4.0")
        self.requires("openexr/3.2.4", override=True)
        # self.requires("opengv/cci.20200806")
        # self.requires("gmp/6.3.0")
        # self.requires("mpfr/4.2.1")
        # # TODO: make ceres cross compile to armv8
        self.requires("ceres-solver/2.2.0")
        # self.requires("libx264/cci.20220602")
        # self.requires("libx265/3.4")
        if self.options.with_apriltag:
            self.requires("apriltag/3.1.4")
        # self.requires("coin-utils/[>=2.11.11 <3]")
        # # TODO: upgrade to 1.17.9
        # self.requires("coin-clp/1.17.9")
        # self.requires("coin-cbc/2.10.5")
        # See https://github.com/conan-io/conan-center-index/pull/23536
        # self.requires("coin-cbc/2.10.11")
        # self.requires("coin-lemon/1.3.1")
        self.requires("lemon/3.32.3")

        # self.requires("libpng/1.6.42", override=True)
        # self.requires("lz4/1.9.4")

        # # Use geogram installed by a direct "make install" local build
        # # TODO: add geogram to conan-center
        if self.options.with_mvs:
            self.requires("geogram/1.9.0")
            self.requires("openmesh/11.0")
        # # self.requires("gfortran/10.2")
        # # LAPACK
        # # SuiteSparse

        # # self.requires("apriltag/3.3.0")
        # # self.requires("popsift/0.9")
        if self.options.with_opengv:
            self.requires("opengv/cci.20200806")
        # # AliceVision have its fork (https://github.com/alicevision/flann)
        # self.requires("flann/1.9.2")
        # Use an older release of nanoflann to be more near than AliceVision fork
        self.requires("nanoflann/1.5.2")
#         Because with release 1.6.0 got following error:
#             ../../src/aliceVision/fuseCut/PointCloud.cpp:58:86:   required from here
# /root/.conan2/p/nanofdf3cf2c8ea57d/p/include/nanoflann.hpp:1697:41: error: ‘class aliceVision::fuseCut::SmallerPixSizeInRadius<double, long unsigned int>’ has no member named ‘sort’
#  1697 |         if (searchParams.sorted) result.sort();

        # # Requires python 3.8+ to be built as shared.
        if self.options.with_onnx:
            self.requires("onnxruntime/1.18.1")
            # self.requires("abseil/20240722.0", override=True)
            # self.requires("abseil/20240722.0", override=True)
        # # IN PROGRESS
        # self.requires("openusd/24.08")
        if self.options.with_lidar:
            self.requires("libe57format/3.1.1")

        # To avoid "Unable to locate package libXXX-dev:arm64" error in system requirements in crosscompile
        # if cross_building(self):
        self.requires("ffmpeg/4.4.4", override=True, options={"with_vaapi": False, "with_vdpau": False, "with_xcb": False, "with_pulse": False})
        # See https://github.com/conan-io/conan-center-index/pull/22152
        # See https://github.com/conan-io/conan-center-index/pull/24562
        # self.requires("pcl/1.13.1")
        self.requires("pcl/1.14.1", options={"with_libusb": False})
        self.requires("openjpeg/2.5.2", override=True)

        self.requires("openblas/0.3.27", override=True)
        # # MeshSDFilter?
        
        if self.options.with_opencv:
            self.requires("opencv/4.10.0", options={"with_wayland": False})
    
        if self.options.with_cctag:
            self.requires("cctag/1.0.4")
        
        # # # Optional
        # https://conan.io/center/cuda-api-wrappers?
        # # # Magma?
        # # # Mosek?
        # # PopSift, needs cuda?
        # if self.options.with_popsift:
        #     self.requires("popsift/0.9")
        # # UncertaintyTE?
    
    def build_requirements(self):
        self.tool_requires("ccache/4.10")
   
    # def system_requirements(self):
    #     self.options.with_cctag:
            
    #     package_manager.Apt(self).install(["libblas-dev"])
    #     if self.options.shared:
    #         package_manager.Dnf(self).install(["blas-devel"])
    #         package_manager.Dnf(self).install(["lapack-devel"])
    #     else:
    #         package_manager.Dnf(self).install(["blas-static"])
    #         package_manager.Dnf(self).install(["lapack-static"])

    def generate(self):
        tc = CMakeToolchain(self, generator="Ninja")
        tc.variables["ALICEVISION_BUILD_SFM"] = self.options.with_sfm
        tc.variables["ALICEVISION_BUILD_MVS"] = self.options.with_mvs
        tc.variables["ALICEVISION_BUILD_HDR"] = self.options.with_hdr
        tc.variables["ALICEVISION_BUILD_SEGMENTATION"] = self.options.with_segmentation
        tc.variables["ALICEVISION_BUILD_STEREOPHOTOMETRY"] = self.options.with_stereophometry
        tc.variables["ALICEVISION_BUILD_PANORAMA"] = self.options.with_panorama
        tc.variables["ALICEVISION_BUILD_SOFTWARE"] = self.options.with_cli
        
        tc.variables["ALICEVISION_USE_OPENMP"] = "ON" if self.options.with_openmp else "OFF"
        tc.variables["ALICEVISION_USE_CCTAG"] = "ON" if self.options.with_cctag else "OFF"
        tc.variables["ALICEVISION_USE_APRILTAG"] = "ON" if self.options.with_apriltag else "OFF"
        tc.variables["ALICEVISION_USE_POPSIFT"] = "ON" if self.options.with_popsift else "OFF"
        tc.variables["ALICEVISION_USE_OPENGV"] = "ON" if self.options.with_opengv else "OFF"
        tc.variables["ALICEVISION_USE_ALEMBIC"] = "ON" if self.options.with_alembic else "OFF"
        tc.variables["ALICEVISION_USE_UNCERTAINTYTE"] = "ON" if self.options.with_uncertaintype else "OFF"
        tc.variables["ALICEVISION_USE_ONNX"] = "ON" if self.options.with_onnx else "OFF"
        tc.variables["ALICEVISION_USE_ONNX_GPU"] = "ON" if self.options.with_onnx_gpu else "OFF"
        tc.variables["ALICEVISION_USE_OPENCV"] = 'ON' if self.options.with_opencv else "OFF"
        tc.variables["ALICEVISION_USE_OPENCV_CONTRIB"] = 'ON' if self.options.with_opencv else "OFF"
        tc.variables["ALICEVISION_USE_CUDA"] = "ON" if self.options.with_cuda else "OFF"
        tc.variables["ALICEVISION_USE_MESHSDFILTER"] = False
        tc.variables["ALICEVISION_BUILD_LIDAR"] = "ON" if self.options.with_lidar else "OFF"
        # tc.variables["AV_BUILD_LAPACK"] = False
        self.output.info("Extra warning")
        self.output.info(self.dependencies['lemon'].cpp_info.libdirs)
        self.output.info(self.dependencies['lemon'].cpp_info.includedirs)
        self.output.info(self.dependencies['lemon'].cpp_info.libs)
        # tc.variables["LEMON_LIBRARY"] = self.dependencies['lemon'].cpp_info.libdirs[0]
        
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("minizip", "cmake_target_name", "MINIZIP::minizip")
        # deps.set_property("coin-utils", "cmake_target_name", "Coin::CoinUtils")
        # deps.set_property("coin-clp", "cmake_target_name", "Coin::Clp")
        # deps.set_property("coin-osi", "cmake_target_name", "Coin::Osi")
        deps.set_property("nanoflann", "cmake_target_name", "nanoflann")
        deps.generate()
        
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.verbose = True
        cmake.build(cli_args=["--verbose"], build_tool_args=["-j 5"])

    def package(self):
        cmake = CMake(self)
        cmake.install()
        
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        
    # def package_info(self):
    #     self.cpp_info.components["libaliceVision_system"].libs = ["libaliceVision_system"]
    #     self.cpp_info.components["libaliceVision_system"].requires = ["boost::thread", "boost::log"]

    #     self.cpp_info.components["libaliceVision_cmdline"].libs = ["libaliceVision_cmdline"]
    #     self.cpp_info.components["libaliceVision_cmdline"].requires = ["libaliceVision_system", 
    #                                                                  "boost::program_options",
    #                                                                  ]

    #     self.cpp_info.components["libaliceVision_numeric"].libs = ["libaliceVision_numeric"]
    #     self.cpp_info.components["libaliceVision_numeric"].requires = ["boost::log"]
        
    #     self.cpp_info.components["libaliceVision_image"].libs = ["libaliceVision_image"]
    #     self.cpp_info.components["libaliceVision_image"].requires = ["libaliceVision_numeric", 
    #                                                                  "libaliceVision_system", 
    #                                                                  "openimageio::openimageio_openimageio",
    #                                                                  "openimageio::openimageio_openimageio_util",
    #                                                                 # TODO: add OPENEXR_LIBRARIES
    #                                                                  ]

    #     self.cpp_info.components["libvlsift"].libs = ["libvlsift"]
    #     self.cpp_info.components["libvlsift"].system_libs.append("gomp")

    #     self.cpp_info.components["libaliceVision_gpu"].libs = ["libaliceVision_gpu"]
    #     self.cpp_info.components["libaliceVision_gpu"].requires = ["libaliceVision_system"]
    #     if self.options.with_cuda:
    #         # TODO: add cuda requirements
    #         self.cpp_info.components["libaliceVision_gpu"].requires = ["CUDA_LIBRARIES"]
        
    #     self.cpp_info.components["libaliceVision_camera"].libs = ["libaliceVision_camera"]
    #     self.cpp_info.components["libaliceVision_camera"].requires = ["libaliceVision_numeric", 
    #                                                                  "libaliceVision_geometry",
    #                                                                  "libaliceVision_image",
    #                                                                  "libaliceVision_stl",
    #                                                                  "libaliceVision_system",
    #                                                                  ]

    #     self.cpp_info.components["libaliceVision_colorHarmonization"].libs = ["libaliceVision_colorHarmonization"]
    #     self.cpp_info.components["libaliceVision_colorHarmonization"].requires = ["libaliceVision_feature", 
    #                                                                  "libaliceVision_image",
    #                                                                  "libaliceVision_linearProgramming",
    #                                                                  "libaliceVision_matching",
    #                                                                  ]

    #     self.cpp_info.components["libaliceVision_dataio"].libs = ["libaliceVision_dataio"]
    #     self.cpp_info.components["libaliceVision_dataio"].requires = ["libaliceVision_camera", 
    #                                                                  "libaliceVision_image",
    #                                                                  "libaliceVision_sfmData",
    #                                                                  "libaliceVision_sfmDataIO",
    #                                                                  "libaliceVision_system",
    #                                                                  "boost::boost"
    #                                                                  ]        
        
    #     if self.options.with_mvs:
    #         if self.options.with_cuda:
    #             self.cpp_info.components["libaliceVision_depthMap"].libs = ["libaliceVision_depthMap"]
    #             self.cpp_info.components["libaliceVision_depthMap"].requires = ["libaliceVision_mvsData", 
    #                                                                     "libaliceVision_mvsUtils",
    #                                                                     "libaliceVision_system",
    #                                                                     # TODO: add cuda dependencies:
    #                                                                     # ${CUDA_CUDADEVRT_LIBRARY}
    #                                                                     # ${CUDA_CUBLAS_LIBRARIES} #TODO shouldn't be here, but required to build on some machines
    #                                                                     "libaliceVision_gpu",
    #                                                                     "libaliceVision_sfmData",
    #                                                                     "libaliceVision_sfmDataIO",
    #                                                                     "assimp::assimp"
    #                                                                     ]
                    
    
    
    

    #         # if self.options.with_onnx:
        
        
    #     self.cpp_info.components["libaliceVision_feature"].libs = ["libaliceVision_feature"]
    #     self.cpp_info.components["libaliceVision_feature"].requires = ["aliceVision_image", 
    #                                                                  "aliceVision_numeric",
    #                                                                  "aliceVision_system",
    #                                                                  "aliceVision_gpu",
    #                                                                  "vlsift",
    #                                                                  "boost::boost"
    #                                                                  ]      
    #     if self.options.with_cctag:
    #         self.cpp_info.components["libaliceVision_feature"].requires.append("cctag:cctag")
    #     if self.options.with_apriltag:
    #         self.cpp_info.components["libaliceVision_feature"].requires.append("apriltag::apriltag")
    #     if self.options.with_popsift:
    #         self.cpp_info.components["libaliceVision_feature"].requires.append("popsift::popsift")
    #     if self.options.with_opencv:
    #         self.cpp_info.components["libaliceVision_feature"].requires.append(["opencv::opencv_core", 
    #                                                                             "opencv::opencv_imgproc",
    #                                                                             "opencv::opencv_video",
    #                                                                             "opencv::opencv_imgcodecs",
    #                                                                             "opencv::opencv_videoio",
    #                                                                             "opencv::opencv_features2d",
    #                                                                             "opencv::opencv_xfeatures2d"])
        
    #     self.cpp_info.components["libaliceVision_featureEngine"].libs = ["libaliceVision_featureEngine"]
    #     self.cpp_info.components["libaliceVision_featureEngine"].requires = ["libaliceVision_feature", 
    #                                                                  "libaliceVision_image",
    #                                                                  "libaliceVision_sfmData",
    #                                                                  "libaliceVision_system",
    #                                                                  ]      
        
    #     self.cpp_info.components["libaliceVision_geometry"].libs = ["libaliceVision_geometry"]
    #     self.cpp_info.components["libaliceVision_geometry"].requires = ["libaliceVision_numeric", 
    #                                                                  "libaliceVision_linearProgramming",
    #                                                                  ]
        
    #     if self.options.with_opencv:
    #         self.cpp_info.components["aliceVision_imageMasking"].libs = ["aliceVision_imageMasking"]
    #         self.cpp_info.components["aliceVision_imageMasking"].requires = ["aliceVision_image",
    #                                                                             "opencv::opencv_core", 
    #                                                                             "opencv::opencv_imgproc",
    #                                                                             "opencv::opencv_video",
    #                                                                             "opencv::opencv_imgcodecs",
    #                                                                             "opencv::opencv_videoio",
    #                                                                             "opencv::opencv_features2d",
    #                                                                             "opencv::opencv_xfeatures2d",
    #                                                                             # TODO: add Boost_PROGRAM_OPTIONS_LIBRARY
    #                                                                             ]

    #         self.cpp_info.components["aliceVision_keyframe"].libs = ["aliceVision_keyframe"]
    #         self.cpp_info.components["aliceVision_keyframe"].requires = ["libaliceVision_dataio",
    #                                                                      "libaliceVision_sfmData",
    #                                                                      "libaliceVision_sfmDataIO",
    #                                                                      "libaliceVision_sensorDB",
    #                                                                      "libaliceVision_system",
    #                                                                      "openimageio::openimageio"
    #                                                                             "opencv::opencv_core", 
    #                                                                             "opencv::opencv_imgproc",
    #                                                                             "opencv::opencv_video",
    #                                                                             "opencv::opencv_imgcodecs",
    #                                                                             "opencv::opencv_videoio",
    #                                                                             "opencv::opencv_features2d",
    #                                                                             "opencv::opencv_xfeatures2d",
    #                                                                             # TODO: add Boost_PROGRAM_OPTIONS_LIBRARY
    #                                                                             ]
            
    #     self.cpp_info.components["libaliceVision_imageMatching"].libs = ["libaliceVision_imageMatching"]
    #     self.cpp_info.components["aliceVision_keyframe"].requires = ["libaliceVision_image", "libaliceVision_voctree"]

    #     self.cpp_info.components["libaliceVision_lensCorrectionProfile"].libs = ["libaliceVision_lensCorrectionProfile"]
    #     self.cpp_info.components["libaliceVision_lensCorrectionProfile"].requires = ["boost::log", "expat::expat"]

    #     self.cpp_info.components["libaliceVision_localization"].libs = [""]
    #     self.cpp_info.components["libaliceVision_matching"].libs = [""]
    #     self.cpp_info.components["libaliceVision_kvld"].libs = [""]
    #     self.cpp_info.components["libaliceVision_matchingImageCollection"].libs = [""]
    #     self.cpp_info.components["libaliceVision_multiview"].libs = [""]
    #     self.cpp_info.components["libaliceVision_multiview_test_data"].libs = [""]
    #     self.cpp_info.components["libaliceVision_rig"].libs = [""]
    #     self.cpp_info.components["libaliceVision_robustEstimation"].libs = [""]
    #     self.cpp_info.components["libaliceVision_se"].libs = [""]
    #     self.cpp_info.components["libaliceVision_sfm"].libs = [""]
    #     self.cpp_info.components["libaliceVision_sfmData"].libs = [""]
    #     self.cpp_info.components["libaliceVision_sfmDataIO"].libs = [""]
    #     self.cpp_info.components["libaliceVision_track"].libs = [""]
    #     self.cpp_info.components["libaliceVision_voctree"].libs = [""]
        
    #     self.cpp_info.components["libaliceVision_calibration"].libs = ["libaliceVision_calibration"]
    #     # TODO: understand why ldd give differents result as we see in alicevision_add_library/target_link_libraries
    #     self.cpp_info.components["libaliceVision_calibration"].requires = ["libaliceVision_dataio", 
    #                                                                  "libaliceVision_image",
    #                                                                  "libaliceVision_system",
    #                                                                  "libvlsift",
    #                                                                  "libaliceVision_sensorDB",
    #                                                                  "boost::program_options",
    #                                                                  "boost::boost",
    #                                                                  "boost::json"
    #                                                                 #  TODO: add CERES_LIBRARIES

    #                                                                  ]
    #     if self.options.with_opencv:
    #       self.cpp_info.components["libaliceVision_calibration"].requires.append(["opencv::opencv_core",
    #                                                                               "opencv::opencv_imgproc",
    #                                                                               "opencv::opencv_video",
    #                                                                               "opencv::opencv_imgcodecs",
    #                                                                               "opencv::opencv_videoio",
    #                                                                               "opencv::opencv_features2d",
    #                                                                               "opencv::opencv_xfeatures2d",
    #                                                                               ])
            
    #     if self.options.with_cctag:
    #       self.cpp_info.components["libaliceVision_calibration"].requires.append("cctag")

        
    #     self.cpp_info.components["libaliceVision_panorama"].libs = [""]
        
    #     self.cpp_info.components["libaliceVision_hdr"].libs = ["libaliceVision_hdr"]
    #     self.cpp_info.components["libaliceVision_hdr"].requires = ["libaliceVision_system",
    #                                                                               "libaliceVision_image",
    #                                                                               "libaliceVision_sfmData",
    #                                                                             #   TODO: add CERES_LIBRARIES
    #                                                                               ]
        
    #     self.cpp_info.components["libaliceVision_lightingEstimation"].libs = ["libaliceVision_lightingEstimation"]
    #     self.cpp_info.components["libaliceVision_lightingEstimation"].requires = ["libaliceVision_numeric", "libaliceVision_system", "coin-clp::coin-clp", "coin-utils::coin-utils", "coin-osi::coin-osi"]
    #     # TODO: add MOSEK_LIB, Coin::OsiMsk and 
        
    #     self.cpp_info.components["aliceVision_linearProgramming"].libs = ["aliceVision_linearProgramming"]
    #     self.cpp_info.components["aliceVision_linearProgramming"].requires = ["libaliceVision_image", "libaliceVision_system"]
        
    #     self.cpp_info.components["libaliceVision_lInftyComputerVision"].libs = ["libaliceVision_lInftyComputerVision"]
    #     self.cpp_info.components["libaliceVision_lInftyComputerVision"].requires = ["aliceVision_linearProgramming"]
    #     # if self.options.with_mosek:
    #     #     # TODO: add mosek_libs
    #     #     self.cpp_info.components["libaliceVision_lInftyComputerVision"].requires.appends("")
        
    #     self.cpp_info.components["libaliceVision_mesh"].libs = [""]
    #     self.cpp_info.components["libaliceVision_mvsData"].libs = [""]
    #     self.cpp_info.components["libaliceVision_mvsUtils"].libs = [""]
        
    #     self.cpp_info.components["libaliceVision_fuseCut"].libs = ["libaliceVision_fuseCut"]
    #     self.cpp_info.components["libaliceVision_fuseCut"].requires = ["libaliceVision_mvsData", 
    #                                                             "libaliceVision_mvsUtils",
    #                                                             "libaliceVision_mesh",
    #                                                             "libaliceVision_sfmData",
    #                                                             "libaliceVision_system",
    #                                                             "geogram::geogram",
    #                                                             "boost::graph",
    #                                                             "boost::container",
    #                                                             "nanoflann::nanoflann",
    #                                                             "boost::boost"
    #                                                             ]
        
    #     self.cpp_info.components["libaliceVision_sfmMvsUtils"].libs = [""]

    def deploy(self):
        copy(self, "lib/*", src=self.package_folder, dst=self.deploy_folder)
        copy(self, "bin/*", src=self.package_folder, dst=self.deploy_folder)
