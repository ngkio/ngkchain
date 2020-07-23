#pragma once

namespace ngk { namespace vm {

// create constexpr flags for whether the backend should obey alignment hints
#ifdef NGK_VM_ALIGN_MEMORY_OPS
   inline constexpr bool should_align_memory_ops = true;
#else
   inline constexpr bool should_align_memory_ops = false;
#endif


#ifdef NGK_VM_SOFTFLOAT
   inline constexpr bool use_softfloat = true;
#else
   inline constexpr bool use_softfloat = false;
#endif

#ifdef NGK_VM_FULL_DEBUG
   inline constexpr bool ngk_vm_debug = true;
#else
   inline constexpr bool ngk_vm_debug = false;
#endif

}} // namespace ngk::vm
