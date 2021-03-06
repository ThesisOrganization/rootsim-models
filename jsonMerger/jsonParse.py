import json
import numpy as np
import os.path
import math
import argparse


def escape(char):
	if char in ["_"]:
		return "\\"+char
	return char

def filter_escape_string(string):
	arr=map(escape,string)
	string=""
	for elem in arr:
		string+=elem
	return string

parser=argparse.ArgumentParser(description="Parse JSONs from the simulation and the analytical model and merge them in LaTeX.")
parser.add_argument("topology_path",help="folder where the topology.txt and LP.txt are located")
parser.add_argument("simulation_path",help="folder where simulation the JSONs are located")
parser.add_argument("model_path",help="folder where the analytical model JSONs are located")
parser.add_argument("out_path",help="folder where the LaTeX file will be created")
parser.add_argument("-a","--aggregation",help="if node results should be aggregated, default is no aggregation",action="store_true",default=False)
parser.add_argument("-sim_coef","--similarity_coefficient",help="the similarity coefficient, in percentage, to use when aggregating nodes  default is 0.2",default=0.2,type=float)
args=parser.parse_args()

def compute_RA_mean(dict, params, string1, dict_similarity):
  ret = "$"
  D_string = "service_demand"
  N_string = "number_mean_queue"
  flag = True
  total_N = 0
  total=0
  for elem2 in params:
      temp_N = dict[element][string1][elem2][N_string]
      count = 1
      for dict_sim_element in dict_similarity:
          temp_N+= dict[dict_sim_element][string1][elem2][N_string]
          count+=1
      total_N+=temp_N/count

  for elem2 in params:
      temp = dict[element][string1][elem2][D_string] * ( total_N + 1 )
      count = 1
      for dict_sim_element in dict_similarity:
          temp += dict[dict_sim_element][string1][elem2][D_string] * ( total_N + 1 )
          #temp+=dict[dict_sim_element][string1][elem2][string2]
          count+=1

      total_to_return = f"{temp/count:.4g}"
      if flag :
          flag = False
          ret+= str(total_to_return)
      else:
          ret+="$ & $"
          ret+= str(total_to_return)
      total+=temp/count

  total = f"{total:.4g}"
  ret+="$ & $"+total+"$"
  return ret

def result_string_calculation(dict,params, string1, string2, dict_similarity):
    ret = "$"
    flag = True
    total = 0
    for elem2 in params:
        temp = dict[element][string1][elem2][string2]
        count = 1
        for dict_sim_element in dict_similarity:
            temp+=dict[dict_sim_element][string1][elem2][string2]
            count+=1
        total_to_return = f"{temp/count:.4g}"
        if flag :
            flag = False
            ret+= str(total_to_return)
        else:
            ret+="$ & $"
            ret+= str(total_to_return)
        total+=temp/count
    total = f"{total:.4g}"
    ret+="$ & $"+total+"$"
    return ret

def utilization_factor_total(dict,string1,params,dict_similarity):
    total = 0
    for elem2 in params:
        temp = dict[element][string1][elem2]['utilization_factor']
        count = 1
        for dict_sim_element in dict_similarity:
            temp+=dict[dict_sim_element][string1][elem2]['utilization_factor']
            count+=1
        if count == 1:
            total_to_return = temp
        else:
            total_to_return = temp/count
        total += total_to_return
    return total

def aux(dict,dict2,string,dict_similarity):

    f_out.write(" \\midrule\\midrule\\multicolumn{12}{c}{\\textbf{Computed Parameters}}\\\\ \\midrule")
    f_out.write("\\multicolumn{6}{c||}{Analytical Model} & \\multicolumn{6}{c}{Simulated Model}\\\\ \n \\midrule & t & e & c & b & sum & t & e & c & b & sum &  \\\\ \\midrule")

    lambdas_string = result_string_calculation(dict,params, string, 'lambda_in',dict_similarity)
    lambdas_string+=" & "+ result_string_calculation(dict2,params, string, 'lambda_in',dict_similarity)

    f_out.write("$\\lambda$ &" +lambdas_string+"& $\\lambda$ \\\\")

    D_string_model = result_string_calculation(dict,params, string, 'service_demand',dict_similarity)
    D_string_simulator =" & "+ result_string_calculation(dict2,params, string, 'service_demand',dict_similarity)
    D_string = D_string_model + D_string_simulator
    f_out.write("D & "+D_string+"& D\\\\")


    N_string = result_string_calculation(dict,params, string, 'number_mean_queue',dict_similarity)
    N_string+=" & "+ result_string_calculation(dict2,params, string, 'number_mean_queue',dict_similarity)
    f_out.write("N & "+N_string+"& N\\\\")

    U_string = result_string_calculation(dict,params, string, 'utilization_factor',dict_similarity)
    U_string+=" & "+ result_string_calculation(dict2,params, string, 'utilization_factor',dict_similarity)

    f_out.write("U & "+U_string+"& U\\\\")

    R_string = result_string_calculation(dict,params, string, 'response_time_a',dict_similarity)
    R_string +=" & "+ compute_RA_mean(dict2, params, string, dict_similarity)

    f_out.write("RA & "+R_string+"& \\textcolor{teal}{RA}\\\\")

    R_string = result_string_calculation(dict,params, string, 'response_time',dict_similarity)
    R_string +=" & "+ result_string_calculation(dict2,params, string, 'response_time',dict_similarity)

    f_out.write("RB & "+R_string+"& RB\\\\")

    f_out.write("\n\\bottomrule\n\\end{tabular}\n\\end{table}\n\\filbreak\n")



with open(args.simulation_path+'/simulation_results.json') as f_simulator:
  data_simulator = json.load(f_simulator)
with open(args.model_path+'/model_res.json') as f_model:
  data_model = json.load(f_model)


flagStable = True
count = 0;
dict_simulator = {}
dict_model = {}
num_elements_simulator = len(data_simulator)
num_elements_model = len(data_model)

ordered_id_list = []

while(count < num_elements_simulator):
    type = data_simulator[count]['type']
    if type != 'wan':
        id_simulator = data_simulator[count]['id']
        dict_simulator[id_simulator] = {}
        ordered_id_list.append(id_simulator);
        for element in data_simulator[count]:
            if element != 'id':
                dict_simulator[id_simulator][element] = data_simulator[count][element]
            if element == 'stable':
                if (dict_simulator[id_simulator][element] != 1):
                    flagStable = False

    count+=1

count = 0
while(count < num_elements_model):
    id_model = data_model[count]['id']
    dict_model[id_model] = {}
    for element in data_model[count]:
        if element != 'id':
            dict_model[id_model][element] = data_model[count][element]

    count+=1

ordered_id_list.sort()
dict_res = {}
list = ['lambda_in','service_demand','utilization_factor','response_time']
params = ["telemetry","transition","command","batch"]

######NEW PART
for element in ordered_id_list:
    dict_res[element] = {}
    for i in list:
        dict_res[element][i] = []
        for c in params:
            type = dict_simulator[element]['type']
            if type == 'lan':
                if c == 'command':
                    dict_res[element][i].append(dict_simulator[element]['lan_in'][c][i])
                else:
                    dict_res[element][i].append(dict_simulator[element]['lan_out'][c][i])
            else:
                dict_res[element][i].append(dict_simulator[element]['parameters'][c][i])
    dict_res[element]["stable"] = dict_simulator[element]["stable"];
#If you don't use generator.py comment this part and lines 38
stringAdditionalInfo = ""
dict_ids_regional = {}
dict_ids_local = {}
dict_ids_acts = {}
dict_ids_lans = {}
with open(args.topology_path+"/jsonAdditionalInfo.txt") as f:
    lines = f.readlines()
    stringAdditionalInfo+="There is one Central node, between the Central node and the Regional layer there is one WAN. Between each regional and its Locals there is a WAN.\\newline "
    stringAdditionalInfo+="There are "+str(lines[0].strip())+" regional nodes."
    stringAdditionalInfo+="In total "+lines[1]+" local nodes.\\\\"
    stringAdditionalInfo+="In total there are "+str(lines[2]).strip()+ " sensors and "+str(lines[3]).strip()+" actuators."
    #stringAdditionalInfo+=lines[4]#WAN
    if lines[4].strip() == "REGIONALS":
        line_counter = 5
        while lines[line_counter].strip() != "LOCALS":
            line_list = lines[line_counter].split(";")
            id_regional = int(line_list[0])
            type_regional = line_list[1]
            dict_ids_regional[id_regional] = {}
            dict_ids_regional[id_regional]['type'] = type_regional
            dict_ids_regional[id_regional]['type_local'] = {}

            for line_list_element in line_list[2:]:
                type = line_list_element.split(",")[0].strip()
                amount = line_list_element.split(",")[1].strip()

                dict_ids_regional[id_regional]['type_local'][type] = amount

            line_counter+=1
    for line_element in lines[line_counter+1].split(";"):
        id_father = int(line_element.split(",")[0].strip())
        id_local = int(line_element.split(",")[1].strip())
        type = line_element.split(",")[2].strip()
        dict_ids_local[id_local] = {}
        dict_ids_local[id_local]['id_father'] = id_father
        dict_ids_local[id_local]['type'] = type

    for line_element in lines[line_counter+3].split(";"):
        id_father = int(line_element.split(",")[0].strip())
        id_actuator = int(line_element.split(",")[1].strip())
        type = line_element.split(",")[2].strip()
        dict_ids_acts[id_actuator] = {}
        dict_ids_acts[id_actuator]['id_father'] = id_father
        dict_ids_acts[id_actuator]['type'] = type

    for line_element in lines[line_counter+5].split(";"):
        #print(line_element)
        id_father = int(line_element.split(",")[0].strip())
        id_lan = int(line_element.split(",")[1].strip())
        type = line_element.split(",")[2].strip()
        dict_ids_lans[id_lan] = {}
        dict_ids_lans[id_lan]['id_father'] = id_father
        dict_ids_lans[id_lan]['type'] = type
        #print("ID",id_lan)
        dict_ids_lans[id_lan]['sensors'] = {}
        dict_ids_lans[id_lan]['actuators'] = {}
        sen = line_element.split(",")[3]
        for element in sen.split("."):
            type = element.split("/")[0]
            amount = element.split("/")[1]
            dict_ids_lans[id_lan]['sensors'][type] = amount
        act = line_element.split(",")[4]
        for element in act.split("."):
            type = element.split("/")[0]
            amount = element.split("/")[1]
            dict_ids_lans[id_lan]['actuators'][type] = amount

list_regional = []
list_local = []
list_lan = []
list_actuators = []
for element in ordered_id_list:
    type = dict_model[element]['type']
    if(type == 'node'):
        node_type = dict_model[element]['node_type']
        if(node_type == 'regional'):
            list_regional.append(element)
        elif(node_type == 'local'):
            list_local.append(element)
    elif(type == 'lan'):
        list_lan.append(element)
    elif(type == 'actuator'):
        list_actuators.append(element)

if args.aggregation:
	aggregation_flag = True
else:
	aggregation_flag = False


f_out = open(args.out_path+"/complete_results.tex", "w")
#title
initial_header = "\\documentclass{article}\n\\usepackage{booktabs}\n\\usepackage{xcolor}\n\\usepackage{float}\n\\usepackage[margin=0.5in]{geometry}\n\\title{Results}\n\\author{Silvio Dei Giudici, Marco Morella, Mattia Nicolella}\n\\begin{document}\n\\maketitle\n"
f_out.write(initial_header);

begin_table = "\\begin{table}[H]\\centering\\begin{tabular}{@{}c|cccc|c||cccc|c|c@{}}\\toprule\\multicolumn{12}{c}{\\textbf{Given Parameters}}\\\\\\midrule\\multicolumn{2}{c|}{ } & \\multicolumn{2}{c}{t} & \\multicolumn{2}{c}{e} & \\multicolumn{2}{c}{c} & \\multicolumn{2}{c}{b} & \\multicolumn{2}{|c}{sum} \\\\"

def aggr_line(dict,params,string1):
    string2 = 'aggregation_rate'
    aggrs = {}
    for elem2 in params:
        temp = dict[element][string1][elem2][string2]
        count = 1
        aggrs[elem2]= f"{temp/count:.4g}"
    return("\\midrule\\multicolumn{2}{c|}{aggr} & \\multicolumn{2}{c}{"+aggrs['telemetry']+"} & \\multicolumn{2}{c}{"+aggrs['transition']+"} & \\multicolumn{2}{c}{"+aggrs['command']+"} & \\multicolumn{2}{c}{"+aggrs['batch']+"} & \\multicolumn{2}{|c}{ } \\\\"+service_line(dict,params,string1))

def service_line(dict,params,string1):
    string2 = 'service_time'
    serv = {}
    serv['total'] = 0
    for elem2 in params:
        #print(element,string1,elem2,string2)
        #print(dict[element])
        temp = dict[element][string1][elem2][string2]
        count = 1
        serv[elem2]= f"{temp/count:.4g}"
        serv['total']+=temp/count
    serv['total'] = f"{serv['total']:.4g}"

    return(" \\midrule\\multicolumn{2}{c|}{S} & \\multicolumn{2}{c}{"+serv['telemetry']+"} & \\multicolumn{2}{c}{"+serv['transition']+"} & \\multicolumn{2}{c}{"+serv['command']+"} & \\multicolumn{2}{c}{"+serv['batch']+"} & \\multicolumn{2}{|c}{"+serv['total']+"}\\\\")


def sim_cycles(dict_sim,dict_model,parameters):
  if dict_sim["preemption"] == 1:
    return(" \\midrule\\multicolumn{2}{c|}{Sim cycles} & \\multicolumn{2}{c}{"+str(int(math.ceil(dict_sim['time_slice']*dict_sim['sim_proc_multi'])))+"} & \\multicolumn{2}{c}{"+str(int(math.ceil(dict_sim['time_slice']*dict_sim["sim_proc_multi"])))+"} & \\multicolumn{2}{c}{"+str(int(math.ceil(dict_sim['time_slice']*dict_sim['sim_proc_multi'])))+"} & \\multicolumn{2}{c}{"+str(int(math.ceil(dict_sim['time_slice']*dict_sim['sim_proc_multi'])))+"} & \\multicolumn{2}{|c}{ }\\\\")
  else:
    return(" \\midrule\\multicolumn{2}{c|}{Sim cycles} & \\multicolumn{2}{c}{"+str(int(math.ceil(dict_sim['sim_proc_multi']*dict_model[parameters]['telemetry']['service_time'])))+"} & \\multicolumn{2}{c}{"+str(int(math.ceil(dict_sim['sim_proc_multi']*dict_model[parameters]['transition']['service_time'])))+"} & \\multicolumn{2}{c}{"+str(int(math.ceil(dict_sim['sim_proc_multi']*dict_model[parameters]['command']['service_time'])))+"} & \\multicolumn{2}{c}{"+str(int(math.ceil(dict_sim['sim_proc_multi']*dict_model[parameters]['batch']['service_time'])))+"} & \\multicolumn{2}{|c}{ }\\\\")

key_union = [];


with open(args.topology_path+'/LP.txt') as f:
    lines = f.readlines()
    elements = lines[0].strip() #elementi
    LP = lines[1].strip() #Lp
f.close()

#we read the simulator statistics from the json file
with open(args.simulation_path+'/simulation_stats.json') as f_stats:
  stats_simulator = json.load(f_stats)
  run_type=stats_simulator['run_type']
  sim_duration=stats_simulator['duration']
  used_mem=stats_simulator['used_mem']
  num_threads=stats_simulator['num_threads']
  platform=stats_simulator['platform']


to_write = "\\section{General Informations}"
to_write += "Platform: "+platform+".\\\\"
to_write += "Run type: "+run_type+".\\\\ "
if run_type == 'parallel':
	to_write += "Number of used threads: "+num_threads+".\\\\"
to_write += "Number of elements in the topology: "+elements+".\\\\ "
to_write += "Number of LPs used in the simulation: "+LP+".\\\\ "
to_write += "Simulation duration: "+sim_duration+".\\\\ "
to_write += "Memory usage: "+used_mem+".\\\\ "

if(flagStable):
    to_write+= "All elements reached stability in the simulation. "
else:
    to_write+= "Not all elements reached stability, in their sections it will be highlited! "

to_write+="\n\\subsection{Topology Informations}"
to_write+=stringAdditionalInfo
f_out.write(to_write)

dict_regional_similar = {}
dict_local_similar = {}
dict_actuator_similar = {}
dict_lan_similar = {}
key_union = []

if aggregation_flag:
    for element in list_regional:
        dict_regional_similar[element] = []
        for element2 in dict_ids_regional:
            if(element < element2):
                if dict_ids_regional[element] == dict_ids_regional[element2] and dict_res[element]["stable"] == dict_res[element2]["stable"]:
                    key_union.append(element2)
                    dict_regional_similar[element].append(element2)

    for element in list_local:
        dict_local_similar[element] = []
        for element2 in dict_ids_local:
            if(element < element2):
                if dict_ids_local[element] == dict_ids_local[element2] and dict_res[element]["stable"] == dict_res[element2]["stable"]:
                    key_union.append(element2)
                    dict_local_similar[element].append(element2)

    for element in list_actuators:
        dict_actuator_similar[element] = []
        for element2 in dict_ids_acts:
            if(element < element2):
                if dict_ids_acts[element] == dict_ids_acts[element2] and dict_res[element]["stable"] == dict_res[element2]["stable"]:
                    key_union.append(element2)
                    dict_actuator_similar[element].append(element2)


    for element in list_lan:
        dict_lan_similar[element] = []
        for element2 in dict_ids_lans:
            if(element < element2):
                if dict_ids_lans[element] == dict_ids_lans[element2] and dict_res[element]["stable"] == dict_res[element2]["stable"]:
                    key_union.append(element2)
                    dict_lan_similar[element].append(element2)

    pop_list = []
    for element in dict_regional_similar:
        if len(dict_regional_similar[element]) == 0:
            pop_list.append(element)
    for element in pop_list:
        dict_regional_similar.pop(element,None)
    pop_list = []
    for element in dict_local_similar:
        if len(dict_local_similar[element]) == 0:
            pop_list.append(element)
    for element in pop_list:
        dict_local_similar.pop(element,None)
    pop_list = []
    for element in dict_actuator_similar:
        if len(dict_actuator_similar[element]) == 0:
            pop_list.append(element)
    for element in pop_list:
        dict_actuator_similar.pop(element,None)

    for element in dict_lan_similar:
        if len(dict_lan_similar[element]) == 0:
            pop_list.append(element)
    for element in pop_list:
        dict_lan_similar.pop(element,None)

f_out.write("\n\\section{Detailed view}\n")
for element in ordered_id_list:
    if(element not in key_union):
        type = dict_model[element]['type']
        if type == 'node':
            str_to_write = dict_model[element]['node_type'].capitalize()
            to_write = "\\subsection{"+str_to_write+" node "+str(element)+"}\n"
            f_out.write(to_write);
            if dict_simulator[element]["stable"] == 0:
                f_out.write("This element \\textbf{didn't} reach stability in the simulation!\\\\")
            f_out.write("Scheduling algorithm: "+dict_simulator[element]["scheduler"]+".\\\\")
            if dict_simulator[element]["preemption"] == 1:
                f_out.write("Preemption enabled. \\\\")
                f_out.write("Time slice for the scheduler: "+str(dict_simulator[element]["time_slice"])+".\\\\")
                if dict_simulator[element]["sim_proc"] == 1:
                    f_out.write("Message processing is simulated with a loop of "+str(dict_simulator[element]["sim_proc_multi"])+" cycles multiplied by the time slice. The exact number of cycles is represented by the \"Sim cycles\" variable.\\\\")
            else:
                f_out.write("Preemption not enabled. \\\\")
                if dict_simulator[element]["sim_proc"] == 1:
                    f_out.write("Message processing is simulated with a loop of "+str(dict_simulator[element]["sim_proc_multi"])+" cycles multiplied by the service time of the considered message. The exact number of cycles is represented by the \"Sim cycles\" variable.\\\\")
            if dict_model[element]['num_cores'] > 1:
                f_out.write("This node has "+str(dict_model[element]['num_cores'])+" processing units.\\\\")
            if dict_model[element]['node_type'] == 'regional':
                f_out.write("This regional node of type "+filter_escape_string(dict_ids_regional[element]['type'])+" has in its subtree: \\begin{itemize}\n")

                for type_local_dict_ids in dict_ids_regional[element]['type_local']:
                    amount = dict_ids_regional[element]['type_local'][type_local_dict_ids]
                    f_out.write("\\item "+amount+" local nodes of type "+filter_escape_string(type_local_dict_ids)+"\n")
                f_out.write("\\end{itemize}\n")


            if dict_model[element]['node_type'] == 'local':
                f_out.write("This node is of type : "+filter_escape_string(dict_ids_local[element]['type'])+"\\\\"+"\n")

            f_out.write("This element finished the simulation at simulation time: "+str(dict_simulator[element]["sim_time"])+".\\\\\n")
            flagSimilarity = False
            if(element in dict_regional_similar.keys() or element in dict_local_similar.keys()):
                flagSimilarity = True
                to_write = "This node has the same defining characteristics as these other nodes: \\textbf{"
                if dict_model[element]['node_type'] == 'regional':
                    for similar in dict_regional_similar[element]:
                        to_write+= str(similar)+"; "
                    to_write+="}"
                    f_out.write(to_write)

                elif dict_model[element]['node_type'] == 'local':
                    for similar in dict_local_similar[element]:
                        to_write+= str(similar)+"; "
                    to_write+="}"

                    f_out.write(to_write)

            f_out.write(begin_table)
            f_out.write(aggr_line(dict_model,params,'parameters'))
            if dict_simulator[element]['sim_proc']==1:
                f_out.write(sim_cycles(dict_simulator[element],dict_model[element],'parameters'))

            if flagSimilarity:
                if dict_model[element]['node_type'] == 'regional':
                    print(element)
                    aux(dict_model,dict_simulator,'parameters',dict_regional_similar[element])
                elif dict_model[element]['node_type'] == 'local':
                    aux(dict_model,dict_simulator,'parameters',dict_local_similar[element])
            else:
                aux(dict_model,dict_simulator,'parameters',[])


            if dict_simulator[element]['node_type'] == 'central' :
                str_to_write = "Central storage of Node "
                to_write = "\\subsection{"+str_to_write+str(element)+"}\n"
                f_out.write(to_write);
                f_out.write("Scheduling algorithm: "+dict_simulator[element]['storage']["scheduler"]+".\\\\")
                if dict_simulator[element]['storage']["preemption"] == 1:
                    f_out.write("Preemption enabled. \\\\")
                    f_out.write("Time slice for the scheduler: "+str(dict_simulator[element]['storage']["time_slice"])+".\\\\")
                    if dict_simulator[element]['storage']["sim_proc"] == 1:
                        f_out.write("Message processing is simulated with a loop of "+str(dict_simulator[element]['storage']["sim_proc_multi"])+" cycles multiplied by the time slice. The exact number of cycles is represented by the \"Sim cycles\" variable.\\\\")
                else:
                    f_out.write("Preemption not enabled. \\\\")
                    if dict_simulator[element]['storage']["sim_proc"] == 1:
                       f_out.write("Message processing is simulated with a loop of "+str(dict_simulator[element]['storage']["sim_proc_multi"])+" cycles multiplied by the service time of the considered message. The exact number of cycles is represented by the \"Sim cycles\" variable.\\\\")
                f_out.write(begin_table)
                f_out.write(service_line(dict_model,params,'storage'))
                if dict_simulator[element]['storage']['sim_proc']==1:
                    f_out.write(sim_cycles(dict_simulator[element]['storage'],dict_model[element],'storage'))

                aux(dict_model,dict_simulator,'storage',[])

            #f_out.write("\n\\newpage")

        elif type == 'actuator':
            str_to_write = "Actuator "
            to_write = "\\subsection{"+str_to_write+str(element)+"}\n"
            f_out.write(to_write);
            if dict_simulator[element]["stable"] == 0:
                f_out.write("This element \\textbf{didn't} reach stability in the simulation!\\\\")
            f_out.write("Scheduling algorithm: "+dict_simulator[element]["scheduler"]+".\\\\")
            if dict_simulator[element]["preemption"] == 1:
                f_out.write("Preemption enabled. \\\\")
                f_out.write("Time slice for the scheduler: "+str(dict_simulator[element]["time_slice"])+".\\\\")
                if dict_simulator[element]["sim_proc"] == 1:
                    f_out.write("Message processing is simulated with a loop of "+str(dict_simulator[element]["sim_proc_multi"])+" cycles multiplied by the time slice. The exact number of cycles is represented by the \"Sim cycles\" variable.\\\\")
            else:
                f_out.write("Preemption not enabled. \\\\")
                if dict_simulator[element]["sim_proc"] == 1:
                    f_out.write("Message processing is simulated with a loop of "+str(dict_simulator[element]["sim_proc_multi"])+" cycles multiplied by the service time of the considered message. The exact number of cycles is represented by the \"Sim cycles\" variable.\\\\")
            f_out.write("This actuator is of type: "+filter_escape_string(dict_ids_acts[element]['type'])+"\\\\"+"\n")
            f_out.write("This element finished the simulation at simulation time: "+str(dict_simulator[element]["sim_time"])+".\\\\\n")
            flagSimilarity = False
            if element in dict_actuator_similar.keys():
                flagSimilarity = True
                to_write = "This actuator has the same defining characteristics as these other actuators: \\textbf{"
                for similar in dict_actuator_similar[element]:
                    to_write+= str(similar)+"; "
                to_write+="}"
                f_out.write(to_write)

            f_out.write(begin_table)
            f_out.write(service_line(dict_model,params,'parameters'))
            if dict_simulator[element]['sim_proc']==1:
                    f_out.write(sim_cycles(dict_simulator[element],dict_model[element],'parameters'))
            if flagSimilarity:
                aux(dict_model,dict_simulator,'parameters',dict_actuator_similar[element])
            else:
                aux(dict_model,dict_simulator,'parameters',[])

           # f_out.write("\n\\newpage")

        elif type == 'lan':

            str_to_write = "Lan IN "
            to_write = "\\subsection{"+str_to_write+str(element)+"}\n"
            f_out.write(to_write)
            if dict_simulator[element]["stable"] == 0:
                f_out.write("This element \\textbf{didn't} reach stability in the simulation!\\\\")
            f_out.write("Scheduling algorithm: "+dict_simulator[element]['lan_in']["scheduler"]+".\\\\")
            if dict_simulator[element]['lan_in']["preemption"] == 1:
                f_out.write("Preemption enabled. \\\\")
                f_out.write("Time slice for the scheduler: "+str(dict_simulator[element]['lan_in']["time_slice"])+".\\\\")
                if dict_simulator[element]['lan_in']["sim_proc"] == 1:
                    f_out.write("Message processing is simulated with a loop of "+str(dict_simulator[element]['lan_in']["sim_proc_multi"])+" cycles multiplied by the time slice. The exact number of cycles is represented by the \"Sim cycles\" variable.\\\\")
            else:
                f_out.write("Preemption not enabled. \\\\")
                if dict_simulator[element]['lan_in']["sim_proc"] == 1:
                    f_out.write("Message processing is simulated with a loop of "+str(dict_simulator[element]['lan_in']["sim_proc_multi"])+" cycles multiplied by the service time of the considered message. The exact number of cycles is represented by the \"Sim cycles\" variable. The exact number of cycles is represented by the \"Sim cycles\" variable.\\\\")
            f_out.write("This element finished the simulation at simulation time: "+str(dict_simulator[element]["sim_time"])+".\\\\\n")
            flagSimilarity = False
            if element in dict_lan_similar.keys():
                flagSimilarity = True
                to_write = "This LAN has the same defining characteristics as these other LANs: \\textbf{"
                for similar in dict_lan_similar[element]:
                    to_write+= str(similar)+"; "
                to_write+="}"
                f_out.write(to_write)

            f_out.write(begin_table)
            f_out.write(service_line(dict_model,params,'lan_in'))
            if dict_simulator[element]['lan_in']['sim_proc']==1:
                    f_out.write(sim_cycles(dict_simulator[element]['lan_in'],dict_model[element],'lan_in'))
            if flagSimilarity:
                aux(dict_model,dict_simulator,'lan_in',dict_lan_similar[element])
            else:
                aux(dict_model,dict_simulator,'lan_in',[])


            str_to_write = "Lan OUT "
            to_write = "\\subsection{"+str_to_write+str(element)+"}\n"
            f_out.write(to_write);
            f_out.write("Scheduling algorithm: "+dict_simulator[element]['lan_out']["scheduler"]+".\\\\")
            if dict_simulator[element]['lan_out']["preemption"] == 1:
                f_out.write("Preemption enabled. \\\\")
                f_out.write("Time slice for the scheduler: "+str(dict_simulator[element]['lan_out']["time_slice"])+".\\\\")
                if dict_simulator[element]['lan_out']["sim_proc"] == 1:
                    f_out.write("Message processing is simulated with a loop of "+str(dict_simulator[element]['lan_out']["sim_proc_multi"])+" cycles multiplied by the time slice. The exact number of cycles is represented by the \"Sim cycles\" variable.\\\\")
            else:
                f_out.write("Preemption not enabled. \\\\")
                if dict_simulator[element]['lan_out']["sim_proc"] == 1:
                    f_out.write("Message processing is simulated with a loop of "+str(dict_simulator[element]['lan_out']["sim_proc_multi"])+" cycles multiplied by the service time of the considered message. The exact number of cycles is represented by the \"Sim cycles\" variable.\\\\")
            f_out.write(begin_table)
            f_out.write(service_line(dict_model,params,'lan_out'))
            if dict_simulator[element]['lan_out']['sim_proc']==1:
                    f_out.write(sim_cycles(dict_simulator[element]['lan_out'],dict_model[element],'lan_out'))
            if flagSimilarity:
                aux(dict_model,dict_simulator,'lan_out',dict_lan_similar[element])
            else:
                aux(dict_model,dict_simulator,'lan_out',[])

           # f_out.write("\n\\newpage")


f_out.write("\n\\end{document}")

f_out.close()
