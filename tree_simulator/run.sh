#!/bin/bash
source_location=$(pwd)
number_lp=""
file_json="simulation_results.json"
stat_json="simulation_stats.json"
run_type="serial"
working_threads=-1
options=""
dbg_arg=""
dbg_param=""
opt_make=""
dbg_make=""
quiet="no"
error="no"
threads_equal_lp="no"
targets=()
sim_name=""
seed=""
timeout=""
output_location="../tree_simulator_bin"
make_redirect=""

for arg
do
	if [[ $arg == "-c" || $arg == "--compile-only" ]];then
		targets[${#targets[@]}]="compile"
	elif [[ $arg == "-e" || $arg == "--execute-only" ]];then
		targets[${#targets[@]}]="execute"
	elif [[ $arg == "--run-complete" ]]; then
		targets[${#targets[@]}]="all"
		options="all"
	elif [[ $arg == "-q" || $arg == "--quiet" ]]; then
		quiet="yes"
	elif [[ $arg == "json" || $arg == "clean" ]]; then
			targets[${#targets[@]}]=$arg
			options=$arg
	elif [[ $arg == "parallel" ]]; then
			run_type="parallel"
	elif [[ $arg == "valgrind" || $arg == "gdb" ]]; then
		dbg_arg=$arg
		opt_make+="DBG=1 "
		dbg_make="clean"
	elif [[ $arg == "--preempt" ]]; then
		opt_make+="PREEMPT=1 "
	elif [[ $arg == "--threads-less-than-lps" ]]; then
		threads_less_than_lps="yes"
	elif [[ ${arg,,} == "--sched=rr" ]]; then
		opt_make+="SCHED_RR=1 "
	elif [[ ${arg:0:16} == "--sim_processing" ]]; then
		opt_make+="SIM_PROC=1 "
		if [[  ${arg:17} > 0 ]]; then
			opt_make+="SIM_PROC_MULTI=${arg:17} "
		fi
	elif [[ ${arg:0:29} == "--redir_compilation_messages=" ]]; then
		make_redirect=" >>${arg#"--redir_compilation_messages="} 2>&1"
	elif [[ ${arg:0:7} == "--seed=" ]]; then
		echo ${arg#"--seed="} > ~/.rootsim/numerical.conf
		seed="--deterministic-seed"
	elif [[ ${arg:0:5} == "--lp=" ]]; then
		number_lp=${arg#"--lp="}
	elif [[ ${arg:0:5} == "--wt=" ]]; then
		working_threads=${arg#"--wt="}
	elif [[ ${arg:0:6} == "--out=" ]];then
		output_location=${arg#'--out='}
	elif [[ ${arg:0:10} == "--timeout=" ]]; then
		timeout=${arg#"--timeout="}
		timeout_rootsim="--simulation-time $timeout"
		timeout_use=$timeout
		timeout_neurome="--time=$timeout"
	elif [[ $arg == "--all-sim" ]]; then
		sim_name="all"
	else
		arg=${arg//'-'/''}
		arg=${arg,,}
		if [[ $arg == "rootsim" ]]; then
			sim_name="ROOT-Sim"
		elif [[ $arg == "rootsim3" || $arg == "neurome" ]]; then
			sim_name="NeuRome"
		elif [[ $arg == "use" ]]; then
			sim_name="USE"
		fi
	fi
done

if [[ $run_type == "parallel" && $working_threads == -1 ]]; then
	working_threads=$(nproc)
fi

if [[ $run_type == "serial" ]]; then
	working_threads=1
fi

if [ "$dbg_arg" == "valgrind" ]; then
	dbg_param="valgrind --leak-check=full -s"
elif [ "$dbg_arg" == "gdb" ]; then
		dbg_param="gdb --args"
fi


if [[ ${#targets[@]} > 1 && $options == "all" ]]; then
	echo -e "ERROR: --run-complete and other execution options specified, use ONLY --run-complete or -c or -e."
	error="yes"
fi

if [[ ${#targets[@]} == 0 ]]; then
	echo -e "ERROR: no operation specified, use at least one of these: -c -e --run-complete json clean.\n"
	error="yes"
fi
if [[ $sim_name == "" ]] &&  [[ ^.*execute.*$ =~ ${targets[@]} || $options == "all" ]]; then
	echo -e "ERROR: no simulator specified, use at least one of these: USE, ROOT-Sim, NeuRome.\n"
	error="yes"
fi
if [[ $sim_name == "all" ]] && [[ ^.*execute.*$ =~ ${targets[@]} || $options == "all" ]]; then
	echo -e "ERROR: you cannot choose to execute the simulation on ALL the available simulators!\n"
	error="yes"
fi
if [[ $sim_name == "all" || $sim_name == "" ]] && [[ $options == "json" ]]; then
	echo -e "ERROR: you cannot choose to parse the simulation output withtout specifing the simulator, this will mess up the stats!\n"
	error="yes"
fi
if [[ $quiet == "no" || $error == "yes" ]]; then
	echo -e "This script can compile and run the model, using the configured simulator. The operation to perform and the simulator to target need to passed as a parameter (see below for the options).\n Running the model will generate two json files:\n
\"$file_json\": which will contain the data of all the model elements (sensors excluded), that is also available in a per LP fashion in the \"lp_data\" folder\n
\"$stat_json\": which contains general statistics on the executed simulation\n"
	echo -e "\nTo run the model at least these files are required in this folder:\n
\"topology.txt\", which will contain the topology and the characteristics of the elements in the model\n
\"LP.txt\", which will contain the association between model elements and LPs.\n
The binary data for each LP in the \"bin\", \"bin/gentop\" and \"bin/lptop\" folders.\n\n"
	echo -e "The execution can be customized with some arguments:\n
	\n General options:\n
\"-q --quiet\": disable this message\n
\"--redir_compilation_messages=[path to file]\": redirect compilation messages to a file which will be used in append.
\"clean\": remove all products of compilation and execution, leaving only the source files\n
\nSimulator options:\n
\"USE\": choose USE as the simulator\n
\"ROOT-Sim\": choose ROOT-Sim as the simulator\n
\"NeuRome\": choose NeuRome as the simulator\n
\"--all-sim\": choose all the simulators, this is valid only for the compilation operation\n
\nExecution options:\n
\"-c --compile-only\": compiles only the model. When the platform is USE the folder \"USE-model-sources\" is left untouched if it already exists\n
\"-e --execute-only\": only executes the model passing parameters according to the type of simulator chosen\n
\"json\": only merge the json files in \"lp_data\"\n
\"--run-complete\": Compile and run the model with the chosen simulator\n
\nExecution tweaks:\n
\"--threads-less-than-lps\": Ties the number of threads for parallel execution to be less or equal to the number of LPs, otherwise the simulation will be aborted with error code 150.\n
\"--timeout=[number]\": for USE it represente the number of seconds after which the simulation must be stopped. For ROOT-Sim instead it represents the logical virtual time after which the simulation must be stopped.
\"--seed=\":defines the seed to be used during the simulation.\n
\"--sched=[RR,FIFO]\": choose the scheduler type, the default is FIFO.\n
\"--preempt\": enable preemption of task, using as time slice for each node the smallest service time.\n
\"--sim_processing=[loops]\": activate the simulation of the message processing (via busy wait), the \"loops\" parameter is optional and should b ea power of 10 since it represents the number which will multiplicate the service time (or the time slice if the preemption is enabled) to determine how many cycles the busy wait will last. Default value is 100.\n
\"gdb\" run the program under gdb (this will make a temporary modification to the makefile, adding -g  and -O0 to the compiler options)\n
\"valgrind\": run the program under valgrind (this will make a temporary modification to the makefile, adding -g to the compiler options)\n
\"--lp=\": specify the number of LPs, if this argument is not provided the number of LPs will be determined from \"LP.txt\"\n
\"serial\": run with only one thread (used by default)\n
\"parallel\": run with multiple threads\n
\"--wt=\": specify the number of threads to use (if not given the minimum between the number of CPUs and the number of LP will be used in a parallel run)\n
\"--out=[path_to_output_folder]\": The path to the folder in which compilation results must be saved and from where the simulation mus be runned, defaults to \"tree_simulation_bin\"\n"
	echo -e "\nUnrecognized arguments will be ignored."
fi
if [[ $error == "yes" ]]; then
	exit 255
else
	if [[ $quiet == "no" ]]; then
		read -n1 -r -p "Press any key to continue or CTRL+C to exit." key
	fi
fi

for target in ${targets[@]}; do
	if [ "$options" == "clean" ]; then
			rm -r -f $output_location/lp_data/
			rm -r -f $output_location/outputs
			make clean >/dev/null
			rm -f $output_location/*.txt
			rm -f $output_location/*.json
	else
		echo "Using $sim_name as the simulation platform."
		if [[ $target == "all" || $target == "execute" ]]; then
			#we read the LP.txt to get the number of lps and we search for the longest line in LP.txt and topology.txt, since we don't want a realloc by libc when parsing these files.
			if [[ -e "$output_location/LP.txt" && -r "$output_location/LP.txt" ]]; then
				number_lp=$(sed -n 2p $output_location/LP.txt)
			else
				echo "ERROR: no LP.txt in $output_location."
				exit 255
			fi
			if [[ ! -e "$output_location/topology.txt" || ! -r "$output_location/topology.txt" ]]; then
				echo "ERROR: no topology.txt in $output_location.".
				exit 255
			fi
			echo "Removing previous output files.."
			# we remove folders and files conating the output data of the simulation
			rm -rf $output_location/outputs
			rm -rf $output_location/lp_data/
			rm -f $output_location/$stat_json
			rm -f $output_location/$file_json
			mkdir -p $output_location/lp_data
			echo "Done."
		fi
		#it makes no sense to have more threads than LPs
		if [[ $target == "all" || $target == "execute" ]]; then
			if [[ $working_threads -gt $number_lp ]]; then
				if [[ $threads_less_than_lps == "yes" ]]; then
					echo "EXECUTION ABORTED AS REQUESTED: more threads ($working_threads) than LPs ($number_lp)."
					exit 150
				else
					echo "Number of working threads ($working_threads) greater than number of lps ($number_lp), matching number of lps."
					working_threads=$number_lp
				fi
			fi
		fi

		if [[ $sim_name == "ROOT-Sim" || $sim_name == "all" ]]; then
			if [[ $run_type == "parallel" ]]; then
				stat_source="$output_location/outputs/execution_stats"
			else
				stat_source="$output_location/outputs/sequential_stats"
			fi
			if [[ $target == "all" || $target == "compile" ]]; then
				echo "Compiling model..."
				eval make LOCATION=$output_location $opt_make $dbg_make rootsim $make_redirect
				err=$?
				if [[ $err != 0  ]]; then
					echo "Error during compilation of model, aborting."
					exit $err
				fi
				echo "Done, executable is called \"simulation_rootsim\" and can be found in the \"$output_location\" folder."
			fi
			if [[ $target == "all" || $target == "execute" ]]; then
			echo "Executing model..."
			cd $output_location
				if [[ $run_type == "parallel" ]]; then
						echo "Parallel execution with $working_threads threads."
						$dbg_param ./simulation_rootsim --wt $working_threads --lp $number_lp $seed $timeout_rootsim
					else
						echo "Serial execution."
                        $dbg_param ./simulation_rootsim --sequential --lp $number_lp $seed $timeout_rootsim
					fi
				err=$?
				if [[ $err != 0  ]]; then
					echo "ROOT-Sim has raised an error, aborting."
					exit $err
				fi
				cd $source_location
				echo "Done."
			fi
			if [[ $target == "all" || $options == "json" ]]; then
				echo "Parsing statistics..."
				stat_used_mem=$(sed -n 's/PEAK MEMORY USAGE.......... : //p' $stat_source)
				stat_duration=$(sed -n 's/TOTAL SIMULATION TIME ..... : //p' $stat_source)
				echo "Done."
			fi
		fi
		if [[ $sim_name == "USE" || $sim_name == "all" ]]; then
			if [[ $target == "all" || $target == "compile" ]]; then
				echo "Compiling model..."
				eval make LOCATION=$output_location $opt_make $dbg_make use $make_redirect
				err=$?
				if [[ $err != 0  ]]; then
					echo "Error during compilation of model, aborting."
					exit $err
				fi
				echo "Done, executable is called \"simulation_use\" and can be found in the \"$output_location\" folder."
			fi
			cd $output_location
			stat_source="USE_output.txt"
			if [[ $target == "all" || $target == "execute" ]]; then
				echo "Executing model..."
				if [[ $run_type == "parallel" ]]; then
					echo "Parallel execution with $working_threads threads."
				else
					echo "Serial execution."
				fi
				# during debug we don't save the stats
				if [[ -z $dbg_arg ]]; then
					# we save the output so we can grab the stats without redirecting output
					# starting process in background and redirecting output to file
					script -e -O $stat_source -c "./simulation_use $working_threads $number_lp $timeout_use"
				else
					$dbg_param ./simulation_use $working_threads $number_lp $timeout_use
				fi
				err=$?
				if [[ $err != 0  ]]; then
					echo "USE has raised an error, aborting."
					exit $err
				fi
			fi
			if [[ $target == "all" || $options == "json" ]]; then
				echo "parsing statistics..."
				stat_used_mem=$(sed -E -n -e 's/Total allocated space\.+: //p' $stat_source)
				stat_duration=$(sed -E -n -e 's/Simulation ended \(seconds\):[ ]+//p' $stat_source)
				echo "Done."
			fi
			cd $source_location
		fi
		if [[ $sim_name == "NeuRome" || $sim_name == "all" ]]; then
			if [[ $target == "compile" || $target == "all" ]]; then
				echo "Compiling model..."
				eval make LOCATION=$output_location $opt_make $dbg_make neurome $make_redirect
				err=$?
				if [[ $err != 0  ]]; then
					echo "Error during compilation of model, aborting."
					exit $err
				fi
				echo "Done; there are 2 executables, one for the parallel execution and one for the serial execution, they are called \"simulation_neurome_[parallel/serial]\" and can be found in the \"$output_location\" folder."
			fi
			if [[ $target == "execute" || $target == "all" ]]; then
				echo "Executing model..."
				cd $output_location
				if [ "$run_type" == "parallel" ]; then
					echo "Parallel execution with $working_threads threads."
					$dbg_param ./simulation_neurome_parallel --wt $working_threads --lp $number_lp $seed $timeout_neurome
				else
					echo "Serial execution."
					$dbg_param ./simulation_neurome_serial --lp $number_lp $seed $timeout_neurome
				fi
				err=$?
				if [[ $err != 0  ]]; then
					echo "NeuRome has raised an error, aborting."
					exit $err
				fi
			fi
			cd $source_location
			#if [[ $target == "all" || $options == "json" ]]; then
				#TODO grab statistics from neurome output
			#fi
		fi
		if [[ $target == "all" || $options == "json" ]]; then
			echo "Exporting simulation statistics to $stat_json..."
			#creating the json file with stats
			echo "{ \"run_type\": \"$run_type\", \"num_threads\": \"$working_threads\", \"used_mem\": \"$stat_used_mem\", \"duration\": \"$stat_duration\", \"platform\":\"$sim_name\" }" > $output_location/$stat_json
				echo "Done."
			# merging lp jsons
			echo "Merging jsons in lp_data..."
			python3 generate_json.py $output_location"/lp_data" $output_location/$file_json
			echo "Done, results are in $file_json."
		fi
	fi
done
