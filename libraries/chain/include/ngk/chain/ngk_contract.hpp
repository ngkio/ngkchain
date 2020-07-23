#pragma once

#include <ngk/chain/types.hpp>
#include <ngk/chain/contract_types.hpp>

namespace ngk { namespace chain {

   class apply_context;

   /**
    * @defgroup native_action_handlers Native Action Handlers
    */
   ///@{
   void apply_ngk_newaccount(apply_context&);
   void apply_ngk_updateauth(apply_context&);
   void apply_ngk_deleteauth(apply_context&);
   void apply_ngk_linkauth(apply_context&);
   void apply_ngk_unlinkauth(apply_context&);

   /*
   void apply_ngk_postrecovery(apply_context&);
   void apply_ngk_passrecovery(apply_context&);
   void apply_ngk_vetorecovery(apply_context&);
   */

   void apply_ngk_setcode(apply_context&);
   void apply_ngk_setabi(apply_context&);

   void apply_ngk_canceldelay(apply_context&);
   ///@}  end action handlers

} } /// namespace ngk::chain
