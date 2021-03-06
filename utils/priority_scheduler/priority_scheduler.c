/** \file priority_scheduler.c
 * \brief Implementation of the priority scheduler
 */

#include "priority_scheduler.h"
#include "scheduling_algorithms.h"
#include "queue_quick_sort.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

/** Allocates a new `::priority_scheduler` struct with the given parameters
 * If the order of the queue of the same type is meaningful (usually when `::UPDATE_PRIO` is not used) the array must be already sorted since the sorting algorithm will mess up the relative position of elements of the same type.
 * A `NULL` pointer and 0 can be used to configure a scheduler with no available output queues, it will return to the caller jobs extracted from the input queues.
 */
priority_scheduler* new_prio_scheduler(queue_conf** input, queue_conf** output, int num_input, int num_output, unsigned int events,int prio, scheduling_algorithm algo){

	//we sort the input and output queues by their type
	queue_quicksort(input,num_input);
	queue_quicksort(output,num_output);

	//we allocate data for our scheduler
	priority_scheduler* sched = (priority_scheduler*) malloc(sizeof(priority_scheduler));
	sched->input_queues=input;
	sched->num_input_queues=num_input;
	sched->num_output_queues=num_output;
	if(num_output>0){
		sched->output_queues=output;
	} else{
		sched->output_queues=NULL;
	}
	if(events<=0 && num_output==0){
		sched->events_to_schedule=1;
	} else {
		sched->events_to_schedule=events;
	}
	sched->sched_algo=algo;
	sched->mix_prio=prio;
	sched->scheduler_timestamp=0;
	sched->last_schedule_out=INVALID_JOB;
	return sched;
}

/** \brief Check is an output queue is infinite or has still space for jobs
 * \param[in] output The output queue to be checked
 */
int check_queues(queue_conf* queue){
	int infinite_queue,queue_full=0;
	//check if the queue is infinite
	infinite_queue= queue->check_full==NULL;
	if(!infinite_queue){
		//check if the queue is full
		queue_full=(queue->check_full)(queue->queue);
	}
	return infinite_queue || !queue_full;
}

/**
 * To schedule the jobs on the output queues we extract them in order from the input queues, according to the type of queue.
 * The queue in which a job is placed is chosen by considering the order in which the output queues are placed, with the
 * possibility to upgrade the priority of a job (See `::UPGRADE_PRIO`) if there is a suitable queue available.
 * __NOTE:__ It is possible that some jobs can be not scheduled depending on the output queue characteristics and on the usage of `::UPDATE_PRIO`.
 * Before scheduling jobs, if the output queues are all empty the `scheduler_timestamp` is reset, to try avoiding overflows.
 * Real time jobs that don't meet the deadline are scheduled regardless (they shoul always meet the deadline).
 * If there were no output queues supplied, the function will return up to `events_to_schedule` jobs, according to the scheduler configuration.
 */
int schedule_out(priority_scheduler* sched,job_info* jobs,int num_jobs){
	int out_queue;
	int i,output_index=0,output_empty=1,job_index=0,events_to_schedule=0,res=SCHEDULE_FAIL;
	job_info job;
	job.job_type=INVALID_JOB;
	//we determine the number of events to be scheduled out
	if(sched->events_to_schedule==0){
		events_to_schedule=1;
	} else{
		events_to_schedule=sched->events_to_schedule;
	}
	//some sanity checks
	if(sched->num_output_queues>0){
		// we check if all output queues are empty
		for(i=0;i<sched->num_output_queues && output_empty;i++){
			output_empty= output_empty && (sched->output_queues[i]->check_presence)(sched->output_queues[i]->queue)==0;
		}
	} else{
		if(jobs==NULL || num_jobs<events_to_schedule){
			printf("invalid parameters for the scheduler\n");
			exit(EXIT_FAILURE);
		}
	}

	//if all output queues are empty we can reset the scheduler timestamp
	if(output_empty || sched->num_output_queues==0){
		sched->scheduler_timestamp=0;
	}

	// we schedule events from the input queues (sorted by priority) to the output queues (sorted by priority)
		for(job_index=0;job_index<events_to_schedule;job_index++){
			//we select the output queue according to the scheduling algorithm
			out_queue=select_queue(sched);
			if(out_queue<0){
				return out_queue;
			}
			if(sched->num_output_queues>0){
				//we find a suitable output queue
				if(sched->mix_prio==UPGRADE_PRIO){
					//if the priority of a job can be upgraded we choose the first queue which is not full
					while(!check_queues(sched->output_queues[output_index])){
						output_index++;
						//if we don't have any other output queues we cannot schedule jobs
						if(output_index>=sched->num_output_queues){
							return res;
						}
					}
				} else {
					// if the job priority must not be upgraded, we try to schedule jobs from the ith input queue to the ith output queue
					if(check_queues(sched->output_queues[out_queue])){
						output_index=out_queue;
					} else {
						// we cannot schedule an event from the ith input queue, so we jump to the next input queue
						break;
					}
				}
			}
			//we can now schedule the job from the ith input queue to a suitable output queue
			//we dequeue the job from the ith input queue
			job=(sched->input_queues[out_queue]->dequeue)(sched->input_queues[out_queue]->queue);
			if(job.job_type!=INVALID_JOB || res==SCHEDULE_DONE){
				sched->last_schedule_out=job.job_type;
				res=SCHEDULE_DONE;
			}

				if(sched->num_output_queues>0){
					//we enqueue the job on the chosen output queue
					(sched->output_queues[output_index]->enqueue)(sched->output_queues[output_index]->queue,sched->scheduler_timestamp,job);
				} else {
					//we add it to the job array if we have no output queues configured
					jobs[job_index]=job;
				}
				//we increment the timestamp of the scheduler since we have scheduled one more job
				sched->scheduler_timestamp++;
		}
	return res;
}

/**
 * Schedule a new event in the first appropriate queue which has free space.
 */
int schedule_in(priority_scheduler* sched, job_info job){
	int i, done=SCHEDULE_FAIL;
	//we find a suitable queue
	for(i=0;i<sched->num_input_queues && done==SCHEDULE_FAIL;i++){
		// we skip the queue if we have different queues per job type
		if(sched->input_queues[i]->type==INVALID_JOB || sched->input_queues[i]->type==job.job_type){
			if(sched->input_queues[i]->prio==job.prio && check_queues(sched->input_queues[i])){
			//the queue has the same type of the event and is not full so we can add the job in it
			(sched->input_queues[i]->enqueue)(sched->input_queues[i]->queue,job.deadline,job);
			done=SCHEDULE_DONE;
			}
		}
	}
	return done;
}
