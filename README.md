# 🔀 ARP MitM Attack — Seguridad de Redes

<div align="center">

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Scapy](https://img.shields.io/badge/Scapy-Latest-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Linux-orange?style=for-the-badge&logo=linux)
![License](https://img.shields.io/badge/Uso-Educativo-red?style=for-the-badge)

**Sael Germán García** | Matrícula: `2025-0725`  
Asignatura: Seguridad de Redes | Profesor: Jonathan Rondón  
Instituto Tecnológico de las Américas — ITLA | 2026

</div>

---

## 📋 Descripción del Ataque

El **ARP Man-in-the-Middle Attack** explota la vulnerabilidad inherente del protocolo **ARP (Address Resolution Protocol)** ante ataques de suplantación de identidad. Mediante el envío de respuestas ARP maliciosas, el atacante envenena las cachés ARP de los dispositivos legítimos, posicionándose de forma transparente entre la víctima y su Gateway predeterminado para interceptar, analizar y reenviar el tráfico en tiempo real.

> 💡 **Prerrequisito:** El atacante debe encontrarse en el mismo dominio de difusión (VLAN) que la víctima. Para este laboratorio, el puerto del atacante (e0/3 en SW1) fue migrado desde VLAN 99 hacia VLAN 10.

---

## 🗺️ Topología de Red

### 📊 Segmentación de VLANs

| VLAN ID | Nombre | Segmento IP | Descripción |
|:-------:|:------:|:-----------:|-------------|
| 10 | Usuarios | 10.7.25.0/24 | Víctima (VPC1: 10.7.25.3) y Atacante (10.7.25.100) |
| 20 | Servidores | 10.7.20.0/24 | VPC2 — zona de servidores |
| 99 | Gestión | 10.7.99.0/24 | VLAN nativa — sin hosts activos durante el ataque |

### 📊 Matriz de Direccionamiento

| Elemento | Dirección IP | Dirección MAC | Detalle |
|:--------:|:------------:|:-------------:|---------|
| Víctima (VPC1) | 10.7.25.3 | Asignada por DHCP | Conectado a SW2 (e0/0) |
| Gateway Real (R1) | 10.7.25.1 | aa:bb:cc:00:01:00 | Subinterfaz R1 Eth0/0.10 |
| Atacante (Ubuntu) | 10.7.25.100 | 00:11:22:33:44:55 | Migrado a VLAN 10 en SW1 (e0/3) |
| Resultado MitM | — | 10.7.25.1 → 00:11:22:33:44:55 | VPC1 asocia el GW con la MAC del atacante |

---

## ⚙️ Requisitos

```bash
# Sistema Operativo
Ubuntu Linux (recomendado)

# Dependencias
sudo apt update && sudo apt install -y python3-scapy python3-pip

# Privilegios requeridos
sudo / root
```

---

## 🔧 Configuración Previa

### Migración de puerto en SW1
```cisco
SW1(config)# interface ethernet0/3
SW1(config-if)# switchport access vlan 10
SW1(config-if)# no shutdown
SW1(config-if)# end
SW1# write memory
```

### Ajuste de MAC e IP en el atacante
```bash
sudo ip link set ens4 down
sudo ip link set ens4 address 00:11:22:33:44:55
sudo ip link set ens4 up
sudo ip addr add 10.7.25.100/24 dev ens4
sudo ip route add default via 10.7.25.1 dev ens4
```

---

## 🚀 Uso

```bash
# Ejecutar el ataque
sudo python3 arp_mitm.py

# Verificar envenenamiento en VPC1
show arp

# Capturar tráfico interceptado
sudo tcpdump -i ens4 -n host 10.7.25.3
```

---

## 🔬 ¿Cómo funciona?

| Paso | Descripción |
|:----:|-------------|
| 1️⃣ | Habilita IP Forwarding para reenviar tráfico interceptado sin cortar el servicio |
| 2️⃣ | Resuelve la MAC real de la víctima (VPC1) y del Gateway (R1) |
| 3️⃣ | Lanza un hilo en segundo plano para capturar tráfico en tiempo real |
| 4️⃣ | Envía ARP Reply falso a VPC1: *"El Gateway soy yo (00:11:22:33:44:55)"* |
| 5️⃣ | Envía ARP Reply falso a R1: *"VPC1 soy yo (00:11:22:33:44:55)"* |
| 6️⃣ | Al detener con Ctrl+C restaura automáticamente las tablas ARP originales |

---

## 🛡️ Contramedidas

### 1. Habilitar DHCP Snooping (prerrequisito)
```cisco
SW1(config)# ip dhcp snooping
SW1(config)# ip dhcp snooping vlan 10
```

### 2. Habilitar Dynamic ARP Inspection (DAI)
```cisco
SW1(config)# ip arp inspection vlan 10
```

### 3. Configurar puerto confiable hacia R1
```cisco
SW1(config)# interface ethernet0/0
SW1(config-if)# ip arp inspection trust
SW1(config-if)# exit
```

---

## 📁 Archivos del Repositorio

| Archivo | Descripción |
|:-------:|-------------|
| [`arp_mitm.py`](arp_mitm.py) | Script principal del ataque |
| [`SaelGermanGarcia_2025-0725_MitM_ARP_P1.pdf`](SaelGermanGarcia_2025-0725_MitM_ARP_P1.pdf) | Documentación técnica completa |

---

## 🖼️ Capturas de Pantalla

- 📸 [Estado Inicial de la Tabla ARP en la Víctima](Capturas%20de%20Pantalla%20MitM%20ARP/Estado%20Inicial%20de%20la%20Tabla%20ARP%20en%20la%20V%C3%ADctima%20.png)
- 📸 [Inicialización del Script de Envenenamiento ARP](Capturas%20de%20Pantalla%20MitM%20ARP/Inicializaci%C3%B3n%20del%20Script%20de%20Envenenamiento%20ARP.png)
- 📸 [Ejecución Activa del Ataque Man-in-the-Middle](Capturas%20de%20Pantalla%20MitM%20ARP/Ejecuci%C3%B3n%20Activa%20del%20Ataque%20Man-in-the-Middle.png)
- 📸 [Tabla ARP Comprometida — Ataque Exitoso](Capturas%20de%20Pantalla%20MitM%20ARP/Tabla%20ARP%20Comprometida%20%28Ataque%20Exitoso%29.png)
- 📸 [Contramedida Aplicada](Capturas%20de%20Pantalla%20MitM%20ARP/contramedidaa.png)

---

## 📎 Recursos

📄 **Documentación Técnica:** [Ver Informe PDF](SaelGermanGarcia_2025-0725_MitM_ARP_P1.pdf)  
▶️ **Video Demostración:** [Ver en YouTube](https://youtube.com/playlist?list=PLV_dKVnYXf6dpmk3j8uXPHAZdbrkCQGAY)

---

## 📚 Referencias

1. Cisco Systems. *Dynamic ARP Inspection Configuration Guide*. Documentación oficial de Cisco IOS.
2. Scapy Project. *Scapy: Interactive packet manipulation program*. [https://scapy.net/](https://scapy.net/)
3. IETF. *RFC 826: An Ethernet Address Resolution Protocol*. Especificación base del protocolo ARP.
4. Reconocimiento especial: Troubleshooting , script base y documentación apoyado en Inteligencia Artificial.

---

<div align="center">

⚠️ **AVISO LEGAL** ⚠️  
*Este script fue desarrollado exclusivamente con fines académicos y educativos.*  
*Su uso en redes sin autorización explícita es ilegal y éticamente inaceptable.*

</div>
