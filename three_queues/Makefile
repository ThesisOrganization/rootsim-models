CC = ../Simulator/bin/rootsim-cc
CFLAGS = -Wall -Wextra
TARGET = queues

SRCS = application.c
OBJS = $(SRCS:.c=.o)

.PHONY: clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJS)

.c.o:
	$(CC) $(CFLAGS) $(INCLUDES) -c $<  -o $@

clean:
	$(RM) *.o *.o.rs $(TARGET)
