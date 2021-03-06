#ifndef COMMON_FUNCTIONS_H
#define COMMON_FUNCTIONS_H

#include "../../utils/priority_scheduler/priority_scheduler.h"
#include "../../utils/partop/header.h"
#include "../../utils/priority_queue/priority_queue.h"
#include "../../utils/application_datatypes.h"
#include "../../utils/message/message.h"
#include "../simulation.h"

#define FREEJOB_NOTFOUND -1

void fill_job_info(job_info * info, double arrived_in_node_timestamp, double deadline, job_type job_type, int device_sender, double busy_time_transition, double waiting_time_transition, int device_destination);

int get_free_core(job_info * current_jobs, int num_cores);

/*
#define DEBUG
#ifdef DEBUG
#define ASSERT(x,s)\
if (! (x)) {\
    printf(s);\
    exit(1);\
}
#else
#define ASSERT(x,s)
#endif
*/

//#define DEBUG
#define PRINT_RESULTS


#ifdef DEBUG
#define PRINT(s) printf("%s\n", s)
#else
#define PRINT(s)
#endif

#ifdef DEBUG
#define PRINT_VALUE(v) printf("%d\n", v)
#else
#define PRINT_VALUE(v)
#endif

#ifdef DEBUG
#define PRINT_DOUBLE(v) printf("%f\n", v)
#else
#define PRINT_DOUBLE(v)
#endif

#ifdef DEBUG
//list all debug prints and tests
//#define DEBUG_NUMBER_MSGS //used to print the type of message received by the central that are going to be saved on the disk
//#define DEBUG_RESPONSE_TIME
//#define DEBUG_INITIAL_VALUES_NODES


#endif


//NODES
#define GET_SERVICE_TIMES_NODES(a) getServiceTimesNodes(a)
#define GET_NODE_TYPE(a) getNodeType(a)
#define GET_AGGREGATION_RATE(a) getAggregationRate(a)
#define GET_DELAY_UPPER_ROUTER(a) getDelayUpperRouter(a)
#define GET_DELAY_LOWER_ROUTER(a) getDelayLowerRouter(a)
#define GET_WAN_DOWN(a) getWanDown(a)
#define GET_PROB_COMMAND(a) getProbCommandResponse(a)
#define GET_NUMBER_OF_CORES(a) getNumberOfCores(a)

//SENSORS
#define GET_SENSOR_TYPE_RATES(a) getSensorRates(a)
#define GET_SENSOR_TYPE(a) getSensorType(a)
#define GET_LIST_SENSORS_BY_TYPE(a,b) getListSensorsByType(a,b)

//ACTUATORS
#define GET_SERVICE_COMMAND(a) getServiceTimeCommand(a)
#define GET_RATE_TRANSITION(a) getRateTransition(a)

//LANS
#define GET_LAN_IN_TYPE_SERVICE(a) getLANsINserviceTimesByType(a)
#define GET_LAN_OUT_TYPE_SERVICE(a) getLANsOUTserviceTimesByType(a)
#define GET_LAN_TYPE(a) getLanType(a)

//WANS
#define GET_DELAY(a) getDelay(a)

#define GET_ACTUATOR_PATHS(a) getActuatorPaths(a)
#define GET_ACTUATOR_PATHS_INDEX(a,b) getActuatorPathsIndex(a,b)
#define GET_ACT_TYPE_BELOW_LIST(a) getActuatorTypesBelowList(a)
#define GET_SENS_TYPE_BELOW_LIST(a) getSensorsTypesBelowList(a)
#define GET_LIST_ACTUATORS_BY_TYPE(a,b) getListActuatorsByType(a,b)
#define GET_UPPER_NODE(a) getUpperNode(a)

#define GET_DISK_SERVICES(a) getDiskServices(a)

#define GET_TYPE(a) getType(a)
#define CONVERT_ELEMENT_TO_LP(a,b) getElToLPMappingOneElement(a,b)
#define GET_EL_TO_LP_MAPPING(a)  getElToLPMapping(a)
#define GET_NUM_EL_TO_LP(a) getNumValidElToLP(a)

//GENERAL TOPOLOGY
#define GET_TOTAL_NODES(a) getTotalNodes(a)
#define GET_SENSOR_NODES(a) getSensorNodes(a)
#define GET_ACTUATOR_NODES(a) getActuatorNodes(a)
#define GET_NUMBER_OF_LANS(a) getNumberOfTotalLANs(a)
#define GET_NUMBER_OF_WANS(a) getNumberOfTotalWANs(a)
#define GET_NUMBER_ACT_TYPES(a) getNumberOfActTypes(a)
#define GET_NUMBER_SENS_TYPES(a) getNumberOfSensTypes(a)
#define GET_PROB_ACTUATORS(a) getProbOfActuators(a)
#define GET_TOPOLOGY(a,b,c) getTopology(a,b,c)
#define GET_GEN_TOPOLOGY(a) getGenTopology(a)

#define GET_COST(a) getCost(a)

//ELEMENT TOPOLOGY
#define GET_ELEMENT_TOPOLOGY(a,b) getLPTopology(a,b)
#define GET_NUMBER_ACT_BELOW(a) getNumberOfBelowActuators(a)
#define GET_NUMBER_SENS_BELOW(a) getNumberOfBelowSensors(a)
#define GET_NUMBER_LOWER_ELEMENTS(a) getNumberLower(a)
#define GET_LOWER_ELEMENTS(a) getLowers(a)
#define GET_LANS(a) getLANS(a)
#define GET_NUMBER_LANS(a) getNumberLANS(a)


//TOTAL TOPOLOGY
#define DESTROY_TOTAL_TOPOLOGY(a) destroyTotalTopology(a)

//LP TOPOLOGY
#define GET_LP_TOPOLOGY(a) getLPTopology(a)
#define GET_LP_DEVICES(a,b) getLPtoElementMappingOneLP(a,b)
#define GET_NUM_LP_DEVICES(a,b) getAmountsOfElementsInOneLP(a,b)
#define GET_NUM_ACT_PATHS(a) getNumValidActuatorPaths(a)
#define GET_NUM_LPS(a) getNumLP(a)
#endif /* COMMON_FUNCTIONS_H */
