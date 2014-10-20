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


import XenAPI
import sys
import random

class XcpManager(object):
    '''
    classdocs
    '''
    
    session = None
    hostUUID = None
    XAPI = None


    def __init__(self,  pUrl="localhost", pUserName="root", pPasswd="root"):
        '''
        Constructor
        '''
        self.url = pUrl
        self.username = pUserName
        self.password = pPasswd
        # First acquire a valid session by logging in:
        self.session = XenAPI.Session(pUrl)
        self.XAPI = self.session.xenapi
        self.XAPI.login_with_password(pUserName, pPasswd)
        hosts = self.XAPI.host.get_all()
        if not hosts: 
            self.__doExit("Could not obtain a valid reference to the XenServer host")
        self.hostUUID = hosts[0]
        
        
    def __doExit(self, message):
        print "Exiting: " + message
        sys.exit(1)
    
    
    def vmByUUID(self, pVmUUID):
        return self.XAPI.VM.get_by_uuid(pVmUUID)
    
    
    
    def getVmUUID(self, pRef):
        return self.XAPI.VM.get_uuid(pRef)
    def getVmRecord(self, pRef):
        return self.XAPI.VM.get_record(pRef)
    def getVmState(self, pRef):
        return self.XAPI.VM.get_power_state(pRef)
    def getVmDescription(self, pRef):
        return self.XAPI.VM.get_name_description(pRef)
    def getVmName(self, pRef):
        return self.XAPI.VM.get_name_label(pRef)
    def getVmDomID(self, pRef):
        return self.XAPI.VM.get_domid(pRef)
    def getVmVBDs(self, pRef):
        return self.XAPI.VM.get_VBDs(pRef)
    def getVmMetrics(self, pRef):
        return self.XAPI.VM.get_metrics(pRef)
    def getVmVDIs(self, pRef):
        vdis = []
        vbds = self.getVmVBDs(pRef)
        for vbd in vbds:
            vdis.append(self.XAPI.VBD.get_VDI(vbd))
        return vdis
    def getVmVifs(self, pRef):
        return self.XAPI.VM.get_VIFs(pRef)
    def getVmNetworks(self, pRef):
        nets = []
        for vif in self.getVmVifs(pRef):
            nets.append(self.XAPI.VIF.get_network(vif))
        return nets
    
    def getVCPUs_utilisation(self, pRef):
        self.XAPI.VM_metrics.get_VCPUs_utilisation(pRef)
    
    
    
    
    def getResidentVMs(self):
        return self.XAPI.host.get_resident_VMs(self.hostUUID)
    def getAllVms(self):
        myVMs = []
        for tmpVm in self.XAPI.VM.get_all():
            if not self.XAPI.VM.get_is_a_template(tmpVm):
                myVMs.append(tmpVm)
        return myVMs    
    def getRunningVMs(self):
        return [vm for vm in self.getAllVms() if self.isVmRunning(vm) and not self.XAPI.VM.get_is_control_domain(vm)]
    def getAllTemplates(self):
        return [tpl for tpl in self.XAPI.VM.get_all() if self.XAPI.VM.get_is_a_template(tpl)]
    
    
    
    
    
    def getNetworkByUUID(self, pUuid):
        return self.XAPI.network.get_by_uuid(pUuid)
    def getNetworkByName(self, pNetNameLabel):
        return self.XAPI.network.get_by_name_label(pNetNameLabel)
    def getNetworkBridgeDev(self, pRef):
        return self.XAPI.network.get_bridge(pRef)
    def getNetworkDescription(self, pRef):
        return self.XAPI.network.get_name_description(pRef)
    def getNetworkVifs(self, pRef):
        return self.XAPI.network.get_VIFs(pRef)
    def getNetworkUUID(self, pRef):
        return self.XAPI.network.get_uuid(pRef)
    def getNetworks(self):
        return self.XAPI.network.get_all()
    def getNetworkName(self, pRef):
        return self.XAPI.network.get_name_label(pRef)
    def getVifNetwork(self, pRef):
        return self.XAPI.vif.get_network(pRef)
    def getVifRecord(self, pVifRef):
        return self.XAPI.VIF.get_record(pVifRef)
    def getVifUUID(self, pRef):
        return self.XAPI.vif.get_uuid(pRef)
    def getVifVM(self, pRef):
        return self.XAPI.vif.get_VM(pRef)
    
    
    
    
    
    
    def isVmRunning_UUID(self, pUuid):
        return self.XAPI.VM.get_power_state(self.vmByUUID(pUuid))
    def isVmRunning(self, pRef):
        #print "\n=======%s=========\n" % (pRef)
        return (self.XAPI.VM.get_power_state(pRef) == "Running")
    def isDom0(self, pRef):
        return self.XAPI.VM.get_is_control_domain(pRef)
    
    
    
    def do_ShutdownClean(self, pRef):
        try:
            self.XAPI.VM.clean_shutdown(pRef)
        except XenAPI.Failure, e:
                print "Failed to shutdown gracefully the VM (%s): \n Error: %s" % (self.getVmUUID(pRef), str(e))
                return False
        return True
    def do_ShutdownClean_UUID(self, pUuid):
        return self.do_ShutdownClean(self.vmByUUID(pUuid))
    def do_ShutdownHard(self, pRef):
        try:
            self.XAPI.VM.hard_shutdown(pRef)
        except XenAPI.Failure, e:
                print "Failed to force-shutdown the VM (%s): \n Error: %s" % (self.getVmUUID(pRef), str(e))
                return False
        return True
    def do_ShutdownHard_UUID(self, pUuid):
        return self.do_ShutdownHard(self.vmByUUID(pUuid))
    def do_Start(self, pRef):
        return self.XAPI.VM.start(pRef, False, False)
    def do_Start_UUID(self, pUuid):
        return self.XAPI.VM.start(self.vmByUUID(pUuid), False, False)
    def getNextFreeVifDev(self, pVmRef):
        devArr = [0]*40 # 40 vifs max
        for vif in self.getVmVifs(pVmRef):
            devArr[int(self.XAPI.VIF.get_device(vif))] = 1
        for i in range(0,40):
            if not devArr[i]:
                return str(i)
        return str(40)
    def do_CreateVif(self, pVmRef, pNetwork, pDevice=None, pMac=None, pRateKbps=None):
        if pDevice is None:
            pDevice = self.getNextFreeVifDev(pVmRef)
        print "Creating vif %s for VM %s" % (pDevice, self.getVmUUID(pVmRef))
        vif = { 'device': str(pDevice),
                'network': pNetwork,
                'VM': pVmRef,
                'MAC': pMac if pMac else self.do_GenerateMAC(),
                'MTU': "1500",
                'qos_algorithm_type': "",
                'qos_algorithm_params': {},
                'other_config': {"ethtool-rx": "off", 
                                 "ethtool-tx": "off",  
                                 "ethtool-tso": "off",
                                 "ethtool-ufo": "off",
                                 "ethtool-gso": "off",
                                 "ethtool-gro": "off",
                                 "ethtool-lro": "off"}
                }
        if pRateKbps:
            vif['qos_algorithm_type'] = "ratelimit"
            vif['qos_algorithm_params'] = {"kbps":str(pRateKbps)}
        #import pprint
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(vif)
        try:                       
            vifref = self.XAPI.VIF.create(vif)
        except Exception, e:               
            print "Error creating vif %s at VM %s:\n %s" % (pDevice, self.getVmUUID(pVmRef), str(e))
            return None
        return vifref
    def do_GenerateMAC(self):
        mac = [ 0x1a, 
                0x6e, 
                0x7f,
                random.randint(0x00, 0xff),
                random.randint(0x00, 0xff),
                random.randint(0x00, 0xff) ]
        return ':'.join(map(lambda x: "%02x" % x, mac))
    def do_DestroyVif(self, pRef):
        self.XAPI.VIF.destroy(pRef)
    def do_CreateNetwork(self, pName, pMTU=None, pDescription=''):
        net = { 'MTU': "" if pMTU is None else pMTU,
                'name_label': pName,
                'name_description': pDescription,
                'other_config' : {}
        }
        return self.XAPI.network.create(net)
    def do_UpdateNetwork(self, pNetRef, pName, pMTU=None, pDescription=''):
        try:
            self.XAPI.network.set_name_label(pNetRef, pName)
            self.XAPI.network.set_MTU(pNetRef, pMTU)
            self.XAPI.network.set_name_description(pNetRef, pDescription)
        except Exception, e:               
            print "Error updating network %s:\n %s" % (self.getNetworkUUID(pNetRef), str(e))
            return False
        return True        
        
    def do_DestroyNetwork(self, pRef):
        for vif in self.getNetworkVifs(pRef):
            self.do_DestroyVif(vif)
        self.XAPI.network.destroy(pRef)
    def do_CreateVM(self, pVmConfig):
        vmData = {'name_label': pVmConfig['name_label'],
                'name_description': pVmConfig['name_description'],
                'is_a_template': False,
                'user_version': '1',
                'memory_static_max': pVmConfig['memory_static_max'],
                'memory_dynamic_max': pVmConfig['memory_dynamic_max'],
                'memory_dynamic_min': pVmConfig['memory_dynamic_min'],
                'memory_static_min': pVmConfig['memory_static_min'],
                'VCPUs_max': pVmConfig['VCPUs_max'],
                'VCPUs_params': pVmConfig['VCPUs_params'],
                'VCPUs_at_startup': pVmConfig['VCPUs_at_startup'],
                'actions_after_shutdown': 'Destroy',
                'actions_after_reboot': 'Restart',
                'actions_after_crash': 'Restart',
                'platform': {'nx': 'false', 'acpi': 'true', 'apic': 'true', 'pae': 'true', 'viridian': 'true'},
                'blocked_operations': {},
                'HVM_boot_policy': '',
                'HVM_boot_params': {},
                'HVM_shadow_multiplier': 1.000,
                'PV_kernel': pVmConfig['PV_kernel'],
                'PV_ramdisk': pVmConfig['PV_ramdisk'],
                'PV_args': pVmConfig['PV_args'],
                'PV_legacy_args': '',
                'PV_bootloader': pVmConfig['PV_bootloader'],
                'PV_bootloader_args': pVmConfig['PV_bootloader_args'],
                'affinity': '',
                'other_config': { 'mac_seed' : 'df6584ca-7e9c-027e-3071-6ca73c6398ce'},
                'xenstore_data': {},
                'ha_always_run': False,
                'ha_restart_priority': '',
                'protection_policy': '',
                #'tags': "",
                'PCI_bus': '',
                'recommendations': '',
        }   
        print "Creating vm %s" % (pVmConfig['name_label'])
        vm = None      
        try:                       
            vm = self.XAPI.VM.create(vmData)
        except Exception, e:               
            print "Error creating vm %s:\n %s" % (vmData['name_label'], str(e))
        return vm
    def do_UpdateVM(self, pRef, pVmConfig):
        if pVmConfig.has_key('name_label'):
            self.XAPI.VM.set_name_label(pRef, pVmConfig['name_label'])
        if pVmConfig.has_key('name_description'):
            self.XAPI.VM.set_name_description(pRef, pVmConfig['name_description'])
        if pVmConfig.has_key('memory_static_min'):
            self.XAPI.VM.set_memory_static_min(pRef, pVmConfig['memory_static_min'])
        if pVmConfig.has_key('memory_dynamic_min'):
            self.XAPI.VM.set_memory_dynamic_min(pRef, pVmConfig['memory_dynamic_min'])                                       
        if pVmConfig.has_key('memory_dynamic_max'):
            self.XAPI.VM.set_memory_dynamic_max(pRef, pVmConfig['memory_dynamic_max'])
        if pVmConfig.has_key('memory_static_max'):
            self.XAPI.VM.set_memory_static_max(pRef, pVmConfig['memory_static_max'])
        if pVmConfig.has_key('VCPUs_max'):
            self.XAPI.VM.set_VCPUs_max(pRef, pVmConfig['VCPUs_max'])
        if pVmConfig.has_key('VCPUs_params'):
            self.XAPI.VM.set_VCPUs_params(pRef, pVmConfig['VCPUs_params'])
        if pVmConfig.has_key('VCPUs_at_startup'):
            self.XAPI.VM.set_VCPUs_at_startup(pRef, pVmConfig['VCPUs_at_startup'])
        if pVmConfig.has_key('PV_kernel'):
            self.XAPI.VM.set_PV_kernel(pRef, pVmConfig['PV_kernel'])
        if pVmConfig.has_key('PV_ramdisk'):
            self.XAPI.VM.set_PV_ramdisk(pRef, pVmConfig['PV_ramdisk'])
        if pVmConfig.has_key('PV_args'):
            self.XAPI.VM.set_PV_args(pRef, pVmConfig['PV_args'])
        if pVmConfig.has_key('PV_bootloader'):
            self.XAPI.VM.set_PV_bootloader(pRef, pVmConfig['PV_bootloader'])
        if pVmConfig.has_key('PV_bootloader_args'):
            self.XAPI.VM.set_PV_bootloader_args(pRef, pVmConfig['PV_bootloader_args'])
    def do_DestroyVM(self, pRef, pWDisk=False):
        if self.isVmRunning(pRef):
            self.do_ShutdownHard(pRef)
        if pWDisk:
            vdis = self.getVmVDIs(pRef)
            for v in vdis:
                self.XAPI.VDI.destroy(v)
        return self.XAPI.VM.destroy(pRef)
    def do_CloneVDI_byUUID(self, pTemplateUuid, pName=None, pDescription=None):
        try:
            pTemplateRef = self.XAPI.VDI.get_by_uuid(pTemplateUuid)
            options = {}
            vdi = self.XAPI.VDI.clone(pTemplateRef, options)
            if pName:
                self.XAPI.VDI.set_name_label(vdi, pName)
            if pDescription:
                self.XAPI.VDI.set_name_description(vdi, pDescription)
            return vdi
        except Exception, e:
            print "Error cloning VDI %s :\n %s" % (pTemplateUuid, str(e))
        return None
    def do_DestroyVDI(self, pVdiRef):
        self.XAPI.VDI.destroy(pVdiRef)
    def do_CreatePlugVBD(self, pVmRef, pVdiRef, pBootable=False, pReadonly=False, pName='', pDescription=''):
        vbd_rec = {}
        vbd_rec['VM'] = pVmRef
        vbd_rec['VDI'] = pVdiRef
        vbd_rec['userdevice'] = 'autodetect'
        vbd_rec['bootable'] = pBootable
        vbd_rec['mode'] = 'RO' if pReadonly else 'RW'
        vbd_rec['type'] = 'disk'
        vbd_rec['unpluggable'] = True
        vbd_rec['empty'] = False
        vbd_rec['other_config'] = {}
        vbd_rec['qos_algorithm_type'] = ''
        vbd_rec['qos_algorithm_params'] = {}
        vbd_rec['qos_supported_algorithms'] = []
        vbd_rec['name_label'] = pName
        vbd_rec['name_description'] = pDescription
        vbd = None
        try:
            vbd = self.XAPI.VBD.create(vbd_rec)
        except Exception, e:
            print "Error creating VBD with VDI %s :\n %s" % (self.XAPI.VDI.get_uuid(pVdiRef), str(e))
            return None
        return vbd    
    def do_PlugVBD(self, pVbdRef):
            try:
                self.XAPI.VBD.plug(pVbdRef)
            except Exception, e:
                print "Error plugging VBD %s :\n %s\n Destroying VBD" % (self.XAPI.VBD.get_uuid(pVbdRef), str(e))
                return None
            return True
        
    
    
    
    def printHostDetails(self):
        print "\nUUID=" + self.hostUUID + "\n"
        print "\nHere follow the details \n".join("%s: %s" % (k, v) for k, v in self.XAPI.host.get_record(self.hostUUID).items())
    def printNetworkDetails(self, pRef):
        print "\n".join("%s: %s" % (k, v) for k, v in self.XAPI.network.get_record(pRef).items())
        
    
