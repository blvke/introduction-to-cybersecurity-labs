; # Simple Programm to exit
; # with a defined state
; #
; # Compile using nasm:
; # nasm -f elf32 exit.asm
; # ld -m elf_i386 -o exiter exit.o 
; #
; # Generate Shellcode using Hexdump
; # objdump -d exiter
; ##################################

global _start			;  define entry point

section .text			; begin of .text section
_start:					; entry point
   xor eax, eax			; Zero out eax, avoid Nullbytes
   mov al, 1			; set eax to $1 (exit Interuppt)
   xor ebx, ebx			; zero out ebx for exit Code NULL
   int 0x80				; execute Interupt

; end of exit.asm
