cmake_minimum_required(VERSION 3.20)

add_executable(main_svgSample main.cpp)

set_property(TARGET main_svgSample
  PROPERTY FOLDER Dependencies/vectorGraphics
)