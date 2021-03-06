#ifndef APPLICATION_DATATYPES_H
#define APPLICATION_DATATYPES_H

#include "ROOT-Sim.h"
#include "idmap/idmap.h"
#include "partop/partop_datatypes.h"
#include "priority_scheduler/priority_scheduler_datatypes.h"

//#############################################
//APPLICATION DATA
//#############################################


typedef enum _events_type{ //INIT should be 0
	DISABLE_UNUSED_LP=10,
	ARRIVE,
	ARRIVE_DISK,
	FINISH,
	FINISH_DISK,
	GENERATE_TRANSITION,
	GENERATE_TELEMETRY,
	UPDATE_TIMESTAMP,
	STABILITY_ACQUIRED,
	STABILITY_LOST,
	RECEIVE_SETUP_MESSAGE,
	START_SIMULATION
} events_type;

/** These timestamp are used during the various phases of the setup.
 * The value of the timestamp is used as it is to send the struct the refer to, then every inner pointer is sent as a separate message using an increase of 0.01, to avoid overlapping of the messages for different structs.
 */
typedef enum _ts_data{
	TS_DISABLE_UNUSED_LP=1,
	TS_RECV_LP_STATE_INFO,
	TS_RECV_GENERAL_TOPOLOGY,///< Timestamp used to start sending the general_topology.
	TS_RECV_ELEMENT_INDEX_MAP, ///< Timestamp used to send the element_to_index idmap.
	TS_RECV_DEVICES, ///< Timestamp used to start sending the info on the device_array.
	TS_RECV_ELEMENT_TOPOLOGY, ///< Timestamp used to start sendig Element_topology.
	TS_RECV_SPECIFIC_TOPOLOGY,///< Timestamp used to start sending the specific_topology.
	TS_RECV_BELOW_DEVICES_INFO, ///< Timestamp used to start sending info about the below sensors/actuators.
	TS_START_SIMULATION ///< This value must be higher that all the timestamps in the setup phase sincr it's used to start the simulation after the initialization of the LPs.
} ts_data;

/// Used to determine the type of data received in a ::RECEIVE_SETUP_DATA event.
typedef enum _setup_data_types{
	SETUP_DATA_LP_STATE=0, ///< lp_state struct
	SETUP_DATA_PINT, ///< int*
	SETUP_DATA_PDOUBLE, ///< double*
	SETUP_DATA_PIDMAP, ///<idamp*
	SETUP_DATA_DEVICES_ARRAY,
	SETUP_DATA_DEVICE_STATE,
	SETUP_DATA_GENERAL_TOPOLOGY, ///< general_topology struct
	SETUP_DATA_ELEMENT_TOPOLOGY, ///< Element_topology struct
	SETUP_DATA_LAN_TOPOLOGY, ///< lan_topology struct
	SETUP_DATA_WAN_TOPOLOGY, ///< wan_topology struct
	SETUP_DATA_SENSOR_TOPOLOGY, ///< sensor_topology struct
	SETUP_DATA_ACTUATOR_TOPOLOGY, ///< actuator_topology struct
	SETUP_DATA_NODE_TOPOLOGY ///< node_topology
} setup_data_types;


typedef struct _queue_state {
	double time_slice;
	simtime_t * start_processing_timestamp;
	job_info * current_jobs;
	int num_cores; ///max number of current jobs running
	int num_running_jobs; ///number of the current jobs that are handled by the multi core
	int num_jobs_in_queue;
	//global statistics
	double global_actual_timestamp;
	double global_actual_timestamp_stable;
	double global_start_timestamp;
	/*
	//multi-core metrics
	double B_global;
	double B_global_stable;
	double last_timestamp_B_global;
	*/
	//end
	simtime_t last_update_ts;
	double W2;
	double W2_stable;
	//METRICS, from slide 4, single queue modeling, CP
	//note that these values are computed with the values after the last finish event before the termination
	int * A; //number of jobs arrived (arrivals)
	int * A_post; //number of jobs arrived (arrivals), after the last finish event
	int * C; //number of jobs completed (completions)
	double * B; //busy time, time in which the queue is computing
	double * W; //time spent in the system by all arrivals
	int * A_stable;
	int * C_stable;
	double * B_stable;
	double * W_stable;
	simtime_t * actual_timestamp_stable;
	simtime_t * actual_timestamp;
	simtime_t * start_timestamp;
	double * old_response_times;
	void * queues;
} queue_state;

typedef struct _sensor_state {
	//prio_type job_generated;
	double rate_telemetry;
	double rate_transition;
} sensor_state;

typedef struct _node_state {
	queue_state * queue_state;
	double * service_rates;
	node_type type;
	int telemetry_aggregation;
	int num_telemetry_aggregated;
	double up_delay;
	double down_delay;
	int id_wan_down;
	double prob_cmd;
	int batch_aggregation;
	int num_batch_aggregated;
	queue_state * disk_state;
} node_state;

typedef struct _actuator_state {
	queue_state * queue_state;
	double rate_transition;
	double service_rate_command;
} actuator_state;


typedef enum _lan_direction{ //INIT should be 0
	LAN_IN = 0,
	LAN_OUT
} lan_direction;

typedef struct _lan_state {
	queue_state * queue_state_in;
	queue_state * queue_state_out;
	double * service_rates_in;
	double * service_rates_out;
} lan_state;

typedef struct _wan_state {
	double delay;
} wan_state;

typedef union {
	sensor_state * sensor;
	node_state * node;
	actuator_state * actuator;
	lan_state * lan;
	wan_state * wan;
} state_info;

///Used to determine is an LP is active or not
typedef enum _lp_usage_types{
	LP_DISABLED=0,
	LP_SETUP,
	LP_ENABLED
} lp_usage_types;

typedef enum _simulation_status{
	SIMULATION_ACTIVE = 0,
	SIMULATION_STOP
} simulation_status; //to delete

typedef enum _stability_value{
	ELEMENT_UNSTABLE = 0,
	ELEMENT_STABLE
} stability_value;

typedef struct{
	int element_id; ///< The id of the element which the data we are about to receive belongs.
} message_header;

typedef struct {
	message_header header;
	setup_data_types data_type; ///< The type of the data we are about to receive.
	setup_data_types container_struct; ///< The type of the struct which contains the data we will receive.
	size_t data_size; ///< The size of the data we are about to receive.
	void* data;
} message_setup;

typedef struct{
	message_header header;
	job_info info;
} message_arrive;

typedef struct{
	message_header header;
	int core; ///the core that is handling the job
	lan_direction direction;
} message_finish;

typedef struct{
	message_header header;
} message_generate;

typedef struct{
	message_header header;
} message_update;

typedef struct _device_state {
	simulation_status simulation_completed;
	stability_value stability;
	simtime_t device_timestamp;
	state_type type;
	Element_topology* topology;
	int num_acts_types;
	double * prob_actuators;
	state_info info;
} device_state;

typedef struct _state {
	lp_usage_types lp_enabled; //1 lp enabled, 0 lp disabled
	int number_lps_enabled;
	int num_stable_elements;
	//general infos
	device_state** devices_array;
	int num_devices;
	general_topology* general_topology;
	idmap* element_to_index;
} lp_state;


#endif /* APPLICATION_DATATYPES_H */
