#
# Copyright 2019 XEBIALABS
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
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
            new_path = "%s\gtm" % workspace_path
            if not os.path.exists(new_path):
                os.makedirs(new_path)
            # connection.setWorkingDirectory(connection.getFile(self.scriptpath))
            # upload the script and pass it to cscript.exe

            gtm_disable_file = connection.getFile(OverthereUtils.constructPath(connection.getFile(new_path), 'gtm_disable.py'))
            OverthereUtils.write(String(self.script).getBytes(), gtm_disable_file)
            gtm_disable_file.setExecutable(True)
            gtm_disable_file_path = gtm_disable_file.getPath()

            targetFile = connection.getTempFile('gtm_disable_script', '.cmd')
            batch_script =  "@echo off\r\ncd %s\r\npython %s \r\n" % (workspace_path, gtm_disable_file_path)
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
app_name='%s'
data_center = '%s'

app_list = app_name.replace(' ','').split(',')

print 'Connecting to BIG-IP at [' + bigip_address + '] as user [' + bigip_user + ']'
bigip = pc.BIGIP(hostname = bigip_address, username = bigip_user, password = bigip_pass, fromurl = True, wsdls = ['GlobalLB.Application'])

gtm_app  = bigip.GlobalLB.Application
gtm_app_version  = gtm_app.get_version()
print 'Detected version of data_center: ' + gtm_app_version
for app in app_list:
    app_path = '/' + active_partition + '/' + app

    data_centers = gtm_app.get_data_centers([app_path])
    print "Found the following data centers : {data_centers}".format(data_centers=str(data_centers))
    
    for dc in data_centers:
        if isinstance(dc,list):
            for dc_name in dc:
                if data_center.lower() in dc_name.lower():
                    obj = gtm_app.typefactory.create('GlobalLB.Application.ApplicationContextObject')
                    obj.application_name = app_path
                    obj.object_name = dc_name
                    obj.object_type = gtm_app.typefactory.create('GlobalLB.Application.ApplicationObjectType').APPLICATION_OBJECT_TYPE_DATACENTER
                    print "Disabling Datacenter : {dc_name}".format(dc_name=dc_name)
                    try:
                        gtm_app.disable_application_context_object([obj])
                    except Exception as e:
                        print str(e)
                else:
                    print "Skipping Datacenter : {dc_name}".format(dc_name=dc_name)
                    continue
""" % ( bigIpAddress, bigIpUser, bigIpPass, bigActivePartitionName, bigApplicationName, bigAppDataCenter )


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
