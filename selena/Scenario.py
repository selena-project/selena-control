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

import abc
import pprint
from CommandTools import CommandTools
import time


class Scenario(object):
    '''
    classdocs
    '''

    __metaclass__ = abc.ABCMeta
    MAX_NODES = 300


    def __init__(self):
        '''
        Constructor
        '''
        self.duration = 60  # 60 seconds default value
        self.name = None
        self.isInitialized = False
        self.EMU_NODES = {}
        self.NODES_BY_VMREF = {}
        self.LINKS_MATRIX = [[None]*Scenario.MAX_NODES for x in xrange(Scenario.MAX_NODES)]
        self.LINKS = []
        self.HUBS = []
        self.TDF = 1
        self.EXEC = CommandTools()
        #print "This is (base-class) Scenario"


    def newNode(self, pID, pName, pType, pNetifs, pCPUs, pCPUPin, pRam):
        node = {
                 "ID": pID,
                 "NAME": pName,
                 "TYPE": pType,
                 "NETIFS": pNetifs,

                 "XEN_CPUS": pCPUs,
                 "XEN_CPUPIN": pCPUPin,
                 "XEN_RAM": pRam,
                 "XEN_TEMPLATE_VDI": "",
                 "XEN_KERNEL": ['', '', ''],

                 "META_XEN_VMREF": "",
                 "META_XEN_DOMID":"",
                 "META_XEN_UUID" : "",
                 "META_XEN_NAME" : "",
                 "META_XEN_DESCRIPTION" : "",
                 "META_XEN_VBD": "",
                 "META_XEN_VDI": "",
                 "META_XEN_VIFS": [],

                 "GUEST_MGMT_IPADDR": "",
                 "GUEST_BIN_PATH": "",
                 "GUEST_POX_PATH": "",
                 "GUEST_TG_PATH": "",
                 "GUEST_INIT_SCRIPT": "",
                 "GUEST_REPORT_SCRIPT": ""
        }
        return node

    def newLink(self, pEdgeA, pEdgeB, pRate=None, pLatency=None):
        (nodeA, ifaceA) = pEdgeA
        (nodeB, ifaceB) = pEdgeB
        link = {    "NODE_A": nodeA,
                    "IFACE_A": ifaceA,
                    "NODE_B": nodeB,
                    "IFACE_B": ifaceB,
                    "RATE": pRate,
                    "LATENCY": pLatency,

                    "META_CONFIGURED": False,
                    "META_XEN_NETWORK": None
                }
        return link

    def newHub(self, pEdges, pRate=None, pLatency=None):
        hub = {"LINKS" : pEdges,
               "RATE": pRate,
               "LATENCY": pLatency,
               "META_CONFIGURED": False,
               "META_XEN_NETWORK": None
               }
        return hub


    def addNode(self, pNode):
        if len(self.EMU_NODES) >= Scenario.MAX_NODES:
            print "ERROR: Could not add node (%d, %s) in scenario. Limit of %d nodes is reached" % (pNode['ID'], pNode['NAME'], Scenario.MAX_NODES)
            return False
        if pNode['ID'] in self.EMU_NODES:
            print "ERROR: Could not add node (%d, %s) in scenario. ID must be unique" % (pNode['ID'], pNode['NAME'])
            return False
        # TODO: check for IP and MAC address conflicts
        # TODO: check for available physical RAM
        # TODO: check for IP and MAC address validity
        # TODO: check for IP settings validity
        # TODO: check for NodeType validity
        # A safe guard
        pNode['META_XEN_VMREF'] = ""
        pNode['META_XEN_DOMID'] = "-1"
        pNode['META_XEN_UUID'] = ""
        pNode['META_XEN_NAME'] = ""
        pNode['META_XEN_DESCRIPTION'] = ""
        pNode['META_XEN_VBD'] = ""
        pNode['META_XEN_VDI'] = ""
        pNode['META_XEN_VIFS'] = (len(pNode["NETIFS"])+1)*[None]
        self.EMU_NODES[pNode['ID']] = pNode
        return True


    def addLink(self, pLink):
        nodeA = nodeB = None
        # Check if both Node IDs exist in our scenario
        if pLink['NODE_A'] in self.EMU_NODES:
            nodeA = self.EMU_NODES[pLink['NODE_A']]
        else:
            print "ERROR: Could not add link (%d, %d) in scenario. Node %d doesn't exist" % (pLink['NODE_A'], pLink['NODE_B'], pLink['NODE_A'])
            return False
        if pLink['NODE_B'] in self.EMU_NODES:
            nodeB = self.EMU_NODES[pLink['NODE_B']]
        else:
            print "ERROR: Could not add link (%d, %d) in scenario. Node %d doesn't exist" % (pLink['NODE_A'], pLink['NODE_B'], pLink['NODE_B'])
            return False
        # Check if the described interfaces exist
        if  len(nodeA['NETIFS']) <= pLink['IFACE_A'] or\
            len(nodeB['NETIFS']) <= pLink['IFACE_B']:
            print "ERROR: Could not add link (%d, %d) in scenario. The provided interface indices are non-existent" % (pLink['NODE_A'], pLink['NODE_B'])
            return False
        # Check if link already exists
        if self.linkExists(pLink):
            print "ERROR: Could not add link (%d, %d) in scenario. It already exists" % (pLink['NODE_A'], pLink['NODE_B'])
            return False
        # Safe guard
        pLink['META_CONFIGURED'] = False
        pLink['META_XEN_NETWORK'] = None
        # Finally add the link in the matrix
        # Add in the quick lookup array (both sides of the main diagonal, with values properly swapped)
        self.LINKS.append(pLink)
        #self.LINKS.append(pLink.copy)
        return True

    def addHub(self, pHub):
        nodeA = nodeB = None
        # Check if both Node IDs exist in our scenario

	for (node, iface) in pHub['LINKS']:
            if node in self.EMU_NODES:
                nodeObj = self.EMU_NODES[node]
            else:
                print "ERROR: Could not add link hub in scenario. Node %d doesn't exist" % ( node)
                return False
        # Check if the described interfaces exist
        if  len(nodeObj['NETIFS']) <= iface:
            print "ERROR: Could not add link hub in scenario. The provided interface indices are non-existent"
            return False
        # Safe guard
        pHub['META_CONFIGURED'] = False
        pHub['META_XEN_NETWORK'] = None
        # Finally add the link in the matrix
        # Add in the quick lookup array (both sides of the main diagonal, with values properly swapped)
        self.HUBS.append(pHub)
        #self.LINKS.append(pLink.copy)
        return True

    def getNode_ById(self, pId):
        if pId in self.EMU_NODES:
            return self.EMU_NODES[pId]
        return None
    def getNodeVMRef_ById(self, pId):
        node = self.getNode_ById(pId)
        return None if node is None else node['META_XEN_VMREF']

    def isNodeConfigured(self, pId):
        if self.EMU_NODES[pId]["META_XEN_VMREF"]:
            return True
        return False


    def addNode_VifRef(self, pId, pVifRef, pVifIdx):
        if not pId in self.EMU_NODES:
            return False
        self.EMU_NODES[pId]['META_XEN_VIFS'][pVifIdx] = pVifRef
        return True


    def markLinkAsConfigured_old(self, pIdA, pIdB, pNet):
        if not self.linkExists_old(pIdA, pIdB):
            print "WARNING: Trying to mark a non-existent link as configured (%d--%d)" % (pIdA, pIdB)
            return False
        self.LINKS_MATRIX[pIdA][pIdB]['META_CONFIGURED'] = True
        self.LINKS_MATRIX[pIdA][pIdB]['META_XEN_NETWORK'] = pNet
        self.LINKS_MATRIX[pIdB][pIdA]['META_CONFIGURED'] = True
        self.LINKS_MATRIX[pIdB][pIdA]['META_XEN_NETWORK'] = pNet
        return True

    def linkExists_old(self, pIdA, pIdB):
        return not ((self.LINKS_MATRIX[pIdA][pIdB] is None) and (self.LINKS_MATRIX[pIdB][pIdA] is None))

    def linkExists(self, pLink):
        for link in self.LINKS:
            if  (pLink['NODE_A'] == link['NODE_A']) and (pLink['IFACE_A'] == link['IFACE_A']) or\
                (pLink['NODE_A'] == link['NODE_B']) and (pLink['IFACE_A'] == link['IFACE_B']) or\
                (pLink['NODE_B'] == link['NODE_A']) and (pLink['IFACE_B'] == link['IFACE_A']) or\
                (pLink['NODE_B'] == link['NODE_B']) and (pLink['IFACE_B'] == link['IFACE_B']):
                return True
        return False

    def isLinkConfigured_old(self, pIdA, pIdB):
        if not self.linkExists_old(pIdA, pIdB):
            return False
        return (self.LINKS_MATRIX[pIdA][pIdB]['META_CONFIGURED']) or (self.LINKS_MATRIX[pIdB][pIdA]['META_CONFIGURED'])




    def getPrettyString(self):
        return "\n====Scenario %s====\nEMU_NODES = %s \nLINKS = %s\nduration = %s\ninitialized = %s\n" % (self.name, self.EMU_NODES, self.LINKS, self.duration, self.isInitialized)

    def prettyPrint(self):
        print "\n-------------  Scenario name: %s ------------" % (self.name)
        print "Duration =  %s" % (self.duration)
        print "Initialized = %s" % (self.isInitialized)
        print "EMULATION NODES:"
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.EMU_NODES)
        print "EMULATION LINKS:"
        print self.linksToPrettyString()

    def linksToPrettyString_old(self):
        strLinks = ""
        for i in range(0,Scenario.MAX_NODES):
            for j in range(0,Scenario.MAX_NODES):
                if not self.LINKS_MATRIX[i][j] is None: # and i < j:
                    strLinks += "** Link %d--%d **\n%s\n" % (i,j,str(self.LINKS_MATRIX[i][j]))
        return strLinks

    def linksToPrettyString(self):
        strLinks = ""
        for link in self.LINKS:
            strLinks += "** Link %d(%d)--%d(%d) **\n" % (link['NODE_A'], link['IFACE_A'], link['NODE_B'], link['IFACE_B'])
        return strLinks


    def getMaxNodes(self):
        return self.MAX_NODES


    def blockWaitingXSLock(self, pXsPath, pTimeoutSec, pStep):
        count = pTimeoutSec
        while count > 0:
            (_, out) = self.EXEC.runCommand('sudo xenstore-read %s/lock'%(pXsPath))
            if out.strip() == 'FREE':
                return True
            else:
                time.sleep(pStep)
        return False

    def pushCommand(self, pNodeId, pCmd):
        #print "Sending command to Node %d:\n%s" % (pNodeId, pCmd)
        #return True
        node = self.getNode_ById(pNodeId)
        if not node or int(node['META_XEN_DOMID']) < 1 or len(pCmd) > 4050:
            print "ERROR: Can't push command to node with ID " + str(pNodeId)
            return None
        xsPath = '/local/domain/' + node['META_XEN_DOMID'] + '/Selena'
        # Obtain the lock
        if not self.blockWaitingXSLock(xsPath, 10, 1):
            print "ERROR: Can't push command to node with ID " + str(pNodeId) + ". Couldn't obtain the XS lock."
            return None
        # Write the xenstore records and wait the guest to become ready
        print "Pushing command to VM %s(%d) uuid=%s domid=%s. Waiting for response:\n%s"  % (node['NAME'], node['ID'], node['META_XEN_UUID'], node['META_XEN_DOMID'] ,pCmd)
        self.EXEC.runCommand('sudo xenstore-write ' + xsPath + '/cmd \'' + pCmd + "\'")
        # Wait until lock is released from client in the guest
        if not self.blockWaitingXSLock(xsPath, 10, 1):
            print "ERROR: VM %s(%d) uuid=%s domid=%s does not respond" % (node['NAME'], node['ID'], node['META_XEN_UUID'], node['META_XEN_DOMID'])
            return None
        (_, out) = self.EXEC.runCommand('sudo xenstore-read ' + xsPath + '/response ')
        print "VM %s(%d) uuid=%s node=%s responded: \n%s" % (node['NAME'], node['ID'], node['META_XEN_UUID'], node['META_XEN_DOMID'], out.replace('\\n', '\n').replace('\\t', '\t'))
        return

    # Other concrete implementations of the Scenario must implement this method
    # to provide an emulation description (nodes and links)
    @abc.abstractmethod
    def initScenario(self):
        if self.isInitialized:
            print "Scenario %s is already initialized." % (self.name)
            return False
        self.isInitialized = True
        return True


    # Other concrete implementations of the Scenario must implement this method
    # to start/run the emulation
    @abc.abstractmethod
    def runScenario(self):
        if not self.isInitialized:
            print "Cannot run the Scenario (%s) because it has not been initialized." % (self.name)
            return False
        return True



