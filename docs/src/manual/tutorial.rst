.. _selena_tutorial:

Selena Tutorial
===============

SELENA provides a simple Python API which allows easy description, deployment
automation and execution of experiments. The API builds on top of the XAPI
service and provides enhances configuration primitives to describe network
topologies, resource policies and execute commands on VMs. 

In order to describe a SELENA experiment, the experimenter must extend the
Scenario class and implement custom methods for two functions: The
*init_scenario* function, describing the topology of the experiment, and the
*run_scenario* function, describing the sequence of commands of the
experiment on the guest VM.

In order to walk the user through the required steps, we use a simple a simple
topology with two hosts interconnected through a switch, running a netperf
session, depicted in the following figure.

.. image:: _static/simple-topology.png

SELENA scenario
---------------

In order to run an experiment, a user must implement a Python class which
inherits the Scenario class. The custom scenario class must follow a specific
naming pattern. Specifically, the filename must be the same as the name of the
Scenario class. In this tutorial, we create a Tutorial class which must be
saved in a Tutorial.py file in order to allow execution with the SELENA
execution tools.

A python script that can replicate the previous topology and experimental
scenario is the following:::

    from Scenario import Scenario, NodeTypes
    import time
    
    
    class Tutorial(Scenario):
        def __init__(self):
            super(Tutorial, self).__init__()
    
        def initScenario(self):
            if not super(Tutorial, self).initScenario():
                return False
            self.name = "Tutorial"
    
            # Add the server
            self.addNode(self.newNode(
                0,                        # Unique id for the Node
                'server',                 # Name of the node
                NodeTypes.LINUX_HOST,     # The node is a Linux host
                # definition of the list of interfaces and respective
                # network configuration primitives
                [(1000, "RANDOM", "10.0.0.254", "255.255.255.0", "10.0.0.1")],
                # Nunber of vCPUs used by the node
                2,
                # Identification of the core on which the node is Pinned
                '4',
                # Available RAM for the node
                536870912))
    
            # Add the clients
            self.addNode(self.newNode(1, 'client', NodeTypes.LINUX_HOST,
                                      [(1000, "RANDOM", "10.0.0.1", "255.255.255.0", "10.0.0.254")],
                                      1, '6,7', 536870912))
    
            # Switch definition. The switch has a different node type and
            # has two interfaces, one for each host, which don't have any
            # IP configuration.
            self.addNode(self.newNode(2, 'switch', NodeTypes.LINUX_OVS,
                                      [(1000, "RANDOM", "", "", ""), (1000, "RANDOM", "", "", "")],
                                      1, '5', 536870912))
    
            # link between client and switch
            self.addLink(self.newLink((1, 0), (2, 1), 1000, 0.1))
            # link between server and switch
            self.addLink(self.newLink((0, 0), (2, 0), 1000, 0.1))
    
            return True
    
        def runScenario(self):
            try:
                # A method to configure each device queue sizes and
                # disable network optimizations and enable the openvswitch
                # instance.
        	    self.setupNetworking()
                # A method to configure link delays.
        	    self.setupNetworkEmulation()

                # Once everything is setted up, we run a command to run the 
                # netperf session and output statistics in a file.
                self.pushCommand(1, "netperf -H 10.0.0.254 -C -c -t TCP_STREAM -l 60 -D 1 > /tmp/throughput.log")

                # wait for the emulation to complete and return to terminate
                # the experiment.
                time.sleep(60)
            except KeyboardInterrupt:
                return
    
        def getLinuxInterfaceCmd(self, ix, addr, mask, gw, queue):
            # interface 0 is the management. subsequent interfaces follow a
            # naming similar to what is used in the link definitions.
            intf = 'eth'+str(ix+1)
            cmdLine = "ifconfig %s up" % (intf)
            cmdLine += "; ifconfig %s txqueuelen %s" % (intf, str(queue))
            cmdLine += "; ethtool -K %s tso off tx off rx off" % (intf)
            if addr:
                cmdLine = "ifconfig %s %s netmask %s" % (intf, addr, mask)
                if gw:
                    cmdLine += "; ip route del 0/0"
                    cmdLine += "; route add default gw %s %s" % (gw, intf)
            return (intf, cmdLine)
    
        def setupNetworking(self):
            # Setup device interface and port grouping in the switch.
            for nId, node in self.EMU_NODES.items():
                for ix in range(0, len(node['NETIFS'])):
                    dev = node['NETIFS'][ix]
                    (_, cmd) = self.getLinuxInterfaceCmd(ix, dev[2], dev[3], dev[4], dev[0])
                    self.pushCommand(nId, cmd)
                if node['TYPE'] == NodeTypes.LINUX_OVS:
                    bridge = 'br0'
                    self.pushCommand(nId, 'ovs-vsctl del-br %s; ovs-vsctl add-br %s' % (bridge, bridge))
                    for ix in range(0, len(node['NETIFS'])):
                        dev = node['NETIFS'][ix]
                        (intf, _) = self.getLinuxInterfaceCmd(ix, dev[2], dev[3], dev[4], dev[0])
                        self.pushCommand(nId, 'ovs-vsctl add-port %s %s' % (bridge, intf))
            time.sleep(5)
    
        def getLinkEmulationCmd(self, ix, rate, delay=None):
            # configure an emulation of the link delay.
            intf = 'eth'+str(ix+1)
            cmdLine = "tc qdisc del root dev %s ; " % (intf)
            if delay:
                cmdLine += "tc qdisc add dev %s root handle 1: netem delay %sms ; " % (intf, str(delay))
            return cmdLine
    
        def setupNetworkEmulation(self):
            # Set all the network interfaces
            for link in self.LINKS:
                delay = link['LATENCY']
                if delay:
                    nodeA = self.EMU_NODES[link['NODE_A']]
                    ifA = link['IFACE_A']
                    nodeB = self.EMU_NODES[link['NODE_B']]
                    ifB = link['IFACE_B']
                    rate = link['RATE']

                    # we only configure link latencies on the edge nodes
                    # of the host.
                    if (nodeA['TYPE'] != NodeTypes.LINUX_OVS):
                        # Set the first interface of the link
                        cmd = self.getLinkEmulationCmd(ifA, rate, delay)
                        self.pushCommand(nodeA['ID'], cmd)
                    if nodeB['TYPE'] != NodeTypes.LINUX_OVS:
                        # Set the second interface of the link
                        cmd = self.getLinkEmulationCmd(ifB, rate, delay)
                        self.pushCommand(nodeB['ID'], cmd)
            time.sleep(5)

As mentioned earlier a SELENA experimental definition must extend the Scenario
class and implement two main functions: `init_scenario` and `run_scenario`. The
init_scenario method must initialize the topology of the network. When the
function is invoked the SELENA instance has only connected to the XEN server
and awaits the topology in order to map experimental nodes in guest VMs. The
Scenario class provides four methods to specify the topology of the experiment
of the network. The newNode and addNode methods allow the experimenter to
define the hosts of the topology along with the available interfaces and
address configurations. Each node has a unique id and string name, defined by
the experimenter, a node type, summarised in the table below, an array with
network interfaces and CPU number and affinity and memory limitations for each
guest. Furthermore, in order to define the topology links the SELENA API
provides the commands addLink and newLink. Each link in the SELENA abstraction
consists of node and interface index pairs and the API allows the user to define
the link bandwidth and latency. 

In the case of this tutorial, our sample code configure two nodes with 1 interface, 
which represent the client and the server of our example, and 1 node with 2 interfaces,
which will represent the switch of the topology. Furthermore, the method defines 
two links, connecting the first interface of the client and server with an interface 
of the switch.

+-----------------+---------------------------------+--------------------------------+
| **NodeTypes**   |      **Configuration**          |    **Purpose**                 |
+=================+=================================+================================+
| LINUX_HOST      | Linux 3.10.11, Debian Wheezy    | Simple end-host to run traffic |
|                 |                                 | generators and applications    |
+-----------------+---------------------------------+--------------------------------+
| LINUX_OVS       | Linux 3.10.11, Debian Wheezy,   | A switch abstraction running   |
|                 | Open vSwitch 1.4.2              | an instance of open vSwitch    |
+-----------------+---------------------------------+--------------------------------+
| MIRAGE_SWITCH   | Mirage 1.0, ocaml-openflow      | A Mirage based switch emulator |
+-----------------+---------------------------------+--------------------------------+
| OF_CONTROLLER   | Linux 3.10.11, Debian Wheezy,   | A node configure to run all    |
|                 | Java 1.6, Nox, Pox, Floodlight, | popular OpenFlow controllers   |
|                 | FlowVisor                       |                                |
+-----------------+---------------------------------+--------------------------------+
| LINUX_WEBSERVER | Linux 3.10.11, Debian Wheezy,   | An experimental containing all |
|                 | Apache 2.0, Nginx, PHP, MySQL,  | required software to run web   |
|                 | memcached, redis                | applications                   |
+-----------------+---------------------------------+--------------------------------+

The run_scenario method is executed once the topology is up and configured and the nodes 
have all connected to the signalling service in Dom0. The SELENA abstraction allows 
a Scenario class to manipulate the guest and execute commands within them. In order to 
achieve this, the scenario object has the pushCmd method which runs a command in 
the guest with the respective node index. In the case of the tutorial, the run_scenario
executes in the client node a netperf command towards the controller. 


