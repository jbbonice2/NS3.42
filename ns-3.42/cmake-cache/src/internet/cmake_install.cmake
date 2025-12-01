# Install script for directory: /nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet

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
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib64/libns3.42-internet-default.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib64/libns3.42-internet-default.so")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib64/libns3.42-internet-default.so"
         RPATH "/usr/local/lib:$ORIGIN/:$ORIGIN/../lib:/usr/local/lib64:$ORIGIN/:$ORIGIN/../lib64")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib64" TYPE SHARED_LIBRARY FILES "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/build/lib64/libns3.42-internet-default.so")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib64/libns3.42-internet-default.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib64/libns3.42-internet-default.so")
    file(RPATH_CHANGE
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib64/libns3.42-internet-default.so"
         OLD_RPATH "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/build/lib64::::::"
         NEW_RPATH "/usr/local/lib:$ORIGIN/:$ORIGIN/../lib:/usr/local/lib64:$ORIGIN/:$ORIGIN/../lib64")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib64/libns3.42-internet-default.so")
    endif()
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/ns3" TYPE FILE FILES
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/helper/internet-stack-helper.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/helper/internet-trace-helper.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/helper/ipv4-address-helper.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/helper/ipv4-global-routing-helper.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/helper/ipv4-interface-container.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/helper/ipv4-list-routing-helper.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/helper/ipv4-routing-helper.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/helper/ipv4-static-routing-helper.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/helper/ipv6-address-helper.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/helper/ipv6-interface-container.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/helper/ipv6-list-routing-helper.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/helper/ipv6-routing-helper.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/helper/ipv6-static-routing-helper.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/helper/neighbor-cache-helper.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/helper/rip-helper.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/helper/ripng-helper.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/arp-cache.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/arp-header.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/arp-l3-protocol.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/arp-queue-disc-item.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/candidate-queue.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/global-route-manager-impl.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/global-route-manager.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/global-router-interface.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/icmpv4-l4-protocol.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/icmpv4.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/icmpv6-header.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/icmpv6-l4-protocol.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ip-l4-protocol.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv4-address-generator.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv4-end-point-demux.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv4-end-point.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv4-global-routing.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv4-header.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv4-interface-address.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv4-interface.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv4-l3-protocol.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv4-list-routing.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv4-packet-filter.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv4-packet-info-tag.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv4-packet-probe.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv4-queue-disc-item.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv4-raw-socket-factory.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv4-raw-socket-impl.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv4-route.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv4-routing-protocol.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv4-routing-table-entry.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv4-static-routing.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv4.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-address-generator.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-end-point-demux.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-end-point.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-extension-demux.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-extension-header.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-extension.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-header.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-interface-address.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-interface.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-l3-protocol.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-list-routing.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-option-header.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-option.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-packet-filter.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-packet-info-tag.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-packet-probe.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-pmtu-cache.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-queue-disc-item.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-raw-socket-factory.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-route.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-routing-protocol.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-routing-table-entry.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6-static-routing.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ipv6.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/loopback-net-device.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ndisc-cache.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/rip-header.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/rip.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ripng-header.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/ripng.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/rtt-estimator.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-bbr.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-bic.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-congestion-ops.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-cubic.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-dctcp.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-header.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-highspeed.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-htcp.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-hybla.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-illinois.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-l4-protocol.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-ledbat.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-linux-reno.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-lp.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-option-rfc793.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-option-sack-permitted.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-option-sack.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-option-ts.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-option-winscale.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-option.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-prr-recovery.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-rate-ops.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-recovery-ops.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-rx-buffer.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-scalable.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-socket-base.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-socket-factory.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-socket-state.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-socket.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-tx-buffer.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-tx-item.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-vegas.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-veno.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-westwood-plus.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/tcp-yeah.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/udp-header.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/udp-l4-protocol.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/udp-socket-factory.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/udp-socket.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/src/internet/model/windowed-filter.h"
    "/nfs/home/jeanpetityvelosb/project/python/Bonice/NS3.42/ns-3.42/build/include/ns3/internet-module.h"
    )
endif()

