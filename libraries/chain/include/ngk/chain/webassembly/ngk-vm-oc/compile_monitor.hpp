#pragma once

#include <ngk/chain/webassembly/ngk-vm-oc/config.hpp>

#include <boost/asio/local/datagram_protocol.hpp>
#include <ngk/chain/webassembly/ngk-vm-oc/ipc_helpers.hpp>

namespace ngk { namespace chain { namespace ngkvmoc {

wrapped_fd get_connection_to_compile_monitor(int cache_fd);

}}}