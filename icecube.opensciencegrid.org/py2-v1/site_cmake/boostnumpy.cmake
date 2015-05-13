set(BOOSTNUMPY_LIBRARIES "$ENV{SROOT}/lib/libboost_numpy.so" CACHE FILEPATH "boost::numpy library")
set(BOOSTNUMPY_INCLUDE_DIR "$ENV{SROOT}/include" CACHE PATH "Path to boost::numpy include dir")
set(BOOSTNUMPY_FOUND TRUE CACHE BOOL "boost::numpy found")

# boost::numpy can't work without the Numpy C API
LIST(APPEND BOOSTNUMPY_INCLUDE_DIR ${NUMPY_INCLUDE_DIR})
LIST(APPEND BOOSTNUMPY_LIBRARIES ${NUMPY_LIBRARIES})

