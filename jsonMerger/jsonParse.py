import json
def result_string_calculation(dict,params, string1, string2):
    ret = "$"
    flag = True
    for elem2 in params:
        if flag :
            flag = False
            ret+= str(dict[element][string1][elem2][string2])
        else:
            ret+="$ & $"
            ret+= str(dict[element][string1][elem2][string2])
    ret+="$"
    return ret

def utilization_factor_total(dict,string1,params):
    total = 0
    for elem2 in params:
        total += dict[element][string1][elem2]['utilization_factor']
    return total

def aux(begin_table,dict,string):
    table_string = begin_table
    table_string+="$\\lambda_t$ & $\\lambda_e$ & $\\lambda_c$ & $\\lambda_b$"
    table_string+= "\\"
    table_string+= "\\"
    table_string+="\n"
    f_out.write(table_string)

    lambdas_string = result_string_calculation(dict,params, string, 'lambda_in')
    lambdas_string+="\\\\"
    to_print = "\\midrule\n"+ lambdas_string+ "\n\\bottomrule\n\\end{tabular}\n\\end{table}"
    f_out.write(to_print)

    to_print= begin_table
    to_print+="$D_t$ & $D_e$ & $D_c$ & $D_b$"
    to_print+= "\\"
    to_print+= "\\"
    to_print+="\n"
    f_out.write(to_print)

    D_string = result_string_calculation(dict,params, string, 'service_demand')

    D_string+="\\\\"
    to_print = "\\midrule\n"+ D_string+ "\n\\bottomrule\n\\end{tabular}\n\\end{table}"
    f_out.write(to_print)

    to_print = begin_table
    to_print+="$U_t$ & $U_e$ & $U_c$ & $U_b$"
    to_print+="\\"
    to_print+="\\"
    to_print+="\n"
    f_out.write(to_print)
    U_string = result_string_calculation(dict,params, string, 'utilization_factor')
    total = utilization_factor_total(dict,string,params)

    U_string+="\\\\"
    to_print = "\\midrule\n"+ U_string+ "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n"
    f_out.write(to_print)

    total_u = "\\centering Total Utlization Factor = $" + f"{total:.3}" + "$\n"
    f_out.write(total_u)

    f_out.write(begin_table)
    to_print="$R_t$ & $R_e$ & $R_c$ & $R_b$"
    to_print+= "\\"
    to_print+= "\\"
    to_print+="\n"
    f_out.write(to_print)

    R_string = result_string_calculation(dict,params, string, 'response_time')
    R_string+="\\\\"
    to_print = "\\midrule\n"+ R_string+ "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n"
    f_out.write(to_print)

with open('../tree_simulator/simulation_results.json') as f_simulator:
  data_simulator = json.load(f_simulator)
with open('../model_computation/model_res.json') as f_model:
  data_model = json.load(f_model)

count = 0;
dict_simulator = {}
dict_model = {}
num_elements = len(data_simulator)
ordered_id_list = []
while(count < num_elements):
    id_simulator = data_simulator[count]['id']
    dict_simulator[id_simulator] = {}
    ordered_id_list.append(id_simulator);
    for element in data_simulator[count]:
        if element != 'id':
            dict_simulator[id_simulator][element] = data_simulator[count][element]
    id_model = data_model[count]['id']
    dict_model[id_model] = {}
    for element in data_model[count]:
        if element != 'id':
            dict_model[id_model][element] = data_model[count][element]

    count+=1

ordered_id_list.sort()
params = ["telemetry","transition","command","batch"]
f_out = open("complete_results.tex", "w")
#title
initial_header = "\\documentclass{article}\n\\usepackage{booktabs}\n\\usepackage{float}\n\\title{Results}\n\\begin{document}\n\\maketitle\n\\section{Detailed view}\n"
f_out.write(initial_header);
begin_table ="\\begin{table}[H]\n\\centering\n\\begin{tabular}{@{}cccc@{}}\n\\toprule\n"
complete_table = "\\begin{table}[H]\n\\centering\n\\begin{tabular}{@{}cccc|cccc@{}}\n\\toprule\n$S_t$ & $S_e$ & $S_c$ & $S_b$ & $aggr_t$ & $aggr_e$ & $aggr_c$ & $aggr_b$\\\\"
semi_complete_table = "\\begin{table}[H]\n\\centering\n\\begin{tabular}{@{}cccc@{}}\n\\toprule\n$S_t$ & $S_e$ & $S_c$ & $S_b$\\\\"

for element in ordered_id_list:
    type = dict_model[element]['type']
    if type == 'node':
        str_to_write = dict_model[element]['node_type'].capitalize()
        to_write = "\\subsection{"+str_to_write+" node "+str(element)+"}\n"
        f_out.write(to_write);

        table_string = "\\subsubsection{Given parameters}\n"
        f_out.write(table_string)
        f_out.write(complete_table)

        return1 = result_string_calculation(dict_model,params, 'parameters', 'service_time')
        return1 +=" & "
        return1 += result_string_calculation(dict_model,params, 'parameters', 'aggregation_rate')
        return1 +="\\\\"

        to_print = "\n\\midrule\n"+return1+ "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n"
        f_out.write(to_print)

        table_string = "\\subsubsection{Computed parameters}\n\\begin{minipage}{0.5\\textwidth}\n\\centering	\\textbf{Analytical Model}\n"
        f_out.write(table_string)
        aux(begin_table,dict_model,'parameters')
        f_out.write("\\end{minipage}")

        table_string = "\n\\begin{minipage}{0.5\\textwidth}\n\\centering	\\textbf{Simulated Model}\n"
        f_out.write(table_string)
        aux(begin_table,dict_simulator,'parameters')
        f_out.write("\\end{minipage}")


        if dict_simulator[element]['node_type'] == 'central' :
            str_to_write = "Central storage of Node "
            to_write = "\\subsection{"+str_to_write+str(element)+"}\n"
            f_out.write(to_write);

            table_string = "\\subsubsection{Given parameters}\n"
            f_out.write(table_string)
            f_out.write(semi_complete_table)

            service_string = result_string_calculation(dict_model,params, 'parameters', 'service_time')
            service_string+="\\\\"

            to_print = "\n\\midrule\n"+service_string+ "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n"
            f_out.write(to_print)

            table_string = "\\subsubsection{Computed parameters}\n\\begin{minipage}{0.5\\textwidth}\n\\centering	\\textbf{Analytical Model}\n"
            f_out.write(table_string)
            aux(begin_table,dict_model,'parameters')
            f_out.write("\\end{minipage}")

            table_string = "\n\\begin{minipage}{0.5\\textwidth}\n\\centering	\\textbf{Simulated Model}\n"
            f_out.write(table_string)
            aux(begin_table,dict_simulator,'parameters')
            f_out.write("\\end{minipage}")

        f_out.write("\n\\newpage")

    elif type == 'actuator':
        str_to_write = "Actuator "
        to_write = "\\subsection{"+str_to_write+str(element)+"}\n"
        f_out.write(to_write);

        table_string = "\\subsubsection{Given parameters}\n"
        f_out.write(table_string)
        f_out.write(semi_complete_table)

        service_string = result_string_calculation(dict_model,params, 'parameters', 'service_time')
        service_string+="\\\\"

        to_print = "\n\\midrule\n"+service_string+ "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n"
        f_out.write(to_print)

        table_string = "\\subsubsection{Computed parameters}\n\\begin{minipage}{0.5\\textwidth}\n\\centering	\\textbf{Analytical Model}\n"
        f_out.write(table_string)
        aux(begin_table,dict_model,'parameters')
        f_out.write("\\end{minipage}")

        table_string = "\n\\begin{minipage}{0.5\\textwidth}\n\\centering	\\textbf{Simulated Model}\n"
        f_out.write(table_string)
        aux(begin_table,dict_simulator,'parameters')
        f_out.write("\\end{minipage}")

    elif type == 'lan':

        str_to_write = "Lan IN "
        to_write = "\\subsection{"+str_to_write+str(element)+"}\n"
        f_out.write(to_write);

        table_string = "\\subsubsection{Given parameters}\n"
        f_out.write(table_string)
        f_out.write(semi_complete_table)

        service_string = result_string_calculation(dict_model,params, 'lan_in', 'service_time')
        service_string+="\\\\"

        to_print = "\n\\midrule\n"+service_string+ "\n\\bottomrule\n\\end{tabular}\n\\end{table}"
        to_print+="\n"
        f_out.write(to_print)

        table_string = "\\subsubsection{Computed parameters}\n\\begin{minipage}{0.5\\textwidth}\n\\centering	\\textbf{Analytical Model}\n"
        f_out.write(table_string)
        aux(begin_table,dict_model,'lan_in')
        f_out.write("\\end{minipage}")

        table_string = "\n\\begin{minipage}{0.5\\textwidth}\n\\centering	\\textbf{Simulated Model}\n"
        f_out.write(table_string)
        aux(begin_table,dict_simulator,'lan_in')
        f_out.write("\\end{minipage}")


        table_string = "\\subsubsection{Given parameters}\n"
        f_out.write(table_string)
        f_out.write(semi_complete_table)

        service_string = result_string_calculation(dict_model,params, 'lan_out', 'service_time')
        service_string+="\\\\"

        to_print = "\n\\midrule\n"+service_string+ "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n"
        f_out.write(to_print)

        table_string = "\\subsubsection{Computed parameters}\n\\begin{minipage}{0.5\\textwidth}\n\\centering	\\textbf{Analytical Model}\n"
        f_out.write(table_string)
        aux(begin_table,dict_model,'lan_out')
        f_out.write("\\end{minipage}")

        table_string = "\n\\begin{minipage}{0.5\\textwidth}\n\\centering	\\textbf{Simulated Model}\n"
        f_out.write(table_string)
        aux(begin_table,dict_simulator,'lan_out')
        f_out.write("\\end{minipage}")
        f_out.write("\n\\newpage")


f_out.write("\n\\end{document}")

f_out.close()
