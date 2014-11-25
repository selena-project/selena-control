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


"""
Selena module
=============
The main module for the selena emulation control.
"""

from selena.SelenaLogger import slog, LOG_LEVELS, S_DEBUG, S_INFO, S_WARN, S_ERROR, S_INFO, S_CRIT
from XcpManager import XcpManager
from CommandTools import CommandTools
import sys
import time
from Singleton import Singleton
from selena.TemplatesDB import templatesDB
import os


def __doExit(message=None):
        """
        Exits the program return 1 as error status and printing a message.

        :param message: The message to print to standard output before exiting Selena
        """
        if not message:
            print "Error! Exiting Selena"
        else:
            print "Error! Exiting Selena: %s" % message
        sys.exit(1)

class Selena(object):
    """
    This is the main Selena Class
    """
    __metaclass__ = Singleton

    def __init__(self, selena_config, **kwargs):
        """
        Selena constructor
        Creates the main instance of the Selena module that controls the emulation from
        Dom0 (control domain) of Xen.

        :param selena_config: The configuration dictionary, normally constructed from a JSON configuration file
        :param kwargs:
            *package (str)*: The name of the package in which the main Selena module is located (meta-info)
            *version (str)*: The expected version of Selena
        :return: A new instance of Selena if called first time (singleton pattern).
        """

        for key in kwargs:
            setattr(self, key, kwargs[key])

        # Initialize Selena's configuration based on the informaiton retrieved form the JSON files
        Selena.SELENA_VM_KEYWORD = str(selena_config['SelenaMetaInfo']['SELENA_VM_KEYWORD'])
        Selena.SELENA_NET_KEYWORD = str(selena_config['SelenaMetaInfo']['SELENA_NET_KEYWORD'])
        Selena.SELENA_VDI_KEYWORD = str(selena_config['SelenaMetaInfo']['SELENA_VDI_KEYWORD'])
        Selena.SELENA_VBD_KEYWORD = str(selena_config['SelenaMetaInfo']['SELENA_VBD_KEYWORD'])
        Selena.SELENA_MGMT_NET_NAME = str(selena_config['SelenaManagementNet']['SELENA_MGMT_NET_NAME'])
        Selena.SELENA_MGMT_NET_IP = str(selena_config['SelenaManagementNet']['SELENA_MGMT_NET_IP'])
        Selena.SELENA_MGMT_NETADDR = str(selena_config['SelenaManagementNet']['SELENA_MGMT_NETADDR'])
        Selena.SELENA_MGMT_NET_MASK = str(selena_config['SelenaManagementNet']['SELENA_MGMT_NET_MASK'])
        Selena.XCP_url = str(selena_config['XenServerConfig']['XCP_url'])
        Selena.XCP_uname = str(selena_config['XenServerConfig']['XCP_uname'])
        Selena.XCP_passwd = str(selena_config['XenServerConfig']['XCP_passwd'])
        # Print the configuration
        for member in dir(Selena):
            if "SELENA" in member or "XCP" in member:
                S_DEBUG("DDD: %s = %s", member, str(getattr(Selena, member)))
        # Create the instance of the XcpManager (used to interact with the Xen API)
        self.xcpManager = XcpManager(Selena.XCP_url, Selena.XCP_uname, Selena.XCP_passwd)
        # The object used to execute shell commands
        self.EXEC = CommandTools()
        # The pool of VMs categorized by template
        self.XEN_VM_POOL = {}
        for tpl in templatesDB.keys():
            self.XEN_VM_POOL[tpl] = []
        # The pool of Xen networks
        self.XEN_NET_POOL = []

    def stopAllRunningVMs(self, pForce=False):
        """
        Stops all the VMs that are currently in running state on the Xen server
        :param pForce: Force shutdown, do not wait for VMs to exit gracefully (boolean type)
        """
        S_INFO("Stopping all running VMs")
        runningVMs = self.xcpManager.getRunningVMs()
        for vm in runningVMs:
            self.haltVM(vm, pForce)

    def haltVM(self, pRef, pForce=False):
        """
        Stops the specified VM
        :param pRef: the OpaqueRef for the VM to be shut down
        :param pForce: Force shutdown, do not wait for the VM to exit gracefully (boolean type)
        :return: True if the VM is shut-down successfully, False otherwise
        """
        vmUUID = self.xcpManager.getVmUUID(pRef)
        vmName = self.xcpManager.getVmName(pRef)
        if self.xcpManager.isVmRunning(pRef) and (not pForce):
            S_INFO("Shutting down (gracefully) VM \"%s\" [%s]", vmName, vmUUID)
            self.xcpManager.do_ShutdownClean(pRef)
        # If the VM is still running, then it ignored the shutdown signal, so proceed with a hard-shutdown
        if self.xcpManager.isVmRunning(pRef):
            S_INFO("Forcing shutting down VM \"%s\" [%s]", vmName, vmUUID)
            self.xcpManager.do_ShutdownHard(pRef)
            if self.xcpManager.isVmRunning(pRef):
                S_EXIT("Could not shutdown VM " + vmName + " [" + vmUUID + "]")
                return False
        return True

    def initXenVmPool(self, pScenarioName, pDoShutdown=True):
        """
        Initializes the pool with the VMs.
        It obtains a list of the VMs that are currently installed on the Xen server and based on their
        name-description meta-info it checks if they belong to the specified scenario and also infers
        their template type and allocates them to the correct sub-pool. VMs added in the pool are
        reused across emulations.
        :param pScenarioName: The name of the scenario for which we are initializing the pool
        :param pDoShutdown: If True it will shut down each VM before adding it to the pool.
        """
        print "Constructing the Xen VM pool"
        allVMs = self.xcpManager.getAllVms()
        for vm in allVMs:
            vmUUID = self.xcpManager.getVmUUID(vm)
            vmName = self.xcpManager.getVmName(vm)
            vmDescr = self.xcpManager.getVmDescription(vm)
            if self.isVmOfScenario(vmDescr, pScenarioName):
                # VM should be already shutdown (if not kill it)
                if pDoShutdown == True and self.xcpManager.isVmRunning(vm):
                    self.haltVM(vm)
                vmTplFound = False
                # Now add the VM in the right pool
                for tpl in templatesDB.keys():
                    if self.isVmOfType(vmDescr, tpl):
                        self.XEN_VM_POOL[tpl].append(vm)
                        vmTplFound = True
                        S_INFO("VMPool: Added LINUX_HOST VM \"%s\" [%s]", vmName, vmUUID)
                if not vmTplFound:
                    S_INFO("VMPool: Found VM with unrecognized type \"%s\" [%s]. Destroying the VM", vmName, vmUUID)
                    self.haltVM(vm)
                    self.xcpManager.do_DestroyVM(vm, True)

    def initXenNetPool(self, pScenarioName):
        """
        Initialize the pool with the Xen server networks.
        It obtains a list of the networks that are currently installed on the Xen server and based on their
        name-description meta-info it checks if they belong to the specified scenario and allocates them
        to the networks pool. Networks added in the pool are reused across emulations.
        :param pScenario: The name of the scenario for which we are initializing the pool
        :return:
        """
        print "\nConstructing the Xen Network pool"
        allNets = self.xcpManager.getNetworks()
        for net in allNets:
            netDescr = self.xcpManager.getNetworkDescription(net)
            if netDescr.startswith(Selena.SELENA_NET_KEYWORD + "--" + pScenarioName + "--"):
                # Net should have zero attached VIFs (Selena destroys and re-creates all VIFs)
                for vif in self.xcpManager.getNetworkVifs(net):
                    self.xcpManager.do_DestroyVif(vif)
                # Finally add the network in the pool
                self.XEN_NET_POOL.append(net)
                netUUID = self.xcpManager.getNetworkUUID(net)
                S_INFO("NetPool: Added network \"%s\" [bridge=%s]", netUUID, self.xcpManager.getNetworkBridgeDev(net))

    def generateVmName(self, pName, pID):
        return pName + "--Node(" + str(pID) + ")"

    def generateVmDescription(self, pScenarioName, pType):
        return Selena.SELENA_VM_KEYWORD + "--" + pScenarioName + "--" + pType + "--"

    def isVmOfScenario(self, pDescription, pScenarioName):
        return pDescription.startswith(Selena.SELENA_VM_KEYWORD + "--" + pScenarioName + "--")

    def isVmOfType(self, pVmDescr, pType):
        return "--" + pType + "--" in pVmDescr

    def generateVmConfig(self, pNode, pScenarioName):
        """
        Create a VM configuration based on the details of a scenario Node.
        This configuration is ready to be consumed by XAPI
        :param pNode: The node object of the scenario
        :param pScenarioName: The scenario object
        :return: The new VM configuration in the form of a dictionary
        """
        vmName = self.generateVmName(pNode['NAME'], pNode['ID'])
        vmDescr = self.generateVmDescription(pScenarioName, pNode['TYPE'])
        vmConfig = {'name_label': vmName,
                    'name_description': vmDescr,
                    'memory_static_max': str(pNode['XEN_RAM']),
                    'memory_dynamic_max': str(pNode['XEN_RAM']),
                    'memory_dynamic_min': str(pNode['XEN_RAM']),
                    'memory_static_min': str(pNode['XEN_RAM']),
                    'VCPUs_max': str(pNode['XEN_CPUS']),
                    'VCPUs_params': {'mask': pNode['XEN_CPUPIN']},
                    'VCPUs_at_startup': str(pNode['XEN_CPUS']),
                    'PV_kernel': '',
                    'PV_ramdisk': '',
                    'PV_args': '',
                    'PV_bootloader': '',
                    'PV_bootloader_args': ''
        }
        vmTplFound = False
        for tpl in templatesDB.keys():
            if pNode['TYPE'] == tpl:
                vmConfig['PV_kernel'] = str(templatesDB[tpl]['PV_kernel'])
                vmConfig['PV_ramdisk'] = str(templatesDB[tpl]['PV_ramdisk'])
                vmConfig['PV_args'] = str(templatesDB[tpl]['PV_args'])
                vmConfig['PV_bootloader'] = str(templatesDB[tpl]['PV_bootloader'])
                vmConfig['PV_bootloader_args'] = str(templatesDB[tpl]['PV_bootloader_args'])
                vmTplFound = True
        if not vmTplFound:
            S_EXIT("Selena was requested to build a VM of unknown type %s. Exiting" % (pNode['TYPE']))
        return vmConfig

    def getVmFromPool_byName(self, pVmName, pType):
        """
        Try to Retrieve a VM from the VMs pool with the specified label-name (left from previous emulation runs)
        All VMs in pool have the scenario's name in their description-name meta-info
        (distinct from the name-label)
        :param pVmName: The name of the Vm that we wish to retrieve
        :param pType: The type of the VM which determines the sub-pool in which Selena will search for a matching VM
        :return: The index in the pools and the VM object if a matching VM is found, (None, None) otherwise
        """
        if not self.XEN_VM_POOL[pType]: # pool doesn't contain a VM of our type
            return (None, None)
        for i in range(0, len(self.XEN_VM_POOL[pType])):
            if pVmName == self.xcpManager.getVmName(self.XEN_VM_POOL[pType][i]):
                return (i, self.XEN_VM_POOL[pType][i])
        return (None, None)


    def doPoolFirstPass(self, pScenario):
        """
        Make a first pass of the pool to extract VMs with exact name matches (reuse VMs from previous scenario runs)
        :param pScenario: The name of the scenario
        """
        vmRef = None
        # For each node in the emulation scenario description, try to find matching VMs in the pool
        for nId, node in pScenario.EMU_NODES.items():
            name2lookup = self.generateVmName(node['NAME'], nId)
            (idx, vmRef) = self.getVmFromPool_byName(name2lookup, node['TYPE'])
            if vmRef: # we found a matching VM in the pool
                S_DEBUG("\nFound a matching VM (%s) of type %s in the pool", self.xcpManager.getVmUUID(vmRef), node['TYPE'])
                # remove the VM from the pool
                del self.XEN_VM_POOL[node['TYPE']][idx]
                self.reuseVM(node, vmRef, pScenario.name)


    def reuseVM(self, pNode, pVmRef, pScenarioName):
        """
        Reuse a VM from the scenario's VM pool. Update the node meta-info with the VM's details.
        :param pNode: The scenario's node object that we wish to update with the matching VM's details
        :param pVmRef: The OpaqueRef of the VM to be reused
        :param pScenarioName: The name of the scenario
        """
        # refresh VM's meta information (safe-guard)
        vmConfig = self.generateVmConfig(pNode, pScenarioName)
        self.xcpManager.do_UpdateVM(pVmRef, vmConfig)
        # Now remove all existing VIFs from the VM
        for vif in self.xcpManager.getVmVifs(pVmRef):
            self.xcpManager.do_DestroyVif(vif)
        # Now fill-in the meta-information of the emulation node
        self.setNodeMetaInfo(pNode, pVmRef, pScenarioName)


    def setNodeMetaInfo(self, pNode, pVmRef, pScenarioName):
        vmUUID = self.xcpManager.getVmUUID(pVmRef)
        S_DEBUG("Node (%d, %s) is now being emulated via VM with UUID:%s\n", pNode['ID'], pNode['NAME'], vmUUID)
        pNode["META_XEN_VMREF"] = pVmRef
        pNode["META_XEN_UUID"] = vmUUID
        pNode["META_XEN_NAME"] = self.generateVmName(pNode['NAME'], pNode['ID'])
        pNode["META_XEN_DESCRIPTION"] = self.generateVmDescription(pScenarioName, pNode['TYPE'])
        vbd = self.xcpManager.getVmVBDs(pVmRef)
        pNode["META_XEN_VBD"] = '' if not vbd else vbd[0]
        vdi = self.xcpManager.getVmVDIs(pVmRef)
        pNode["META_XEN_VDI"] = '' if not vdi else vdi[0]
        pNode["META_XEN_VIFS"] = (len(pNode["NETIFS"])+1)*[None] # VIFs should have been already destroyed, and should be an empty list

    def buildXenVMs(self, pScenario):
        vmRef = None
        for nId, node in pScenario.EMU_NODES.items():
            if not pScenario.isNodeConfigured(nId):
                S_INFO("** Building Node (%d, %s) **", nId, node['NAME'])
                if len(self.XEN_VM_POOL[node['TYPE']]) > 0:
                    vmRef = self.XEN_VM_POOL[node['TYPE']].pop()
                    S_DEBUG("Re-using a VM from the pool that wasn't previously matched (%s, %s)",
                            self.xcpManager.getVmName(vmRef),
                            self.xcpManager.getVmUUID(vmRef))
                    self.reuseVM(node, vmRef, pScenario.name)
                else:
                    S_DEBUG("Creating a new VM")
                    vmConfig = self.generateVmConfig(node, pScenario.name)
                    vmRef = self.xcpManager.do_CreateVM(vmConfig)
                    # Now create the disks based on the provided templates
                    self.createVmDisks(vmRef, node, pScenario.name)
                    #---------------------
                    # Now fill-in the meta-information of the emulation node
                    self.setNodeMetaInfo(node, vmRef, pScenario.name)
        return True

    def createVmDisks(self, pVmRef, pNode, pScenarioName):
        tpl_vdi_uuid = None
        for tpl in templatesDB.keys():
            if pNode['TYPE'] == tpl:
                tpl_vdi_uuid = templatesDB[tpl]['VDI_UUID']
        if not tpl_vdi_uuid:
            S_EXIT("Selena was requested to create a disk for a VM of unknown type %s. Exiting" % (pNode['TYPE']))
        vdi = self.xcpManager.do_CloneVDI_byUUID(tpl_vdi_uuid,
                                                 pNode['NAME'] + "--Node(" + str(pNode['ID']) + ")",
                                                 Selena.SELENA_VDI_KEYWORD + "--" + pScenarioName + "--" + pNode['TYPE'] + "--")
        vbd = None
        if not vdi:
            S_EXIT("Failed to clone VDI.. Exiting")
        else:
            vbd = self.xcpManager.do_CreatePlugVBD(pVmRef,
                                                   vdi,
                                                   True,
                                                   False,
                                                   pNode['NAME'] + "--Node(" + str(pNode['ID']) + ")",
                                                   Selena.SELENA_VBD_KEYWORD + "--" + pScenarioName + "--" + pNode['TYPE'] + "--")
            if not vbd:
                self.xcpManager.do_DestroyVDI(vdi)
                S_EXIT("Failed to create-plug VBD. Exiting")
        return vbd


    def buildNetworking(self, pScenario):
        S_INFO("Preparing scenario networking")
        for link in pScenario.LINKS:
            if not link['META_CONFIGURED']:
                #print '***********Configuring link %s**********' % str(link)
                if link: # if Link exists (not None)
                    nodeA = pScenario.EMU_NODES[link['NODE_A']]
                    nodeB = pScenario.EMU_NODES[link['NODE_B']]
                    #print 'NodeA:'
                    #self.pp.pprint(nodeA)
                    #print 'NodeB:'
                    #self.pp.pprint(nodeB)
                    #print "Creating link: %s(%d)--%s(%d)" % (nodeA['NAME'], link['NODE_A'], nodeB['NAME'], link['NODE_B'])
                    # Select a network
                    net = None
                    if len(self.XEN_NET_POOL) > 0: # re-use existing network
                        net = self.XEN_NET_POOL.pop()
                        self.xcpManager.do_UpdateNetwork(net,
                                                         nodeA['NAME']+"(" + str(nodeA['ID']) + ")--" + nodeB['NAME']+"(" + str(nodeB['ID']) + ")",
                                                         '1500',
                                                         Selena.SELENA_NET_KEYWORD + "--" + pScenario.name + "--")
                    else:  # create a new network
                        net = self.xcpManager.do_CreateNetwork(nodeA['NAME']+"(" + str(nodeA['ID']) + ")--" + nodeB['NAME']+"(" + str(nodeB['ID']) + ")",
                                                               '1500',
                                                               Selena.SELENA_NET_KEYWORD + "--" + pScenario.name + "--")
                    if not net:
                        S_EXIT("Could not create network for link " + nodeA['NAME']+"(" + str(nodeA['ID']) + ")--" + nodeB['NAME']+"(" + str(nodeB['ID']) + ")")
                    # Now reset the bridge
                    bridgeIface = self.xcpManager.getNetworkBridgeDev(net)
                    self.EXEC.runCommand("sudo ovs-vsctl del-br " + bridgeIface)
                    (status, _) = self.EXEC.runCommand("sudo ovs-vsctl add-br " + bridgeIface)
                    if status:
                        S_EXIT("Could not configure the bridge interface of network:" % (self.xcpManager.getNetworkUUID(net)))
                    (status, _) = self.EXEC.runCommand("sudo ifconfig " + bridgeIface + " up")
                    if status:
                            S_EXIT("Oh snap... Could not bring up the bridge interface/bridge %s." % bridgeIface)
                    # Try to create the nodeA VIF
                    macAddr = '' if nodeA['NETIFS'][link['IFACE_A']][1] == 'RANDOM' else nodeA['NETIFS'][link['IFACE_A']][1]
                    #print "MAC A: " + macAddr
                    #self.pp.pprint(nodeA['NETIFS'][link['IFACE_A']][1])
                    #self.pp.pprint(net)
                    linkDatarate = None
                    if link['RATE']:
                        linkDatarate = int((link['RATE']*125)/pScenario.TDF) # the int isn't really necessary since both operands are int, just in case....
                    vif = self.xcpManager.do_CreateVif(nodeA['META_XEN_VMREF'], net, str(link['IFACE_A']+1), macAddr, linkDatarate) # we use +1 because device 0 is reserved for management interface
                    #self.pp.pprint(self.xcpManager.getVifRecord(vif))
                    if not vif:
                        S_EXIT("Failed to create Link %s" % (nodeA['NAME']+"(" + str(nodeA['ID']) + ")--" + nodeB['NAME']+"(" + str(nodeB['ID']) + ")"))
                    nodeA['META_XEN_VIFS'][link['IFACE_A']] = vif
                    # Try to create the nodeB VIF
                    macAddr = '' if nodeB['NETIFS'][link['IFACE_B']][1] == 'RANDOM' else nodeB['NETIFS'][link['IFACE_B']][1]
                    #print "MAC B: " + macAddr
                    #self.pp.pprint(nodeB['NETIFS'][link['IFACE_B']][1])
                    vif = self.xcpManager.do_CreateVif(nodeB['META_XEN_VMREF'], net, str(link['IFACE_B']+1), macAddr, linkDatarate) # we use +1 because device 0 is reserved for management interface
                    if not vif:
                        S_EXIT("Failed to create Link %s" % (nodeA['NAME']+"(" + str(nodeA['ID']) + ")--" + nodeB['NAME']+"(" + str(nodeB['ID']) + ")"))
                    nodeB['META_XEN_VIFS'][link['IFACE_B']] = vif
                    #self.pp.pprint(self.xcpManager.getVifRecord(vif))
                    # Mark the link as configured and add META info
                    link['META_CONFIGURED'] = True
                    link['META_XEN_NETWORK'] = net
                    #self.pp.pprint(link)
        for hub in pScenario.HUBS:
            if hub and not hub['META_CONFIGURED']:
                # Select a network
                net = None
                net_id = ""
                first = True

                #construct network ids
                node_name = "%s--%s--"%(Selena.SELENA_NET_KEYWORD, pScenario.name)
                for (node, _) in hub["LINKS"]:
                    node =  pScenario.EMU_NODES[node]
                    preamble = "--"
                    if first: preamble = ""
                    net_id = "%s%s(%d)"%(preamble, node['NAME'], node['ID'])
                    first = False

                if len(self.XEN_NET_POOL) > 0: # re-use existing network
                    net = self.XEN_NET_POOL.pop()
                    self.xcpManager.do_UpdateNetwork(net, net_id, '1500', node_name)
                else:  # create a new network
                    net = self.xcpManager.do_CreateNetwork(net_id, '1500', node_name)
                if not net:
                    S_EXIT("Could not create network for link " + net_id)

                # Now reset the bridge
                bridgeIface = self.xcpManager.getNetworkBridgeDev(net)
                self.EXEC.runCommand("sudo ovs-vsctl del-br " + bridgeIface)
                (status, _) = self.EXEC.runCommand("sudo ovs-vsctl add-br " + bridgeIface)
                if status:
                    S_EXIT("Could not configure the bridge interface of network: %s" % (self.xcpManager.getNetworkUUID(net)))
                (status, _) = self.EXEC.runCommand("sudo ifconfig " + bridgeIface + " up")
                if status:
                        S_EXIT("Oh snap... Could not bring up the bridge interface/bridge %s." % bridgeIface)

                # Try to create the nodeA VIF
                for (node, ifIx) in hub["LINKS"]:
                    nodeObj =  pScenario.EMU_NODES[node]
                    macAddr = ''
                    if nodeObj['NETIFS'][ifIx][1] != "RANDOM": macAddr = nodeObj['NETIFS'][ifIx][1]
                    linkDatarate = None
                    if hub['RATE']:
                        # the int isn't really necessary since both operands are int, just in case....
                        linkDatarate = int((hub['RATE']*125)/pScenario.TDF)
                        # we use +1 because device 0 is reserved for management interface
                        vif = self.xcpManager.do_CreateVif(nodeObj['META_XEN_VMREF'], net, str(ifIx+1),
                                                           macAddr, linkDatarate)
                        if not vif:
                            S_EXIT("Failed to create Link %s" % (net_id))
                        nodeObj['META_XEN_VIFS'][ifIx] = vif
                # Mark the link as configured and add META info
                hub['META_CONFIGURED'] = True
                hub['META_XEN_NETWORK'] = net

    def configureEmulationManagementNetwork(self, pScenario):
        # First make sure that the internal Emulation Management Network exists
        managementNet = None
        matchingNets = self.xcpManager.getNetworkByName(Selena.SELENA_MGMT_NET_NAME)
        if len(matchingNets) == 0:
            print "Creating a management nertwork"
            managementNet = self.xcpManager.do_CreateNetwork(Selena.SELENA_MGMT_NET_NAME, "1500")
        elif len(matchingNets) == 1:
            managementNet = matchingNets[0]
            S_INFO("Found an existing management network: %s\n", self.xcpManager.getNetworkUUID(matchingNets[0]))
        else:
            S_EXIT("Something went wrong and a leftover management network exists.")
        # Now setup the network configuration
        bridgeIface = self.xcpManager.getNetworkBridgeDev(managementNet)
        self.EXEC.runCommand("sudo ovs-vsctl del-br " + bridgeIface)
        (status, _) = self.EXEC.runCommand("sudo ovs-vsctl add-br " + bridgeIface)
        #(status, _) = self.EXEC.runCommand("stat /sys/class/net/" + bridgeIface)
        #if status:
        #    (status, _) = self.EXEC.runCommand("sudo ovs-vsctl add-br " + bridgeIface)
        if status:
            S_EXIT("Could not create the management interface/bridge.")
        if not bridgeIface:
            bridgeIface = 'xapi9999'
        (status, _) = self.EXEC.runCommand("sudo ifconfig " + bridgeIface + " " + Selena.SELENA_MGMT_NET_IP + " netmask " + Selena.SELENA_MGMT_NET_MASK)
        if status:
                S_EXIT("Could not bring up the management interface/bridge.")
        # Now set dev-0 as the management interface for all VMs
        for id, node in pScenario.EMU_NODES.items():
            vif = self.xcpManager.do_CreateVif(node['META_XEN_VMREF'], managementNet, '0')
            if not vif:
                S_EXIT("Failed to create management network VIF for VM %s") % (node['META_XEN_UUID'])
            else:
                node['META_XEN_VIFS'][0] = vif
        return managementNet

    def configureVifTxqueuelen(self, pScenario):
        for nId, node in pScenario.EMU_NODES.items():
            domid = self.xcpManager.getVmDomID(node['META_XEN_VMREF'])
            for i in range(0, len(node['NETIFS'])+1): # +1 for  the management interface
                vifName = 'vif%s.%d' % (str(domid), i)
                S_DEBUG("Configuring netif %s txqueuelen", vifName)
                self.EXEC.runCommand('sudo ifconfig %s txqueuelen 750' % (vifName))


    def startAllVMs(self, pScenario):
        S_INFO("\nStarting now all VMs")
        for nId, node in pScenario.EMU_NODES.items():
            S_INFO("**VM for node: %d, %s**", nId, node['NAME'])
            # Set the meta-info
            node['GUEST_MGMT_IPADDR'] = Selena.SELENA_MGMT_NETADDR + str(nId+2)
            # Start the VM
            self.xcpManager.do_Start(node['META_XEN_VMREF'])
            # Obtain the Guest's DOMID
            tmpdomid = self.xcpManager.getVmDomID(node['META_XEN_VMREF'])
            if int(tmpdomid) < 1:
                S_ERROR("ERROR: VM %s(%d) uuid=%s failed to start", node['NAME'], node['ID'], node['META_XEN_UUID'])
                return
            node['META_XEN_DOMID'] = str(tmpdomid)
            xsPath = '/local/domain/' + str(tmpdomid) + '/Selena'
            # Write the xenstore records and wait the guest to become ready
            self.EXEC.runCommand('sudo xenstore-write ' + xsPath + ' hello')
            self.EXEC.runCommand('sudo xenstore-chmod ' + xsPath + ' r')
            self.EXEC.runCommand('sudo xenstore-write ' + xsPath + '/bootipaddr ' + Selena.SELENA_MGMT_NETADDR + str(nId+2)) # +2 because 0 is reserved for network address, and 1 is reserved for Dom)
            self.EXEC.runCommand('sudo xenstore-chmod ' + xsPath + '/bootipaddr r')
            self.EXEC.runCommand('sudo xenstore-write ' + xsPath + '/bootipmask ' + Selena.SELENA_MGMT_NET_MASK)
            self.EXEC.runCommand('sudo xenstore-chmod ' + xsPath + '/bootipmask r')
            self.EXEC.runCommand('sudo xenstore-write ' + xsPath + '/cmd uptime')
            self.EXEC.runCommand('sudo xenstore-chmod ' + xsPath + '/cmd r')
            self.EXEC.runCommand('sudo xenstore-write ' + xsPath + '/lock RESERVED')
            self.EXEC.runCommand('sudo xenstore-chmod ' + xsPath + '/lock b')
            self.EXEC.runCommand('sudo xenstore-write ' + xsPath + '/response NONE')
            self.EXEC.runCommand('sudo xenstore-chmod ' + xsPath + '/response b')
            self.EXEC.runCommand('sudo xenstore-write ' + xsPath + '/retstatus 0')
            self.EXEC.runCommand('sudo xenstore-chmod ' + xsPath + '/retstatus b')
            # Now expect the guest to respond
            print "Waiting for a response (via xenstore) from VM %s(%d) uuid=%s domid=%s"  % (node['NAME'], node['ID'], node['META_XEN_UUID'], tmpdomid)
            count = 30
            while count > 0:
                #(_, out) = self.EXEC.runCommand('sudo xenstore-read /Selena/response')
                (_, out) = self.EXEC.runCommand('sudo xenstore-read ' + xsPath + '/lock')
                if out.strip() == 'FREE':
                    count = -1
                else:
                    time.sleep(1)
                count -= 1
            if count == 0:
                S_ERROR("ERROR: VM %s(%d) uuid=%s does not respond", node['NAME'], node['ID'], node['META_XEN_UUID'])
            else:
                S_ERROR("Started VM %s(%d) uuid:%s management IP:%s", node['NAME'], node['ID'], node['META_XEN_UUID'], Selena.SELENA_MGMT_NETADDR+str(nId+2))


    def destroyAllVMs(self, pScenario):
        S_INFO("\nDestroying now all VMs")
        for nId, node in pScenario.EMU_NODES.items():
            self.xcpManager.do_DestroyVM(node['META_XEN_VMREF'], True)
            S_INFO("Destroyed emulation VM %s(%d) uuid=%s", node['NAME'], node['ID'], node['META_XEN_UUID'])


    def loadScenario(self, pScenarioClassName):
        """
        Creates an instance of the specified scenario and initializes it by calling instance's method initScenario()

        :param pScenarioClassName: The name (or path) of the scenario module and/or class.
        :return: The new instance of the scenario
        """
        sys.path.append(os.getcwd())
        S_INFO("Loading scenario \"%s\"" % pScenarioClassName)
        ScenarioClass = self.get_class(pScenarioClassName)
        if not ScenarioClass:
            return None
        myScenario = ScenarioClass()
        myScenario.initScenario()
        return myScenario


    def get_class(self, pathToClass):
        """
        A recursive class tracker.

        :param kls: A string that contains a path to a class in dotted format
        :return: The Class object
        """
        retClass = None
        try:
            if not "." in pathToClass:
                m = __import__(pathToClass)
                retClass = getattr(m, pathToClass, None)
            else:
                # Support for dotted definitions
                parts = pathToClass.split('.')
                module = ".".join(parts[:-1])
                m = __import__( module )
                for component in parts[1:]:
                    m = getattr(m, component, None)
                retClass = m
        except ImportError as e:
            S_CRIT("%s", str(e))
        return retClass

    def main(self, pScenarioClassName):
        print "\n--------------------\nHello from Selena\n--------------------\n"
        # Load the requested Scenario
        scenario = self.loadScenario(pScenarioClassName)
        if not scenario:
            S_EXIT("Failed to load scenario %s" % pScenarioClassName)
        #scenario.prettyPrint()
        # Stop all VMs sequentially 1st try gracefully, 2nd try force shutdown (stops all VMs not only the VMs in the pool)
        self.stopAllRunningVMs(True)
        # Initialize the Selena Xen VM pool
        #sys.exit(1)

        self.initXenVmPool(scenario.name, False) # do shutdown ?
        # Do a first pass on the VM pool, trying to re-use VMs from previous emulation runs
        self.doPoolFirstPass(scenario)
        # Create the VMs as described in nodes of the emulation description (try to re-use any left unmatched VMs from the pool first))
        self.buildXenVMs(scenario)

        # Destroy all emulation VMs
        #self.destroyAllVMs(scenario)
        #sys.exit(1)

        # Configure Selena's emulation management network
        self.configureEmulationManagementNetwork(scenario)
        # Initialize the Selena Xen Network pool
        self.initXenNetPool(scenario.name)
        # Now build the scenario's network
        self.buildNetworking(scenario)
        # Print the emulation scenario Data

        #scenario.prettyPrint()
        # Start all VMs sequentially
        self.startAllVMs(scenario)
        # Configure Dom0 VIF txqueuelengths
        self.configureVifTxqueuelen(scenario)
        # Now run the scenario to create the topology
        scenario.runScenario()
        # Stop all VMs sequentially,1st try gracefully, 2nd try force shutdown (stops all VMs not only the VMs in the pool)
        #self.stopAllRunningVMs(True)
        # Destroy all emulation VMs
        #self.destroyAllVMs(scenario)

    def selenaDo_installScenario(self, pScenarioName):
        """
        This method instructs Selena to create the VMs and virtual networks
         necessary to execute the specified scenario.

        :param pScenarioName: The module and/or class name of the scenario description
        :return: True if all VMs and network are created successfully, False otherwise
        """
        S_DEBUG("Installing scenario %s", pScenarioName)
        scenario = self.loadScenario(pScenarioName)
        if not scenario:
            S_EXIT("Failed to load scenario %s" % pScenarioName)
        self.stopAllRunningVMs(True)
        self.initXenVmPool(scenario.name, False)
        self.doPoolFirstPass(scenario)
        self.buildXenVMs(scenario)
        return True

    def selenaDo_uninstallScenario(self, pScenarioName):
        """
        This method instructs Selena to halt and destroy the VMs and virtual networks
         which are related to the specified scenario.

        :param pScenarioName: The module and/or class name of the scenario description
        :return: True if all VMs and network are destroyed successfully, False otherwise
        """
        S_DEBUG("Uninstalling scenario %s", pScenarioName)
        scenario = self.loadScenario(pScenarioName)
        if not scenario:
            S_EXIT("Failed to load scenario %s" % pScenarioName)
        self.stopAllRunningVMs(True)
        self.initXenVmPool(scenario.name, False)
        self.doPoolFirstPass(scenario)
        self.buildXenVMs(scenario)
        self.destroyAllVMs(scenario)
        return True

    def selenaDo_killScenario(self, pScenarioName):
        """
        This method instructs Selena to halt all the VMs which are related to
        the specified scenario. It is assumed that the scenario has been previously
        installed.

        :param pScenarioName: The module and/or class name of the scenario description
        :return: True if all VMs and network are stopped successfully, False otherwise
        """
        S_DEBUG("Killing all VMs belonging to scenario %s", pScenarioName)
        scenario = self.loadScenario(pScenarioName)
        if not scenario:
            S_EXIT("Failed to load scenario %s" % pScenarioName)
        self.stopAllRunningVMs(True)
        return True

    def selenaDo_startScenario(self, pScenarioName):
        """
        This method instructs Selena to start the VMs of the specified scenario. It is
        assumed that the scenario has been previously installed.

        :param pScenarioName: The module and/or class name of the scenario description
        :return: True if all VMs and network are created successfully, False otherwise
        """
        S_DEBUG("Starting and configuring all VMs belonging to scenario %s", pScenarioName)
        scenario = self.loadScenario(pScenarioName)
        if not scenario:
            S_EXIT("Failed to load scenario %s" % pScenarioName)
        self.stopAllRunningVMs(True)
        self.initXenVmPool(scenario.name, False)
        self.doPoolFirstPass(scenario)
        self.buildXenVMs(scenario)
        self.configureEmulationManagementNetwork(scenario)
        self.initXenNetPool(scenario.name)
        self.buildNetworking(scenario)
        self.startAllVMs(scenario)
        self.configureVifTxqueuelen(scenario)
        scenario.runScenario()
        return True

    def selenaDo_restartScenario(self, pScenarioName):
        S_DEBUG("restart scenario is not yet implemented")
        return True


S_EXIT = __doExit
