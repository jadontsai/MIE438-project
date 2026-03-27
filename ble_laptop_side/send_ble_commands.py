import asyncio
from bleak import BleakScanner, BleakClient

DEVICE_NAME = "some_name"
CHAR_UUID = "67676767-6767-6767-6767-676767676ABC"

def clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))

def build_packet(steer: int, speed: int, catch: int) -> bytes:
    steer = clamp(steer, -100, 100)
    speed = clamp(speed, 0, 100)
    catch = 1 if catch else 0
    return f"{steer},{speed},{catch}\n".encode("utf-8")

async def find_device_by_name(name: str):
    devices = await BleakScanner.discover(timeout=5.0)
    for d in devices:
        if d.name == name:
            return d
    return None

async def main():
    target = await find_device_by_name(DEVICE_NAME)
    if target is None:
        print(f"Device '{DEVICE_NAME}' not found.")
        return

    print(f"Found {target.name} at {target.address}")

    async with BleakClient(target) as client:
        print("Connected")

        test_commands = [
            (0, 0, 0),
            (-30, 40, 0),
            (30, 40, 0),
            (0, 60, 0),
            (0, 0, 1),
            (0, 0, 0),
        ]

        for steer, speed, catch in test_commands:
            payload = build_packet(steer, speed, catch)
            print("Sending:", payload)
            await client.write_gatt_char(CHAR_UUID, payload, response=False)
            await asyncio.sleep(1.0)

        print("Done")

if __name__ == "__main__":
    asyncio.run(main())
