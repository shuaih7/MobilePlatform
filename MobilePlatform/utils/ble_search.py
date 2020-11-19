import os, sys
import asyncio
from bleak import discover


async def search():
    devices = await discover()
    for dev in devices:
        print(dev)
        
        
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(search())