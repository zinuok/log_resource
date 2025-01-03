#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# This file is part of the jetson_stats package (https://github.com/rbonghi/jetson_stats or http://rnext.it).
# Copyright (c) 2019 Raffaello Bonghi.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.



# ref: https://thispointer.com/python-get-list-of-all-running-processes-and-sort-by-highest-memory-usage/
from jtop import jtop, JtopException
import csv, argparse
import psutil
from time import sleep

# -------- variables -------- #
# process name list: used for total calculation
# example)
# vins-mono    : ['vins_estimator', 'feature_tracker', 'pose_graph']
# vins-fusion    : ['vins_node', 'loop_fusion_node']
# rovio        : ['rovio_node'] 
# msckf-vio    : ['nodelet'] 
# orb2-ros     : ['orb_slam2_ros_stereo'] 


# 논리 프로세서(코어) 수
num_cores = psutil.cpu_count(logical=True)

                                 
interval = 0.1           # time interval for each logging
# --------------------------- #



def initialize_cpu_percent(proc_list):

    for proc in psutil.process_iter(['name']):
        if proc.info['name'] in proc_list:
            try:
                proc.cpu_percent(interval=None)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    sleep(interval)




def get_proc(vo_name):
    if vo_name == "vins-mono":
        return ['vins_estimator', 'feature_tracker', 'pose_graph']
    if vo_name == "vins-fusion":
        return ['vins_node', 'loop_fusion_node']
    if vo_name == "rovio":
        return ['rovio_node'] 
    if vo_name == "msckf-vio":
        return ['nodelet']
    if vo_name == "msckf-vio-mono":
        return ['msckf_mono_node']
    if vo_name == "orb2-ros":
        return ['orb_slam2_ros_stereo'] 
    if vo_name == "kimera":
        return []

if __name__ == "__main__":
    # parse output file name
    parser = argparse.ArgumentParser()
    parser.add_argument('--save', action="store", dest="file", default="log.csv")
    parser.add_argument('--name', action="store", dest="vo", default="")

    # save True if arg is given
    parser.add_argument('--USE_GPU', action="store_true", default=False)

    args = parser.parse_args()
    
    proc_list = get_proc(args.vo)
    initialize_cpu_percent(proc_list)
    
    print(proc_list)
    f = open(args.file, 'w')
    wr = csv.writer(f)

    if args.USE_GPU:
        wr.writerow(['CPU %', 'Mem %', 'GPU %'])
        try:
            with jtop() as jetson:
                
                while True:
                    total_cpu = 0
                    total_mem = 0
                    # Iterate over all running process
                    for proc in psutil.process_iter():
                        try:
                            # Get process info.
                            info = proc.as_dict(attrs=['name', 'cpu_percent'])
                            if info['name'] in proc_list:
                                # calculate total CPU and Memory usage
                                total_cpu += info['cpu_percent']
                        
                                mem_rss_bytes = proc.memory_info().rss  # 여기서 직접 호출
                                mem_rss_mb = mem_rss_bytes / (1024 * 1024)
                                mem_rss_gb = mem_rss_mb / (1024)
                                total_mem += mem_rss_gb
                                
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                            pass
                        except KeyboardInterrupt:
                            print("Crtl+'C' interrupt")
                            # close(f)
                    
                    # log
                    stats = jetson.stats # get jetson GPU usage info

                    if total_cpu > 0:
                        print("cpu [%]: ", total_cpu, "mem [GB]: ", total_mem, "gpu [GB]: ", stats['GPU'])
                        wr.writerow([total_cpu, total_mem, stats['GPU']])
                    else:
                        print("cpu [%]: ", total_cpu, "mem []: ", total_mem, "  0(%)cpu => skip cpu logging")
                    sleep(interval)     
        except JtopException as e:
            print(e)



    else:
        wr.writerow(['CPU %', 'Mem %'])

        while True:
            total_cpu = 0
            total_mem = 0
            # Iterate over all running process
            for proc in psutil.process_iter():
                try:
                    # Get process info.
                    info = proc.as_dict(attrs=['name', 'cpu_percent'])
                    # print (info['name'])
                    if info['name'] in proc_list:
                        # calculate total CPU and Memory usage
                        cpu_usage_psutil = info['cpu_percent']
                        
                        print(cpu_usage_psutil, proc.cpu_percent(interval=interval))
                        usage_per_core_scale = cpu_usage_psutil
                        total_cpu += usage_per_core_scale
                        
                        
                        mem_rss_bytes = proc.memory_info().rss  # 여기서 직접 호출
                        mem_rss_mb = mem_rss_bytes / (1024 * 1024)
                        mem_rss_gb = mem_rss_mb / (1024)
                        total_mem += mem_rss_gb
                        
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                except KeyboardInterrupt:
                    print("Crtl+'C' interrupt")
                    # close(f)
            
            # log
            if total_cpu > 0:
                print("cpu [%]: ", total_cpu, "mem [GB]: ", total_mem)
                wr.writerow([total_cpu, total_mem])
            else:
                print("cpu: ", total_cpu, "mem: ", total_mem, "  0(%)cpu => skip cpu logging")
            sleep(interval)  

    # close file
    f.close()
    
    # close(f)
# EOF
