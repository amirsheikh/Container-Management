import docker
import os
import re
import time
import threading
import subprocess
global cmd
cmd = []

def submitTask(cmd,tasks,id):
    command = cmd.pop(0)
    command = re.sub('[{}<>]', '', command).split(', ')
    requests = []
    i = 0
    while i < len(command) - 2:
        requests.append(command[i] + " " + command[i + 1])
        i += 2
    output_directory = command[-1]
    tasks[id] = []
    for r in requests:
        r = r.split(" ")
        input = r[1]
        opt = r[0]
        tasks[id].append([opt, input, output_directory])
    id = id + 1
    print('     Request submitted. ID ' + str(id - 1))
    return cmd,tasks,id

def assigendContainer(current_id,con):
    print('>>> Assigend to ' + con + ' and currentID ' + str(current_id))
    container_job = current_id
    current_id = current_id + 1
    return container_job , current_id

def executeTask(tasks,container_job, con):
    current_task = tasks[container_job]
    if(len(current_task) > 0):
        task = current_task.pop(0)
        print('Job for ' + str(container_job) +
                ' in ' +con + ' ' + task[0])
        os.system('docker cp ' + task[1][1:] + ' ' + con + ':usr/src/app')
        os.system('docker exec -d ' + con + ' python ' +
                    task[0] + '.py ' + task[1].split('/')[-1])
        os.system('docker cp '+ con +':usr/src/app/' +
                    task[0] + '.txt ' + task[2][1:])
    else:
        print("    " + con + " job request finished. ID " +
                str(container_job)) 
        container_job = ''

    return tasks , container_job

def operate():
    global cmd
    tasks = {}
    id = 0
    current_id = 0
    container1_job = ''
    container2_job = ''
    container3_job = ''

    while(True):
        if(len(cmd) > 0):
            cmd,tasks,id = submitTask(cmd,tasks,id)

        if(current_id in tasks or container1_job != "" or container2_job != "" or container3_job != ""):
            if(container1_job == '' and current_id in tasks):
                container1_job,current_id = assigendContainer(current_id,"con1")
            if(container2_job == '' and current_id in tasks):
                container1_job,current_id = assigendContainer(current_id,"con2")
            if(container3_job == '' and current_id in tasks):
                container1_job,current_id = assigendContainer(current_id,"con2")

            result_con1 = subprocess.check_output(
                "docker exec con1 ps", shell=True).decode()

            result_con2 = subprocess.check_output(
                "docker exec con2 ps", shell=True).decode()

            result_con3 = subprocess.check_output(
                "docker exec con3 ps", shell=True).decode()

            if("python" not in result_con1 and container1_job != ''):
                tasks,container1_job = executeTask(tasks,container1_job,"con1")
                
            if("python" not in result_con2 and container2_job != ''):
                tasks,container1_job = executeTask(tasks,container1_job,"con1")
                
            if("python" not in result_con3 and container3_job != ''):
                tasks,container1_job = executeTask(tasks,container1_job,"con1")
                

if __name__ == "__main__":
    t1 = threading.Thread(target=operate)
    t1.start()
    while True:
        command = input("Enter your command (Type '0' to exit): ")
        if command == '0':
            print('\nProgram exited successfully.\n')
            break
        cmd.append(command)
