# Set compiler flags
CCC     := gcc
CFLAGS  := -m32 -fno-stack-protector -z execstack -U_FORTIFY_SOURCE -fno-pie -no-pie -Wl,-z,norelro $(EXTRAFLAGS)
LDFLAGS := -Wl,-z-norelro -lstdc++

# Define build target
TARGET = timeservice
# Where to save output to
TO = ./

all: $(TARGET)
all-debug:
	make all EXTRAFLAGS=-g

$(TARGET): $(TARGET).c
	mkdir -p $(TO)
	$(CC) $(CFLAGS) -o $(TO)$(TARGET) $(TARGET).c

clean:
	-rm $(TO)$(TARGET)
