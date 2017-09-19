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
active_partition = '%s' % activePartition
poolmember_pool = '%s' % poolMemberPool
# 192.168.1.2:7070, 192.168.1.45:6600, 192.168.1.45
# 192.168.1.2:7070
# 192.168.1.2
# Address should be given in above manner
# if port number is not given the default 80 port will be set.
poolmember_address = '%s' % poolMemberAddress


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
bigip = pc.BIGIP(hostname = bigip_address, username = bigip_user, password = bigip_pass)

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
        sstate.session_state = 'STATE_ENABLED'
        sstate_list.append(sstate)

        # monitor state
        mstate = bigip.LocalLB.PoolMember.typefactory.create('LocalLB.PoolMember.MemberMonitorState')
        mstate.member = pmem
        mstate.monitor_state = 'STATE_ENABLED'
        mstate_list.append(mstate)
        i += 1

    sstate_seq = bigip.LocalLB.PoolMember.typefactory.create('LocalLB.PoolMember.MemberSessionStateSequence')
    sstate_seq.item = sstate_list

    print 'Enabling pool member ' + str(poolmember_address_list) + ' in pool ' + poolmember_pool
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
        state = pool.typefactory.create('Common.EnabledState').STATE_ENABLED
        state_list.append(state)

        i += 1

    pmem_seq = pool.typefactory.create('Common.AddressPortSequence')
    pmem_seq.item = pmem_list


    state_seq = pool.typefactory.create('Common.EnabledStateSequence')
    state_seq.item = state_list

    # session state
    print 'Enabling pool members ' + str(poolmember_address_list) + ' in pool ' + poolmember_pool
    pool.set_member_session_enabled_state(pool_names = [poolmember_pool], members= [pmem_seq], session_states = [state_seq])

print 'Done'
