#pragma once

#include <string> // std::string

namespace ngk { namespace version {

   ///< Helper function for `version_client()`
   std::string _version_client();

   ///< Helper function for `version_full()`
   std::string _version_full();

} }
