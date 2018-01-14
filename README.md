# Sombrero

## What is this?
Sombrero is a single module daemon manager used to manage nohup daemons on linux based operating systems. It can be useful for orchestrating many custom daemon processes and ensuring they can be recovered automatically in case of crash. It also provided a single interface for managing the daemon processes in Python.

## How do I use it?
In the `sombrero.py` module, you can define both the names and commands for your processes in the `daemon_dict`. Two simple example python processes have been included. You can also set the `nohup endpoints` if you wish to record logs from the daemons, as well as the `daemon_master_frequency` to set the frequency at which the manager will scan for stopped processes and restart them.

Once setup, simply run the sombrero as another nohup daemon. e.g.
`nohup python ./sombrero.py > /dev/null 2>&1 &`

## Tips
- If needed you can set multiple nohup endpoints to separate the logs from different processes.
- You can import the `restart_daemon` function in other modules to force processes restart based on other events.

## TODO
- Remove dependency on StringIO library to make sombrero python 2/3 compatible
