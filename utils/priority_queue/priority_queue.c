#include "priority_queue.h"

#define CAPACITY 50


priority_queue* create_queue(void){

    return heap_new(MIN_HEAP, CAPACITY);

}

void enqueue(priority_queue * pq, double timestamp, job_info payload){

    heap_add(pq, timestamp, payload);

}
job_info dequeue(priority_queue * pq){

    return heap_poll(pq);

}

int check_presence(priority_queue * pq){

    _heap * h = pq;
    return h->used;

}

void delete_queue(priority_queue * pq){

    heap_delete(pq);

}

void print_queue(priority_queue * pq){

    heap_print(pq);

}

double queue_peek(priority_queue* pq){
	return heap_peek(pq);
}
