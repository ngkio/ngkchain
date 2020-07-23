# ##################################################################################################
# Create the ngk-vm interpreter driver.
# ##################################################################################################
add_executable(ngk-vm-interp ${CMAKE_CURRENT_SOURCE_DIR}/interp.cpp)
target_link_libraries(ngk-vm-interp ngk-vm)

add_executable(bench-interp ${CMAKE_CURRENT_SOURCE_DIR}/bench_interp.cpp)
target_link_libraries(bench-interp ngk-vm)

add_executable(hello-driver ${CMAKE_CURRENT_SOURCE_DIR}/hello_driver.cpp)
target_link_libraries(hello-driver ngk-vm)
