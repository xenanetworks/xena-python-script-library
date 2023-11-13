import asyncio
from contextlib import suppress
from xoa_driver import (
    testers,
    modules,
    ports,
    enums,
    utils,
    exceptions
)
from xoa_driver.hlfuncs import (
    mgmt,
    cli
)

CHASSIS_IP = "10.20.1.166"
USERNAME = "xoa"
MODULE_IDX = 8
PORT_IDX = 0

async def my_awesome_func(stop_event: asyncio.Event):
    # create tester instance and establish connection
    async with testers.L23Tester(host=CHASSIS_IP, username=USERNAME, password="xena", port=22606, enable_logging=False) as tester:
        
        #########################################
        #       Use Tester Config File          #
        #########################################

        await mgmt.free_tester(tester=tester, should_free_modules_ports=True)
        await mgmt.reserve_tester(tester=tester)

        # Configure module with .xtc2 file's module config part
        await cli.tester_config_from_file(tester=tester, path="tester_config.txt")

        # Alternatively, you can also configure tester with CLI commands
        await cli.tester_config_from_string(
            tester=tester,
            long_str="""
            C_COMMENT \"This is a comment\"
            """)

        # Release the tester
        await mgmt.free_tester(tester)

        #########################################
        #       Use Module Config File          #
        #########################################
        # access module 0 on the tester
        module = tester.modules.obtain(MODULE_IDX)
        await mgmt.free_module(module=module, should_free_ports=True)
        await mgmt.reserve_module(module=module)

        # Configure module with .xtc2 file's module config part
        await cli.module_config_from_file(module=module, path="module_config.xtc2")

        # Alternatively, you can also configure module with CLI commands
        await cli.module_config_from_string(
            module=module,
            long_str="""
            M_MEDIA  QSFP28
            M_CFPCONFIGEXT  8 25000 25000 25000 25000 25000 25000 25000 25000
            M_COMMENT \"This is a comment\"
            """)
        
        # Release the module
        await mgmt.free_module(module)

        if isinstance(module, modules.ModuleChimera):
            return None
        
        #######################################
        #       Use Port Config File          #
        #######################################
        # access port 0 on the module as the TX port
        port = module.ports.obtain(PORT_IDX)
        await mgmt.reserve_port(port=port)

        # Configure port with .xpc file generated by ValkyrieManager
        await cli.port_config_from_file(port=port, path="port_config.xpc")

        # Alternatively, you can also configure port with CLI commands
        await cli.port_config_from_string(
            port=port,
            long_str="""
            P_RESET
            P_COMMENT \"This is a comment\"
            P_MACADDRESS  0xAAAAAABBBB99
            P_IPADDRESS  1.1.1.1 0.0.0.0 0.0.0.0 0.0.0.0
            """)
        
        # Release the port
        await mgmt.free_port(port)
        

async def main():
    stop_event = asyncio.Event()
    try:
        await my_awesome_func(stop_event)
    except KeyboardInterrupt:
        stop_event.set()


if __name__ == "__main__":
    asyncio.run(main())