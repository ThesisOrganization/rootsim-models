CC = gcc
CFLAGS = -Wall
SRCS = queue_quick_sort.c priority_scheduler.c ../priority_queue/heap/heap.c ../priority_queue/priority_queue.c scheduling_algorithms.c
OBJS = $(SRCS:.c=.o)
HEADERS = $(SRCS:.c=.h)
MAIN = driver

all:    $(MAIN)


$(MAIN): $(OBJS) $(MAIN).c
	$(CC) $(CFLAGS) -o $(MAIN) $(MAIN).c $(OBJS)

%.o: %.c %.h
	gcc -ggdb -c $(CFLAGS) $*.c -o $*.o

clean:
	$(RM) $(SRCS:.c=.o) $(MAIN)
