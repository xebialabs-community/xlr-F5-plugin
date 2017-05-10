# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS. 
#

import sys
import java.lang.System as System
import java.text.SimpleDateFormat as Sdf
import java.sql.Date as Date


from java.lang import Exception
from java.io import PrintWriter
from java.io import StringWriter
from java.lang import ClassLoader


import os, re, sys, traceback

import java.lang.String as String

from com.xebialabs.overthere import CmdLine
from com.xebialabs.overthere.util import CapturingOverthereExecutionOutputHandler, OverthereUtils
from com.xebialabs.overthere.local import LocalConnection

class WinLocalCmd():
    def __init__(self, script):
        self.script = script

        self.stdout = CapturingOverthereExecutionOutputHandler.capturingHandler()
        self.stderr = CapturingOverthereExecutionOutputHandler.capturingHandler()

    def execute(self):

        connection = None
        try:
            connection = LocalConnection.getLocalConnection()
            tmp_workspace_file = connection.getTempFile('tmp_workspace')
            workspace_path = re.sub('tmp_workspace', '', tmp_workspace_file.getPath())
            workspace_directory = connection.getFile(workspace_path)
            connection.setWorkingDirectory(workspace_directory)
            new_path = "%s\ltm" % workspace_path
            if not os.path.exists(new_path):
                os.makedirs(new_path)
            # connection.setWorkingDirectory(connection.getFile(self.scriptpath))
            # upload the script and pass it to cscript.exe

            ltm_disable_file = connection.getFile(OverthereUtils.constructPath(connection.getFile(new_path), 'ltm_disable.py'))
            OverthereUtils.write(String(self.script).getBytes(), ltm_disable_file)
            ltm_disable_file.setExecutable(True)
            ltm_disable_file_path = ltm_disable_file.getPath()

            targetFile = connection.getTempFile('ltm_disable_script', '.cmd')
            batch_script =  "@echo off\r\ncd %s\r\npython %s \r\n" % (workspace_path, ltm_disable_file_path)
            OverthereUtils.write(String(batch_script).getBytes(), targetFile)
            targetFile.setExecutable(True)
            # run cscript in batch mode
            scriptCommand = CmdLine.build(targetFile.getPath())
            return connection.execute(self.stdout, self.stderr, scriptCommand)
        except Exception, e:
            stacktrace = StringWriter()
            writer = PrintWriter(stacktrace, True)
            e.printStackTrace(writer)
            self.stderr.handleLine(stacktrace.toString())
            return 1
        finally:
            if connection is not None:
                connection.close()

    def getStdout(self):
        return self.stdout.getOutput()

    def getStdoutLines(self):
        return self.stdout.getOutputLines()

    def getStderr(self):
        return self.stderr.getOutput()

    def getStderrLines(self):
        return self.stderr.getOutputLines()



scriptFile = """
#!/usr/bin/python

import pycontrol.pycontrol as pc
import getpass
import sys
from sys import argv
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

bigip_address = '%s'
bigip_user = '%s'
bigip_pass = '%s'
active_partition = '%s'
poolmember_pool = '%s'
# 192.168.1.2:7070, 192.168.1.45:6600, 192.168.1.45
# 192.168.1.2:7070
# 192.168.1.2
# Address should be given in above manner
# if port number is not given the default 80 port will be set.

poolmember_address = '%s'


poolmember_address_array = []
poolmember_port_array = []


poolmember_address_list = poolmember_address.replace(' ','').split(',')

for poolmember_address_ip_port in poolmember_address_list:
    pool_details = poolmember_address_ip_port.split(':')
    if len(pool_details)>1:
        poolmember_address_array.append(pool_details[0])
        poolmember_port_array.append(pool_details[1])

    else:
        poolmember_address_array.append(pool_details[0])
        poolmember_port_array.append(80)

print 'Connecting to BIG-IP at [' + bigip_address + '] as user [' + bigip_user + ']'
bigip = pc.BIGIP(hostname = bigip_address, username = bigip_user, password = bigip_pass, fromurl = True, wsdls = ['Management.Partition', 'LocalLB.Pool', 'LocalLB.PoolMember'])

pool = bigip.LocalLB.Pool
pool_version = pool.get_version()
print 'Detected version: ' + pool_version

print 'Setting active partition to [' + active_partition + ']'
bigip.Management.Partition.set_active_partition(active_partition)

try:
    setter = pool.set_member_monitor_state
    legacy_api = 0
except AttributeError:
    legacy_api = 1

if legacy_api:
    sstate_list = []
    mstate_list = []

    i = 0
    for pmem_ip in poolmember_address_array:
        pmem = bigip.LocalLB.PoolMember.typefactory.create('Common.IPPortDefinition')
        pmem.address = pmem_ip
        pmem.port = int(poolmember_port_array[i])

        # session state
        sstate = bigip.LocalLB.PoolMember.typefactory.create('LocalLB.PoolMember.MemberSessionState')
        sstate.member = pmem
        sstate.session_state = 'STATE_DISABLED'
        sstate_list.append(sstate)

        # monitor state
        mstate = bigip.LocalLB.PoolMember.typefactory.create('LocalLB.PoolMember.MemberMonitorState')
        mstate.member = pmem
        mstate.monitor_state = 'STATE_DISABLED'
        mstate_list.append(mstate)
        i += 1

    sstate_seq = bigip.LocalLB.PoolMember.typefactory.create('LocalLB.PoolMember.MemberSessionStateSequence')
    sstate_seq.item = sstate_list

    print 'Disabling pool member ' + str(poolmember_address_list) + ' in pool ' + poolmember_pool
    bigip.LocalLB.PoolMember.set_session_enabled_state(pool_names = [poolmember_pool], session_states = [sstate_seq])


    mstate_seq = bigip.LocalLB.PoolMember.typefactory.create('LocalLB.PoolMember.MemberMonitorStateSequence')
    mstate_seq.item = mstate_list

    #print 'Forcing pool member [' + poolmember_address + ':' + poolmember_port + '] in pool [' + poolmember_pool + '] offline'
    #bigip.LocalLB.PoolMember.set_monitor_state(pool_names = [poolmember_pool], monitor_states = [mstate_seq])
else:
    pmem_list = []
    state_list = []
    i = 0
    for pmem_ip in poolmember_address_array:
        pmem = pool.typefactory.create('Common.AddressPort')
        pmem.address = pmem_ip
        pmem.port = int(poolmember_port_array[i])
        pmem_list.append(pmem)
        state = pool.typefactory.create('Common.EnabledState').STATE_DISABLED
        state_list.append(state)
        i += 1

    pmem_seq = pool.typefactory.create('Common.AddressPortSequence')
    pmem_seq.item = pmem_list


    state_seq = pool.typefactory.create('Common.EnabledStateSequence')
    state_seq.item = state_list

    # session state
    print 'Disabling pool member ' + str(poolmember_address_list) + ' in pool ' + poolmember_pool
    pool.set_member_session_enabled_state(pool_names = [poolmember_pool], members= [pmem_seq], session_states = [state_seq])

    # monitor state
    #print 'Forcing pool member ' + str(poolmember_address_list) + ' in pool ' + poolmember_pool + ' offline'
    #pool.set_member_monitor_state(pool_names = [poolmember_pool], members= [pmem_seq], monitor_states = [state_seq])

print 'Done'
""" % ( bigIpAddress, bigIpUser, bigIpPass, activePartition, poolMemberPool, poolMemberAddress)


script = WinLocalCmd(scriptFile)
exitCode = script.execute()

output = script.getStdout()
err = script.getStderr()
if (exitCode == 0):
    print scriptFile
    print "----"
    print output
else:
    print "Exit code "
    print exitCode
    print
    print "#### Output:"
    print output

    print "#### Error stream:"
    print err
    print
    print "----"

    #sys.exit(exitCode)
    sys.exit(0)
