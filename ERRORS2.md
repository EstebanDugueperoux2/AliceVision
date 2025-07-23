static build with gold linker:

/usr/bin/ld.gold: CMakeFiles/aliceVision_sfmBootstrapping_exe.dir/main_sfmBootstrapping.cpp.o: previous definition here
/usr/bin/ld.gold: error: ../../../Linux-x86_64/libaliceVision_sfm.a(PairsScoring.cpp.o): multiple definition of 'aliceVision::sfm::tag_invoke(boost::json::value_to_tag<aliceVision::sfm::ReconstructedPair>, boost::json::value const&)'
/usr/bin/ld.gold: CMakeFiles/aliceVision_sfmBootstrapping_exe.dir/main_sfmBootstrapping.cpp.o: previous definition here
collect2: error: ld returned 1 exit status

