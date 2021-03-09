from algorithm import *
####################################################################################################################################

def main(file, K = 1, R = 1, P = 0, H = 2):
    TIME_S = monotonic()
    [nodes, RESULT, MAC_TIME, COUNT, COUNT_H, COUNT_C] = MAC(H, READ_FILE(f"{file}_dom.txt", f"{file}_var.txt", f"{file}_con.txt"), Solution = deque(), r = R, probes = P, function = heuristics[H], k = K)
    TIME_F = monotonic()
    TIME = TIME_F - TIME_S
    FILE = open("RESULTS.txt", "a")
    FILE.write(f"{'---'*9}{file} : K = {K}{'---'*9}\n")
    FILE.write(f"Total Time : {str(timedelta(seconds=TIME))[:-4] if len(str(timedelta(seconds=TIME))) == 14 else str(timedelta(seconds=TIME))}\nNodes : {nodes}\nResult : {RESULT if RESULT else 'None (End of Time)'}\n")
    FILE.write(f"MAC Time : {str(timedelta(seconds=MAC_TIME))[:-4] if len(str(timedelta(seconds=MAC_TIME))) == 14 else str(timedelta(seconds=MAC_TIME))}\n")
    if COUNT :
        FILE.write(f"#COMMON CHOICE :\n")
        if sum(COUNT.values()) :
            for value in COUNT : FILE.write(f"{value} : {round((100*COUNT[value])/sum(COUNT.values()), 2)}%\n")
    if COUNT_H :
        FILE.write(f"#COMMON HEURISTIC CHOICE :\n")
        HEURISTICS = {2:"DDEG", 3:"DWDEG", 4:"ACTIVITY", 5:"IMPACT"}
        if sum(COUNT_H.values()) :
            for value in COUNT_H :
                if len(value) == 1 : FILE.write(f"({HEURISTICS[value[0]]}) : {round((100*COUNT_H[value])/sum(COUNT_H.values()), 2)}%\n")
                elif len(value) == 2 : FILE.write(f"{(HEURISTICS[value[0]],HEURISTICS[value[1]])} : {round((100*COUNT_H[value])/sum(COUNT_H.values()), 2)}%\n")
                elif len(value) == 3 : FILE.write(f"{(HEURISTICS[value[0]],HEURISTICS[value[1]],HEURISTICS[value[2]])} : {round((100*COUNT_H[value])/sum(COUNT_H.values()), 2)}%\n")
                else : FILE.write(f"{(HEURISTICS[value[0]],HEURISTICS[value[1]],HEURISTICS[value[2]],HEURISTICS[value[3]])} : {round((100*COUNT_H[value])/sum(COUNT_H.values()), 2)}%\n")
    if COUNT_C :
        FILE.write(f"#COMMON ROW CHOICE :\n")
        if sum(COUNT_C.values()) :
            for value in COUNT_C : FILE.write(f"{value} : {round((100*COUNT_C[value])/sum(COUNT_C.values()), 2)}%\n")
    FILE.write(f"{'---'*9}END{'---'*9}\n")
    FILE.close()
    return [nodes, RESULT, TIME_F - TIME_S]

def Run(files):
    import csv
    for file in files :
        RESULT, result = None, None
        with open('results.csv', 'a+', newline='') as csvfile:
            field_list, data = [], []
            for i in range(1,6,2) : field_list += [f"ddeg (k = {i})\nTime - Nodes", f"dwdeg (k = {i})\nTime - Nodes", f"activity (k = {i})\nTime - Nodes", f"impact (k = {i})\nTime - Nodes"]
            field_list = ["Problem"] + field_list + ["Result"]
            writer = csv.DictWriter(csvfile, fieldnames= field_list)
            writer.writeheader()
            print(f"FILE NAME : {file}")
            data.append(file)
            for h, rpk in zip([2,3,4,5]*4,[(1, 0, 1),(1, 0, 1),(0.99, 25, 1),(1, 0, 1), (1, 0, 3),(1, 0, 3),(0.99, 25, 3),(1, 0, 3), (1, 0, 5),(1, 0, 5),(0.99, 25, 5),(1, 0, 5)]) :
                print(f"HEURISTIC : {h} - RANDOM : {rpk[2]}")
                [nodes, RESULT, TIME] = main(file, K = rpk[2], R = rpk[0], P = rpk[1], H = h)
                data.append(f"{str(timedelta(seconds=TIME))[:-4] if len(str(timedelta(seconds=TIME))) == 14 else str(timedelta(seconds=TIME))} - {nodes}")
                if RESULT : result = RESULT
            data.append(f"{result if result else '-'}")
            writer.writerow(dict(zip(field_list, data)))

for file in ["anna-5","anna-8","david-5","david-8","homer-5","huck-5","huck-8","jean-5","jean-7","games120-5","games120-7","games120-9","miles250-6","miles250-7","miles250-8","miles500-5","miles750-5","miles1000-5","queen5-5-4","queen6-6-6","queen7-7-6"] :
    for k in [1,3,5] : main(file, K = k, R = 0.99, P = 25, H = 6)
