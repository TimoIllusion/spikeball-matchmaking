from multiprocessing import Process
from generate_matchups_excel_sp import main

if __name__ == "__main__":

    worker = 16

    processes = []
    for i in range(worker):
        p = Process(target=main)
        p.start()
        processes.append(p)
        
    for p in processes:
        p.join()
        
    print("Done")