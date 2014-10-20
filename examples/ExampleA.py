# -*- coding: utf-8 -*-
#---------------------------------------------------------------------
#   Copyright (C) 2014 Dimosthenis Pediaditakis.
#
#   All rights reserved.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions
#   are met:
#     1. Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#   THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
#   ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#   ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
#   FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#   DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
#   OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#   HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#   LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
#   OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
#---------------------------------------------------------------------


from selena.Scenario import Scenario
#from ExpManagerServer import ExpManagerServer
#import signal
import time



class ExampleA(Scenario):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        super(ExampleA, self).__init__()
        self.TDF = 1
        self.cLinkSpeed = 1000


    def initScenario(self):
        if not super(ExampleA, self).initScenario():
            return False
        #------------------------------------------
        #  Add here the details of the emulation
        #------------------------------------------
        self.name = "ExampleA"

        latency = 0.02

        #------------------------------------------
        #   Adding the nodes: 1x client, 3x servers, 1x controller, 1x OF switch
        #------------------------------------------

        # Add the hosts
        self.addNode(self.newNode(0, 'hostA', 'LINUX_HOST', [(1000, "fe:ff:ff:01:01:01", "10.0.1.1", "255.255.255.0", "10.0.1.2")], 1, '1', 536870912))
        self.addNode(self.newNode(1, 'hostB', 'LINUX_HOST', [(1000, "fe:ff:ff:01:01:02", "10.0.1.2", "255.255.255.0", "10.0.1.1")], 1, '1', 536870912))

        # Add the OF switch
        self.addNode(self.newNode(2,
                                  'switch',
                                  'LINUX_OVS',
                                  [(500,  "fe:ff:ff:00:02:02", "", "", ""),
                                   (500,  "fe:ff:ff:00:02:03", "", "", "")
                                  ],
                                  1,
                                  '1',
                                  536870912))

        #------------------------------------------
        #  Adding the links:
        #
        #            HostA
        #              |
        #              |
        #            Switch
        #              |
        #              |
        #            HostB
        #------------------------------------------

        # HostA <--> Switch
        self.addLink(self.newLink( (0, 0),   (2,0),   self.cLinkSpeed, latency))

        # HostB <--> Switch
        self.addLink(self.newLink( (1, 0),   (2,1),   self.cLinkSpeed, latency))

        return True


    def runScenario(self):
        print "\n------------------------------------------"
        print "**     Running scenario %s     **" % (self.name)
        print "\n------------------------------------------\n"
        self.runExperiment()

    def runExperiment(self):
        self.setupNetworking()
        self.setupNetworkEmulation()
        # ----------------------------------------
        #  The commands of the experiment go here
        # ----------------------------------------
        try:
            self.pushCommand(0, "netperf -H 10.0.1.2 -C -c -t TCP_STREAM -l 60 -D 1 > /tmp/throughput.log")
            self.mySleep(60)
        except KeyboardInterrupt:
            return
        # -------------------
        print '----------  END OF EXPERIMENT  -----------------'






    def getArpCmd(self, pDev, pIp, pMac):
        return "ip link set dev %s arp off; ip n flush dev %s; ip n add %s lladdr %s dev %s nud perm" % (pDev, pDev, pIp, pMac, pDev)

    def getLinuxInterfaceCmd(self, pIndex, pAddress, pNetMask, pDefGw, pQsize):
        cmdLine = ''
        linuxIface = 'eth'+str(pIndex+1)   # SOS: pIndex+1 because device 0 is the management interface
        if pAddress: # host
            cmdLine = "ifconfig %s %s netmask %s" % (linuxIface, pAddress, pNetMask)
            cmdLine += "; ifconfig %s txqueuelen %s" % (linuxIface, str(pQsize))
            cmdLine += "; ethtool -K %s tso off tx off rx off" % (linuxIface)
            if pDefGw:
                cmdLine += "; ip route del 0/0"
                cmdLine += "; route add default gw %s %s" % (pDefGw, linuxIface)
        else:  # switch
            cmdLine = "ifconfig %s up" % (linuxIface)
            cmdLine += "; ifconfig %s txqueuelen %s" % (linuxIface, str(pQsize))
            cmdLine += "; ethtool -K %s tso off tx off rx off" % (linuxIface)
        return (linuxIface, cmdLine)

    def getLinkEmulationCmd(self, pIndex, pQsize, pRate, pR2q, pMtu=1500, pDelay=None):
        linuxIface = 'eth'+str(pIndex+1)   # SOS: pIndex+1 because device 0 is the management interface
        cmdLine =  "tc qdisc del root dev %s ; " % (linuxIface)
        if pDelay:
            cmdLine += "tc qdisc add dev %s root handle 1: netem delay %sms ; " % (linuxIface, str(pDelay))
            #cmdLine += "tc qdisc add dev %s parent 1:1 pfifo limit %s ; " % (linuxIface, str(pQsize))
        #cmdLine += "tc qdisc add dev %s root handle 1: htb default 10 r2q %d;" % (linuxIface, pR2q)
        #cmdLine += "tc class add dev %s parent 1: classid 10 htb rate %dMbit ceil %dMbit mtu %d;" % (linuxIface, pRate, pRate, pMtu)
        cmdLine += "ifconfig %s txqueuelen %s ; " % (linuxIface, str(pQsize))
        cmdLine += "ethtool -K %s tso off tx off rx off" % (linuxIface)
        return cmdLine

    def setupNetworking(self):
        # Set all the network interfaces
        for nId, node in self.EMU_NODES.items():
            for ifIndex in range(0, len(node['NETIFS'])):
                (_, cmd) = self.getLinuxInterfaceCmd(ifIndex, node['NETIFS'][ifIndex][2], node['NETIFS'][ifIndex][3], node['NETIFS'][ifIndex][4], node['NETIFS'][ifIndex][0])
                self.pushCommand(nId, cmd)
                time.sleep(0.5)
            time.sleep(0.5)
            if node['TYPE'] == 'LINUX_OVS':
                bridge = 'br0'
                #self.pushCommand(nId, 'ovs-vsctl del-br %s; ovs-vsctl add-br %s' % (bridge, bridge))
                self.pushCommand(nId, 'ovs-vsctl del-br %s; ovs-vsctl add-br %s; ovs-vsctl del-fail-mode %s; ovs-vsctl set-fail-mode %s secure' % (bridge, bridge, bridge, bridge))
                time.sleep(0.5)
                for ifIndex in range(0, len( node['NETIFS'])):
                    (linuxIface, _) = self.getLinuxInterfaceCmd(ifIndex, node['NETIFS'][ifIndex][2], node['NETIFS'][ifIndex][3], node['NETIFS'][ifIndex][4], node['NETIFS'][ifIndex][0])
                    self.pushCommand(nId, 'ovs-vsctl add-port %s %s' % (bridge, linuxIface))
                    time.sleep(0.5)
        time.sleep(2)

    def setupNetworkEmulation(self):
        # Set all the network interfaces
        for link in self.LINKS:
            #if link['NODE_A'] != 0 and link['NODE_B'] != 0:
            delay = link['LATENCY']
            if delay:
                nodeA = self.EMU_NODES[link['NODE_A']]
                ifA = link['IFACE_A']
                qsizeA = nodeA['NETIFS'][ifA][0]
                nodeB = self.EMU_NODES[link['NODE_B']]
                ifB = link['IFACE_B']
                qsizeB = nodeB['NETIFS'][ifB][0]
                rate = link['RATE']
                if (nodeA['TYPE'] != 'LINUX_OVS'): # do not set the switch with link delays
                    # Set the first interface of the link
                    cmd = self.getLinkEmulationCmd(ifA, qsizeA, None, None, None, delay) # for TDF > 1 use MTU = 1500
                    self.pushCommand(nodeA['ID'], cmd)
                    time.sleep(0.5)
                if nodeB['TYPE'] != 'LINUX_OVS':
                    # Set the second interface of the link
                    cmd = self.getLinkEmulationCmd(ifB, qsizeB, None, None, None, delay) # for TDF > 1 use MTU = 1500
                    self.pushCommand(nodeB['ID'], cmd)
                    time.sleep(0.5)
        time.sleep(2)

    def mySleep(self, pSec):
        return time.sleep(pSec*self.TDF)