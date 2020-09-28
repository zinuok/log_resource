# log_resource

***
This is python script logs CPU, Memory, and GPU usage for NVIDIA Jetson board. <br>
There are two files for logging the usages
+ cpu_mem_logger.py: total CPU usage and Memory usage for specified processes are logged
+ jetson_stats/examples/resource_logger.py: total CPU usage and Memory usage for specified processes  and total GPU usage are logged <br>total CPU usage and Memory usage for specified processes are logged
<br>
For second script, I modified and add a script 'resource_logger.py' into the original package from [jetson_stats]("https://github.com/rbonghi/jetson_stats")
***
<br><br>

## Install
```
$ pip install psutil
$ sudo -H pip install -U jetson-stats
$ git clone https://github.com/zinuok/log_resource.git
```

## Run
```
$ cd ~/jetson_stats/examples
$ python resource_logger.py --name [ourput csv file name]
```

