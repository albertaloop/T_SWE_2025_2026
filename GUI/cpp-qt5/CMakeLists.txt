cmake_minimum_required(VERSION 3.1)

project(abloop_gui VERSION 2.0 LANGUAGES CXX)


set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_INCLUDE_CURRENT_DIR ON)


set(CMAKE_MESSAGE_LOG_LEVEL "DEBUG")

set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)


find_package(Qt5 REQUIRED COMPONENTS Widgets Core Gui)

#checks if the compiler ID matches "GNU" (for GCC) or contains "Clang" (for both Clang and AppleClang).
if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU" OR
   "${CMAKE_CXX_COMPILER_ID}" MATCHES "Clang")
  add_compile_options(-g)
  message("added compile option -g")
endif()


set(PROJECT_SOURCES
	main.cpp
	CircularBuffer.cpp
	SocketComms.cpp
	MainWindow.cpp
	PodNetWidget.cpp
	Commands.cpp
)

# replaces add_executable so that AUTORCC can add resources file
# qt_add_executable(abloop_gui
#     #resources.qrc
#     ${PROJECT_SOURCES}
# )

add_executable(abloop_gui
${PROJECT_SOURCES}

)


# Find Threads package
find_package(Threads REQUIRED)

# Link pthread
target_link_libraries(abloop_gui PRIVATE ${CMAKE_THREAD_LIBS_INIT})

target_link_libraries(
	abloop_gui
	PRIVATE
	Qt5::Widgets
	Qt5::Core
	Qt5::Gui
)


