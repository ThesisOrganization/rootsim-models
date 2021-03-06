#ifndef _HEAP_H
#define	_HEAP_H

#ifdef	__cplusplus
extern "C" {
#endif

#include "../../priority_scheduler/priority_scheduler_datatypes.h"

typedef struct _heap_entry{
	double key;
	job_info payload;
	int position;
} _heap_entry;

typedef struct {
	_heap_entry * array;
	int size;
	int used;
	int is_min_heap;
} _heap;

#ifdef	__cplusplus
}
#endif

#endif	/* HEAP_H */
