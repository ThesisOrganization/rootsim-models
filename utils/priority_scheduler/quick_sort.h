/** \file quick_sort.h
 * \brief Quick sort algorithm to order the inpu and output queues according to their type.
 */

/** \brief Quick Sort algorithm to sort in place an array of queues.
 * \todo see if its also invariant
 * \param[in,out] arr The queue array to be sorted.
 * \param[in] num The number of elements in the array.
 */
void quicksort(queue_conf** arr,int num);
