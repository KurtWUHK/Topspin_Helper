import os
curdat = CURDATA()


def export():
        XCMD("1 f1p " + str(left_edge))
        XCMD("1 f2p " + str(right_edge))
        XCMD("autoplot -e " + curdat[3] + "/" + curdat[0] + "_" + exp + ".png")


def read_solvent():
        info_file = open(curdat[3] + "/" + curdat[0] + "/" + curdat[1] + "/acqu","r")
        while 1:
                line = info_file.readline()
                if line.find("##$SOLVENT= <") != -1:
                        solv = line.strip("##$SOLVENT= <").strip(">\n")
                        #print("solv = " + solv)
                if line.find("\n") == -1:
                        break
        info_file.close()
        #MSG(solv)
        global def_left_edge_H
        global def_left_edge_C
        if solv == "CDCl3":
                def_left_edge_H = 7.5
                def_left_edge_C = 80
        elif solv == "DMSO":
                def_left_edge_H = 3
                def_left_edge_C = 45
        elif solv == "MeOD":
                def_left_edge_H = 4
                def_left_edge_C = 55        
        elif solv == "D2O":
                def_left_edge_H = 5
                def_left_edge_C = 0
        else:
                def_left_edge_H = 0
                def_left_edge_C = 0        
        #MSG(str(def_left_edge_H))

                
def read_peak():
        peak_list = GETPEAKSARRAY()
        #slist = ""
        #for peak in peak_list:
                #slist += "ppm=" + str(peak.getPositions()[0]) + ", intens="+ str(peak.getIntensity()) + "\n"
        #MSG(slist)
        global first_peak, last_peak
        first_peak = peak_list[0].getPositions()[0]
        last_peak = peak_list[len(peak_list)-1].getPositions()[0]
        #info = str(first_peak) + ", " + str(last_peak)


read_solvent()
if GETPAR2("PULPROG") == "zg30":
	exp = "1H"
	XCMD("layout +/H.xwp")
	read_peak()
	left_edge = float(int((first_peak+1)*2))/2
	right_edge = float(int((last_peak-0.5)*2))/2
	if right_edge > -0.5:
		right_edge = -0.5
	if left_edge < def_left_edge_H:
                left_edge = def_left_edge_H                
	export()
elif GETPAR2("PULPROG") == "zgpg30":
	exp = "13C"	
	XCMD("layout +/C.xwp")
	read_peak()
	left_edge = (int((first_peak/10)+2))*10
	right_edge = (int((first_peak/10)-1))*10
	if right_edge > -10:
		right_edge = -10
	if left_edge < def_left_edge_C:
                left_edge = def_left_edge_C
	export()


#info = str(left_edge) + ", " + str(right_edge)
#MSG(info)



