import os



###read exp, freq and solv
def load_data():
    global exp, freq, solv
    info_file = open(data_set_name + "/acqu","r")
    while 1:
        line = info_file.readline()
        if line.find("##$PULPROG= <") != -1:
            exp = line.strip("##$PULPROG= <").strip(">\n")
            #print("exp = " + exp)
        if line.find("##$BF1= ") != -1:
            freq = float(line[7:].strip("\n"))
            #print("freq = " + str(freq))
        if line.find("##$SOLVENT= <") != -1:
            solv = line.strip("##$SOLVENT= <").strip(">\n")
            if solv == "CDCl3":
                solv = "CDCl<sub>3</sub>"
            elif solv == "DMSO":
                solv = "d<sub>6</sub>-DMSO"
            elif solv == "MeOD":
                solv = "d<sub>4</sub>-methanol"
            elif solv == "D2O":
                solv = "D<sub>2</sub>O"
            #print("solv = " + solv)
        if line.find("\n") == -1:
            break
    info_file.close()
###read exp, freq and solv, finish



###read integral info
def proc_integ():
    global integ_list
    integ_file = open(data_set_name + "/pdata/1/integrals.txt","r")
    #print("\nIntegral info:")
    integ_output = 0

    integ_list = []

    while 1:
        line = integ_file.readline()
        if integ_output == 1:
            integ = line.strip(">\n")
            if integ != "":
                integ = list(map(float,integ.split()))
                integ.pop(0)
                integ_list.append(integ)
                #print("from " + str(integ[0]) + " to " + str(integ[1]) + ", area: " +str(integ[2]))
        if line.find("Number") != -1 and line.find("Integrated Region") != -1 and line.find("Integral") != -1:
            integ_output = 1
        if line.find("\n") == -1:
            break

    integ_file.close()
    #print(integ_list)
###read integral info, finish



###read peak info
def proc_peak():
    global peak_list
    peak_file = open(data_set_name + "/pdata/1/peaklist.xml","r")
    #print("\nPeak info:")

    peak_list = []

    while 1:
        line = peak_file.readline()
        if line.find('    <Peak1D F1="') != -1:
            #peak = line.strip('''    <Peak1D F1"''').strip('''" type="0"/">\n''')
            peak = line[14:].strip('''" type="0"/">\n''')
            peak = list(map(float,peak.split('" intensity="')))
            peak_list.append(peak)
            #print(str(peak[0]) + ", intensity: " + str(peak[1]))
        if line.find("\n") == -1:
            break

    peak_file.close()
    #print(peak_list)
    #print("exported")
###read peak info, finish



###combine peak with integral
def combine_peak_with_integral():
    global integ_list
    for i in range(len(integ_list)):
        integ_list[i].append([])
        #print("from " + str(integ_list[i][0]) + " to " + str(integ_list[i][1]) + ", area: " +str(integ_list[i][2]) + ", include following peak(s):")
        for j in range(len(peak_list)):
            if peak_list[j][0] < integ_list[i][0] and peak_list[j][0] > integ_list[i][1]: # add a peak if in the range of an integral
                integ_list[i][3].append(peak_list[j])
                #print("    " + str(peak_list[j][0]) + ", intensity: " + str(peak_list[j][1]))

    #print(integ_list)
###combine peak with integral, finish



###analysis mutilplet
def analysis_mutilplet():
    global integ_list
    for i in range(len(integ_list)):
        num_of_peaks = len(integ_list[i][3])
        mutilplet_string = ["null","s","d","t","q","quint","sext","sept","oct",]
        binomial = [0, 1,
        [1,1],
        [1,2,1],
        [1,3,3,1],
        [1,4,6,4,1],
        [1,5,10,10,5,1],
        [1,6,15,20,15,6,1],
        [1,7,21,35,35,21,7,1],
        ]
        
        judge_range = [0.833, 1.2]


        if num_of_peaks == 0: # if num of peaks is 0, mark "null"
            integ_list[i].append("null")
        elif num_of_peaks == 1: #if num of peaks is 1, mark "s"
            integ_list[i].append("s")
        elif num_of_peaks == 2: #if num of peaks is 2, judge if two height of two peak are similar, if yes, mark "d" with J vaule, if no, mark "m"
            if (judge_range[0]) < (integ_list[i][3][0][0]/integ_list[i][3][1][0]) < (judge_range[1]):
                integ_list[i].append("d")
                J = (abs(integ_list[i][3][0][0] - integ_list[i][3][1][0]))*freq
                integ_list[i].append(J)
            else:
                integ_list[i].append("m")
        elif num_of_peaks > 8: #if num of peaks more than 8, mark "m"
            integ_list[i].append("m")
        else: #if num of peaks range from 3 to 8, do more judgement
            cond_temp = []
            all_cond_right = 1

            for j in range(num_of_peaks - 2):  #to judge if the acj peak have similar distance
                #MSG(
                    #"shift: " + str((integ_list[i][3][j+2][0])) + " and " + str((integ_list[i][3][j+1][0])) + " and " + str((integ_list[i][3][j][0]))
                    #+ ". distance: " + str((integ_list[i][3][j+2][0] - integ_list[i][3][j+1][0])) + " and " + str((integ_list[i][3][j+1][0] - integ_list[i][3][j][0]))
                    #+ ". condition: " + str((integ_list[i][3][j+2][0] - integ_list[i][3][j+1][0])/(integ_list[i][3][j+1][0] - integ_list[i][3][j][0]))
                    #)
                if (judge_range[0]) < ((integ_list[i][3][j+2][0] - integ_list[i][3][j+1][0])/(integ_list[i][3][j+1][0] - integ_list[i][3][j][0])) < (judge_range[1]):
                    cond_temp.append(1)
                else:
                    cond_temp.append(0)
                    
            for j in range(num_of_peaks - 1):  #to judge if the acj peak acorring with binomial distribute
                #MSG(
                    #"shift: " + str((integ_list[i][3][j+1][0])) + " and " + str((integ_list[i][3][j][0]))
                    #+ ". height: " + str((integ_list[i][3][j+1][1])) + " and " + str((integ_list[i][3][j][1]))
                    #+ ". condition: " + str(integ_list[i][3][j+1][1]/integ_list[i][3][j][1])
                    #)
                binomial_ratio = (float(binomial[num_of_peaks][j+1]))/(float(binomial[num_of_peaks][j]))  #to defind theoric ratio according binomial array
                if (0.667) < ((integ_list[i][3][j+1][1]/integ_list[i][3][j][1])/binomial_ratio) < (1.5):
                    cond_temp.append(1)
                else:
                    cond_temp.append(0)
                    
            for each in cond_temp:  
                all_cond_right = all_cond_right * each
            if all_cond_right == 1:   #if all above conditions were satsify, mark as specific simple couple with J value
                integ_list[i].append(mutilplet_string[num_of_peaks])
                J = (abs(integ_list[i][3][0][0] - integ_list[i][3][num_of_peaks-1][0]))*freq/(num_of_peaks-1)
                integ_list[i].append(J)
            else:
                if num_of_peaks == 4:
                    condition = []
                    condition.append(judge_range[0] < abs((integ_list[i][3][0][0] - integ_list[i][3][1][0])/(integ_list[i][3][2][0] - integ_list[i][3][3][0])) < judge_range[1]) # if the distance between 1,2 and 3,4 also similar
                    condition.append(judge_range[0] < abs(integ_list[i][3][0][1]/integ_list[i][3][1][1]) < judge_range[1])  #if height of all 4 peaks are similar,
                    condition.append(judge_range[0] < abs(integ_list[i][3][0][1]/integ_list[i][3][2][1]) < judge_range[1])
                    condition.append(judge_range[0] < abs(integ_list[i][3][0][1]/integ_list[i][3][3][1]) < judge_range[1])
                    all_cond_right = 1
                    for each in condition:
                        all_cond_right = all_cond_right * each
                    if all_cond_right == 1:   
                        integ_list[i].append("dd")
                        J1 = (abs(integ_list[i][3][0][0] - integ_list[i][3][1][0]) + abs(integ_list[i][3][2][0] - integ_list[i][3][3][0]))*freq/2
                        J2 = (abs(integ_list[i][3][0][0] - integ_list[i][3][2][0]) + abs(integ_list[i][3][1][0] - integ_list[i][3][3][0]))*freq/2
                        integ_list[i].append([J1, J2])
                    else:
                        integ_list[i].append("m")
                elif num_of_peaks == 6:
                    condition = []
                    condition.append(judge_range[0] < abs((integ_list[i][3][0][0] - integ_list[i][3][1][0])/(integ_list[i][3][2][0] - integ_list[i][3][3][0])) < judge_range[1])
                    # if the distance between 1,2 and 3,4 also similar
                    condition.append(judge_range[0] < abs((integ_list[i][3][0][0] - integ_list[i][3][1][0])/(integ_list[i][3][4][0] - integ_list[i][3][5][0])) < judge_range[1])
                    # if the distance between 1,2 and 5,6 also similar
                    condition.append(judge_range[0] < abs((integ_list[i][3][0][0] - integ_list[i][3][2][0])/(integ_list[i][3][2][0] - integ_list[i][3][4][0])) < judge_range[1])
                    # if the distance between 1,3 and 3,5 also similar
                    
                    condition.append(judge_range[0] < abs(integ_list[i][3][0][1]/integ_list[i][3][1][1]) < judge_range[1])
                    condition.append(judge_range[0] < abs(integ_list[i][3][0][1]/integ_list[i][3][4][1]) < judge_range[1])
                    condition.append(judge_range[0] < abs(integ_list[i][3][0][1]/integ_list[i][3][5][1]) < judge_range[1])
                    # if the height of 1,2,5,6 are similar
                    
                    condition.append(judge_range[0] < abs(integ_list[i][3][0][1]*2/integ_list[i][3][2][1]) < judge_range[1])
                    condition.append(judge_range[0] < abs(integ_list[i][3][0][1]*2/integ_list[i][3][3][1]) < judge_range[1])
                    # if the height of 3,4 are around 2 times as 1
                    
                    all_cond_right = 1
                    for each in condition:
                        all_cond_right = all_cond_right * each
                        
                    if all_cond_right == 1:
                        integ_list[i].append("dt")
                        J1 = (abs(integ_list[i][3][0][0] - integ_list[i][3][1][0]) + abs(integ_list[i][3][2][0] - integ_list[i][3][3][0]) + abs(integ_list[i][3][4][0] - integ_list[i][3][5][0]))*freq/3
                        J2 = (abs(integ_list[i][3][0][0] - integ_list[i][3][4][0]) + abs(integ_list[i][3][1][0] - integ_list[i][3][5][0]))*freq/4
                        integ_list[i].append([J1, J2])
                    else:
                        integ_list[i].append("m")
                else:
                    integ_list[i].append("m")



def prod_string_1H():
    global rep_string
    #rep_string = rep_string + "<sup>1</sup>H NMR (" + solv + ", " + str(int(freq+0.2)) + " MHz) &delta; "
    rep_string = rep_string + "<sup>1</sup>H NMR ("  + str(int(freq+0.2)) + " MHz, " + solv + ") &delta; "
    for i in range(len(integ_list)):
        num_of_hydrogen_atom = int(integ_list[i][2]+0.5)
        if integ_list[i][0] - integ_list[i][1] > 0.5:
            pos_of_region = str(round(integ_list[i][0], 2)) + "~" + str(round(integ_list[i][1], 2))
        else:
            pos_of_region = (integ_list[i][0] + integ_list[i][1])/2
            pos_of_region = str(round(pos_of_region, 2))
        item = pos_of_region + " (" + str(int(integ_list[i][2]+0.5)) + "H, " + integ_list[i][4]
        if len(integ_list[i]) == 6:
            if type(integ_list[i][5]) == float:
                item = item + ", <i>J</i> = " + str(round(integ_list[i][5], 2)) + " Hz)"
            elif type(integ_list[i][5]) == list:
                item = item + ", <i>J</i><sub>1</sub> = " + str(round(integ_list[i][5][0], 2)) + " Hz, <i>J</i><sub>2</sub> = " + str(round(integ_list[i][5][1], 2)) + " Hz)"
        else:
            item = item + ")"
        rep_string = rep_string + item
        if i < len(integ_list)-1:
            rep_string = rep_string + ", "
        else:
            rep_string = rep_string + "."



def prod_string_13C():
    global rep_string
    #rep_string = rep_string + " <sup>13</sup>C NMR (" + solv + ", " + str(int(freq+0.2)) + " MHz) &delta; "
    rep_string = rep_string + " <sup>13</sup>C NMR (" + str(int(freq+0.2)) + " MHz, " +  solv + ") &delta; "
    for i in range(len(peak_list)):
        item = str(round(peak_list[i][0], 2))
        rep_string = rep_string + item
        if i < len(peak_list) - 1:
            rep_string = rep_string + ", "
        else:
            rep_string = rep_string + "."




curdat = CURDATA()
data_set_name = curdat[3] + "/" + curdat[0] + "/" + curdat[1]
rep_string = ""
load_data()
if exp == "zg30":
    suffix = "_1H"
    #print("1H NMR (" + solv + ", " + str(int(freq+0.5)) + " MHz)")
    proc_integ()
    proc_peak()
    combine_peak_with_integral()
    analysis_mutilplet()
    prod_string_1H()
elif exp == "zgpg30":
    suffix = "_13C"
    proc_peak()
    prod_string_13C()
#print(integ_list)



file_name = curdat[3] + "/" + curdat[0] + suffix + ".html"
exp_file = open(file_name, 'w')
exp_file.write(rep_string)
exp_file.close()
