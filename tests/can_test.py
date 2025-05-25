import can

# channel names are PCAN_USBBUS1, PCAN_USBBUS2, etc.
# match the device ID shown in PCAN-View (e.g. "PCAN-USBBUSFD")
bus = can.Bus(
    interface='gs_usb',  # or 'pcan' for PCAN-USB
    channel=0,
    bitrate=250000,    # kbit/s, same as your DB entry
    fd=False           # set True for CAN-FD frames
)

print("Listening for CAN messages…")
try:
    for msg in bus:
        print(f"{msg.timestamp:.6f}  ID=0x{msg.arbitration_id:X}  "
              f"Rtr={msg.is_remote_frame}  DLC={msg.dlc}  Data={msg.data.hex()}")
except KeyboardInterrupt:
    print("Shutting down…")
finally:
    bus.shutdown()
