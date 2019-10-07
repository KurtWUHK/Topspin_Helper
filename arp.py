import os
curdat = CURDATA()


target_dir = curdat[3] + "/"
dirs = os.listdir(target_dir)


for i in range(len(dirs)):
    if os.path.isdir(target_dir + dirs[i]):
        sub_dirs = os.listdir(target_dir + dirs[i])
        #MSG(dirs[i])
        for j in range(len(sub_dirs)):
            if os.path.exists(target_dir + dirs[i] + "/" + sub_dirs[j] + "/acqu"):
                #MSG(dirs[i] + "_" + sub_dirs[j])
                RE([dirs[i], sub_dirs[j], "1", target_dir])
                XCMD("str")
                XCMD("apl")
