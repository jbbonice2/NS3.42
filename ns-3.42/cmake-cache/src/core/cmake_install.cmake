# Install script for directory: /nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "default")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "0")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set path to fallback-tool for dependency-resolution.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib64/libns3.42-core-default.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib64/libns3.42-core-default.so")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib64/libns3.42-core-default.so"
         RPATH "/usr/local/lib:$ORIGIN/:$ORIGIN/../lib:/usr/local/lib64:$ORIGIN/:$ORIGIN/../lib64")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib64" TYPE SHARED_LIBRARY FILES "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/build/lib64/libns3.42-core-default.so")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib64/libns3.42-core-default.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib64/libns3.42-core-default.so")
    file(RPATH_CHANGE
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib64/libns3.42-core-default.so"
         OLD_RPATH "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/build/lib64::::::"
         NEW_RPATH "/usr/local/lib:$ORIGIN/:$ORIGIN/../lib:/usr/local/lib64:$ORIGIN/:$ORIGIN/../lib64")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib64/libns3.42-core-default.so")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/ns3" TYPE FILE FILES
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/int64x64-128.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/helper/csv-reader.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/helper/event-garbage-collector.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/helper/random-variable-stream-helper.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/abort.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/ascii-file.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/ascii-test.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/assert.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/attribute-accessor-helper.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/attribute-construction-list.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/attribute-container.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/attribute-helper.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/attribute.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/boolean.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/breakpoint.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/build-profile.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/calendar-scheduler.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/callback.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/command-line.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/config.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/default-deleter.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/default-simulator-impl.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/deprecated.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/des-metrics.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/double.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/enum.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/event-id.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/event-impl.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/fatal-error.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/fatal-impl.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/fd-reader.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/environment-variable.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/global-value.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/hash-fnv.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/hash-function.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/hash-murmur3.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/hash.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/heap-scheduler.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/int64x64-double.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/int64x64.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/integer.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/length.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/list-scheduler.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/log-macros-disabled.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/log-macros-enabled.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/log.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/make-event.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/map-scheduler.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/math.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/names.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/node-printer.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/nstime.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/object-base.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/object-factory.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/object-map.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/object-ptr-container.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/object-vector.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/object.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/pair.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/pointer.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/priority-queue-scheduler.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/ptr.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/random-variable-stream.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/rng-seed-manager.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/rng-stream.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/scheduler.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/show-progress.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/shuffle.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/simple-ref-count.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/simulation-singleton.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/simulator-impl.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/simulator.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/singleton.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/string.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/synchronizer.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/system-path.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/system-wall-clock-ms.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/system-wall-clock-timestamp.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/test.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/time-printer.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/timer-impl.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/timer.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/trace-source-accessor.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/traced-callback.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/traced-value.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/trickle-timer.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/tuple.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/type-id.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/type-name.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/type-traits.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/uinteger.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/uniform-random-bit-generator.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/valgrind.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/vector.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/warnings.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/watchdog.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/realtime-simulator-impl.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/wall-clock-synchronizer.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/val-array.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/core/model/matrix-array.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/build/include/ns3/config-store-config.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/build/include/ns3/core-config.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/build/include/ns3/core-module.h"
    )
endif()

