CC = gcc
CFLAGS = -pthread
LDFLAGS = -lm
OBJS = spend_time.o ex1.o
EXEC = ex1

# regra default
all: build

# regra de compilação
build: $(OBJS)
	$(CC) $(CFLAGS) -o $(EXEC) $(OBJS) $(LDFLAGS)

spend_time.o: spend_time.c spend_time.h
	$(CC) $(CFLAGS) -c spend_time.c $(LDFLAGS)

ex1.o: ex1.c spend_time.h
	$(CC) $(CFLAGS) -c ex1.c

# regra para limpar arquivos temporários e executáveis
clean:
	rm -f $(OBJS) $(EXEC)
