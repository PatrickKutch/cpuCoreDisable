#!/usr/bin/python
##############################################################################
#  Copyright (c) 2019 Intel Corporation
# 
# Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
##############################################################################
#    File Abstract: 
#    simple utility to disable cores on a system.  You can use this to disable
#    all the cores on a physical CPU, or you can use it to disable the hyperthread
#    siblings on a physical CPU
##############################################################################
from __future__ import print_function # for python 2
import argparse
import os
import sys

_Version = '20.1.4 Build 1'

_cpuBaseDir = '/sys/devices/system/cpu/'

def disablepackage(args):
    print("Disabling All Cores on package {}".format(args.package))
    return disablePackageCores(args.package)

def hyperthread(args):
    print("Disabling hyperthread Sibling Cores on package {}".format(args.package))
    return disablePackageHTCores(args.package) 

def main():
    print("CPU Core Disable tool V" + _Version)

    parser = argparse.ArgumentParser(description='CPU Core Disable tool')

    subParsers = parser.add_subparsers(dest='cmd')

    parser_dp = subParsers.add_parser("disablepackage")
    parser_dp.add_argument("-p","--package",help="package (CPU) number to disable",type=int,required=True)

    parser_ht = subParsers.add_parser("hyperthread")
    parser_ht.add_argument("-p","--package",help="package (CPU) number to disable hyperthreading on. can specify 'all'",type=str,required=True)

    try:
        args = parser.parse_args()
        cmd = args.cmd.lower()
        self = sys.modules[__name__]
        if not(hasattr(self, cmd)): #calls one of the fuctions to do the actual work
            print("{} is not a valid option".format(args.cmd))
        else:
            modifiedCount = getattr(self,args.cmd.lower())(args)
            if modifiedCount > 0:
                print("Took {} cores offline.".format(modifiedCount))
                print("**** You must reboot in order to return to previous state ****")


    except Exception as ex:
        print(str(ex))

def disablePackageCores(package):
    state = 0
    changedCount = 0
    for coreName in sorted(os.listdir(_cpuBaseDir)):
        filePkgID = _cpuBaseDir + coreName +'/topology/physical_package_id'
        if os.path.isfile(filePkgID):
            fp = open(filePkgID)
            pkgID = int(fp.readline()) # read the package ID for this cpu core
            fp.close()
            
            if pkgID == package: # matches what we are to disable, so let's do it
                onlineFile = _cpuBaseDir + coreName +'/online'                
                print("writing {} to {}".format(state,onlineFile))
                fp = open(onlineFile,"wt")
                fp.write("{}".format(state))
                fp.close()
                changedCount += 1
                
    return changedCount
                    
            
def disablePackageHTCores(package):
    state = 0
    changedCount = 0
    for coreName in sorted(os.listdir(_cpuBaseDir)):
        
        filePkgID = _cpuBaseDir + coreName +'/topology/physical_package_id'
        if str(package).lower() != 'all':
            if os.path.isfile(filePkgID):
                fp = open(filePkgID)
                pkgID = int(fp.readline()) # read the package ID for this cpu core
                fp.close()
                
            if pkgID != int(package): # doesn't what we are to disable, so skip
                continue
        
        sibsFile = _cpuBaseDir + coreName + '/topology/thread_siblings_list'
        if os.path.isfile(sibsFile):
            fp = open(sibsFile)
            sibs = fp.readline().split(',') # read the siblings this cpu core, if there are none, will not be a comma
            fp.close()
            
           
            if len(sibs) == 1: # no siblings, so just continue
                continue
                
            coreID = coreName[3:] # nuke 'cpu' part of name to get cpu id
                
            if int(sibs[0]) == int(coreID): #There are siblings, but this core is listed 1st, so let's leave it
                pass
                
            else:
                onlineFile = _cpuBaseDir + coreName +'/online'                
                print("writing {} to {}".format(state,onlineFile))
                changedCount += 1
                fp = open(onlineFile,"wt")
                fp.write("{}".format(state))
                fp.close()
                
    return changedCount

if __name__ == "__main__":
    main()

