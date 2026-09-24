import sys
import os
import sqlite3

# Ensure local imports work
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from sdk import (GraphContext, Function, Variable, Call, 
                 Condition, Import, ClassNode, Loop, TryCatch,
                 Return, BinaryOp, Comparison, Enum, Identifier)

DB_PATH = os.path.join(os.getcwd(), "agy_nodeos.db")

def create_advanced_module():
    with GraphContext("AuthModuleV2") as ctx:
        # Imports
        ctx.add_node(Import("crypto_lib", ["verify_hash", "generate_salt"]))
        ctx.add_node(Import("enum", ["Enum"]))
        
        # Enum for Roles
        ctx.add_node(Enum("UserRole", ["ADMIN", "USER", "GUEST"]))
        
        # Base class
        base = ClassNode("BaseAuth")
        ctx.add_node(base)
        
        base_init = Function("__init__", ["self"])
        base_init.add_statement(Variable("self.is_authenticated", raw_value=False))
        base.add_method(base_init)
        
        # OAuth class
        oauth = ClassNode("OAuth", inherits="BaseAuth")
        ctx.add_node(oauth)
        
        oauth_init = Function("__init__", ["self", "provider"])
        oauth_init.add_statement(Call("super().__init__", []))
        oauth_init.add_statement(Variable("self.provider", Identifier("provider")))
        oauth.add_method(oauth_init)
        
        auth_method = Function("authenticate", ["self", "credentials"])
        oauth.add_method(auth_method)
        
        # A loop 
        auth_loop = Loop("for", "cred in credentials")
        auth_method.add_statement(auth_loop)
        
        # Inside loop: TryCatch
        tc = TryCatch("Exception", "e")
        auth_loop.add_statement(tc)
        
        # Inside try: Comparison and Calls
        is_valid = Variable("is_valid", Call("verify_hash", ["cred.password", "cred.hash"]))
        tc.try_block.add_statement(is_valid)
        
        cond = Condition(
            check=Identifier("is_valid"),
            on_true=Call("self.grant_access", ["cred.user_id"]),
            on_false=Call("self.reject_access", ["cred.user_id"])
        )
        tc.try_block.add_statement(cond)
        
        tc.try_block.add_statement(Return(Identifier("is_valid")))
        
        # Inside catch
        tc.catch_block.add_statement(Call("print", ["f'Auth failed: {e}'"]))
        tc.catch_block.add_statement(Return(Identifier("False")))

if __name__ == "__main__":
    print(f"Creating AuthModuleV2 in {DB_PATH}...")
    create_advanced_module()
    print("Done!")
