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
import time

class ExampleB(Scenario):
    '''
    Quick test to check if network hubs work.
    '''
    def __init__(self):
        '''
        Constructor
        '''
        super(ExampleB, self).__init__()
        self.TDF = 1
        self.cLinkSpeed = 1000


    def initScenario(self):
        if not super(ExampleB, self).initScenario():
            return False
        #------------------------------------------
        #  Add here the details of the emulation
        #------------------------------------------
        self.name = "ExampleB"
        latency = 0.02
        #------------------------------------------
        #   Adding the nodes: 2x servers, 2x clients
        #------------------------------------------
        vif = [(1000, "fe:ff:ff:01:01:01", "10.0.1.1", "255.255.255.0", "10.0.1.2")]
        self.addNode(self.newNode(0, 'hostA', 'LINUX_HOST', vif, 1, '1', 536870912))
        vif = [(1000, "fe:ff:ff:01:01:02", "10.0.1.2", "255.255.255.0", "10.0.1.1")]
        self.addNode(self.newNode(1, 'hostB', 'LINUX_HOST', vif, 1, '1', 536870912))
        vif = [(1000, "fe:ff:ff:01:01:03", "10.0.1.3", "255.255.255.0", "10.0.1.1")]
        self.addNode(self.newNode(2, 'hostC', 'LINUX_HOST', vif, 1, '1', 536870912))
        vif = [(1001, "fe:ff:ff:01:01:04", "10.0.1.4", "255.255.255.0", "10.0.1.1")]
        self.addNode(self.newNode(3, 'hostD', 'LINUX_HOST', vif, 1, '1', 536870912))
        #------------------------------------------
        #  Adding the links:
        #
        #            HostA HostB
        #              |     |
        #              |     |
        #              +-----+
	#              |     |
        #              |     |
        #            HostC HostD
        #------------------------------------------
        self.addHub(self.newHub( [(0, 0), (1,0), (2,0),  (3,0)], self.cLinkSpeed, latency))
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
            self.pushCommand(0, "netperf -H 10.0.1.3 -C -c -t TCP_STREAM -l 60 -D 1 > /tmp/throughput.log")
            self.pushCommand(1, "netperf -H 10.0.1.4 -C -c -t TCP_STREAM -l 60 -D 1 > /tmp/throughput.log")
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
                (_, cmd) = self.getLinuxInterfaceCmd(ifIndex, node['NETIFS'][ifIndex][2],
                                                     node['NETIFS'][ifIndex][3], node['NETIFS'][ifIndex][4],
                                                     node['NETIFS'][ifIndex][0])
                self.pushCommand(nId, cmd)
                time.sleep(0.5)
            time.sleep(0.5)
        time.sleep(2)

    def setupNetworkEmulation(self):
        # Set all the network interfaces
        for hub in self.HUBS:
            #if link['NODE_A'] != 0 and link['NODE_B'] != 0:
            delay = hub['LATENCY']
            rate = hub['RATE']
            if delay:
                for (node, ifIx) in hub["LINKS"]:
                    node = self.EMU_NODES[node]
                    if (node['TYPE'] != 'LINUX_OVS'): # do not set the switch with link delays
                        # Set the first interface of the link
                        cmd = self.getLinkEmulationCmd(ifIx, 1002, None, None, None, delay) # for TDF > 1 use MTU = 1500
                        self.pushCommand(node['ID'], cmd)
                        time.sleep(0.5)
        time.sleep(2)

    def mySleep(self, pSec):
        return time.sleep(pSec*self.TDF)
