#include <ngk/chain/webassembly/ngk-vm-oc.hpp>
#include <ngk/chain/wasm_ngk_constraints.hpp>
#include <ngk/chain/wasm_ngk_injection.hpp>
#include <ngk/chain/apply_context.hpp>
#include <ngk/chain/exceptions.hpp>

#include <vector>
#include <iterator>

namespace ngk { namespace chain { namespace webassembly { namespace ngkvmoc {

class ngkvmoc_instantiated_module : public wasm_instantiated_module_interface {
   public:
      ngkvmoc_instantiated_module(const digest_type& code_hash, const uint8_t& vm_version, ngkvmoc_runtime& wr) :
         _code_hash(code_hash),
         _vm_version(vm_version),
         _ngkvmoc_runtime(wr)
      {

      }

      ~ngkvmoc_instantiated_module() {
         _ngkvmoc_runtime.cc.free_code(_code_hash, _vm_version);
      }

      void apply(apply_context& context) override {
         const code_descriptor* const cd = _ngkvmoc_runtime.cc.get_descriptor_for_code_sync(_code_hash, _vm_version);
         NGK_ASSERT(cd, wasm_execution_error, "NGK VM OC instantiation failed");

         _ngkvmoc_runtime.exec.execute(*cd, _ngkvmoc_runtime.mem, context);
      }

      const digest_type              _code_hash;
      const uint8_t                  _vm_version;
      ngkvmoc_runtime&               _ngkvmoc_runtime;
};

ngkvmoc_runtime::ngkvmoc_runtime(const boost::filesystem::path data_dir, const ngkvmoc::config& ngkvmoc_config, const chainbase::database& db)
   : cc(data_dir, ngkvmoc_config, db), exec(cc) {
}

ngkvmoc_runtime::~ngkvmoc_runtime() {
}

std::unique_ptr<wasm_instantiated_module_interface> ngkvmoc_runtime::instantiate_module(const char* code_bytes, size_t code_size, std::vector<uint8_t> initial_memory,
                                                                                     const digest_type& code_hash, const uint8_t& vm_type, const uint8_t& vm_version) {

   return std::make_unique<ngkvmoc_instantiated_module>(code_hash, vm_type, *this);
}

//never called. NGK VM OC overrides ngk_exit to its own implementation
void ngkvmoc_runtime::immediately_exit_currently_running_module() {}

}}}}
