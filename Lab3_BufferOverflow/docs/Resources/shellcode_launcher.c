// shellcode_launcher.c
// Simple program to test the generated Shellcode
//
// Compiler gcc-3-4
//
// Compile using:
// gcc -m32 -g -fno-stack-protector -z execstack shellcode_launcher.c -o shellcode_launcher
//
// #####################################################################


int main()
{
	// Shellcode for basic exit function
	// Replace with the Shellcode you want to validate
	char sc[] = "\x31\xc0\xb0\x01\x31\xdb\xcd\x80";

	// execute shellcode
	int (*ret)() = (int (*)())sc;
	ret();
}
