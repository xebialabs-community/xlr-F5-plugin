#
# Copyright 2017 XEBIALABS
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import bigsuds as pc
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

bigip_address = '%s' % bigIpAddress
bigip_user = '%s' % bigIpUser
bigip_pass = '%s' % bigIpPass
active_partition = '%s' % bigActivePartitionName
app_name='%s' % bigApplicationName
data_center = '%s' % bigAppDataCenter

app_list = app_name.replace(' ','').split(',')

print 'Connecting to BIG-IP at [' + bigip_address + '] as user [' + bigip_user + ']'
bigip = pc.BIGIP(hostname = bigip_address, username = bigip_user, password = bigip_pass)

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
                    print "Enabling Datacenter : {dc_name}".format(dc_name=dc_name)
                    try:
                        gtm_app.enable_application_context_object([obj])
                    except Exception as e:
                        print str(e)
                else:
                    print "Skipping Datacenter : {dc_name}".format(dc_name=dc_name)
                    continue
