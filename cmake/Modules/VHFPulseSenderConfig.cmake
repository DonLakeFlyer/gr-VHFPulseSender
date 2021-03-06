INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_VHFPULSESENDER VHFPulseSender)

FIND_PATH(
    VHFPULSESENDER_INCLUDE_DIRS
    NAMES VHFPulseSender/api.h
    HINTS $ENV{VHFPULSESENDER_DIR}/include
        ${PC_VHFPULSESENDER_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    VHFPULSESENDER_LIBRARIES
    NAMES gnuradio-VHFPulseSender
    HINTS $ENV{VHFPULSESENDER_DIR}/lib
        ${PC_VHFPULSESENDER_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(VHFPULSESENDER DEFAULT_MSG VHFPULSESENDER_LIBRARIES VHFPULSESENDER_INCLUDE_DIRS)
MARK_AS_ADVANCED(VHFPULSESENDER_LIBRARIES VHFPULSESENDER_INCLUDE_DIRS)

