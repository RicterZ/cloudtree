from __future__ import absolute_import, unicode_literals
import os
import json
import time
import paramiko

from QcloudApi.qcloudapi import QcloudApi as qcloud_api

from worker.config import TENCENT_CLOUD_API_ID, TENCENT_CLOUD_API_KEY, TENCENT_CLOUD_REGION, TENCENT_CLOUD_LOGIN_PASSWORD
from worker.celery import app


UBUNTU_16_04 = 'img-pyqx34y1'


CONFIG = {
    'Region': TENCENT_CLOUD_REGION,
    'secretId': TENCENT_CLOUD_API_ID,
    'secretKey': TENCENT_CLOUD_API_KEY,
}

CVM_STATUS_CREATING = 3
CVM_STATUS_NORMAL = 2
CVM_STATUS_DESTROYING = 6
CLOUDTREE_INSTALL_SCRIPT = 'https://raw.githubusercontent.com/RicterZ/cloudtree/master/install.sh'


@app.task
def ping():
    return 'ok'


@app.task
def list_cvm(instance_id=None):
    params = {
        'Filters': {
            'instance-name': 'cloud-tree-cluster'
        }
    }

    if instance_id:
        params['Filters']['instance-id'] = instance_id

    service = qcloud_api('cvm', CONFIG)
    ret = service.call('DescribeInstances', params)
    ret = json.loads(ret)
    if 'instanceSet' not in ret:
        raise Exception('List failed: %s' % ret['Response']['Error']['Message'])

    cluster = []
    for i in ret['instanceSet']:
        # cvm status code
        # 3: creating
        # 2: normal
        # 6: destroying
        if i['instanceName'].startswith('cloud-tree-cluster'):
            cluster.append({
                'ip': i['lanIp'],
                'instance_id': i['unInstanceId'],
                'wan_ip': i['wanIpSet'][0],
                'status': i['status'],
            })
    return cluster


@app.task
def install(ip_address):
    if not ip_address:
        return
    try:
        print('Connect to %s ...' % ip_address)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip_address, 22, 'ubuntu', TENCENT_CLOUD_LOGIN_PASSWORD)
        with open(os.path.join(os.path.dirname(__file__), '../config.py')) as f:
            data = f.read().encode('base64').replace('\n', '')

        # write config file
        _, stdout, stderr = client.exec_command('sudo mkdir /root/cloudtree;'
                                                'sudo bash -c "echo %s | base64 -d > /root/cloudtree/config.py"'
                                                % data)
        _, stdout, stderr = client.exec_command('curl -s %s | sudo bash' % CLOUDTREE_INSTALL_SCRIPT)
        print(stdout.read())
        print(stderr.read())
        client.close()
    except Exception as e:
        print(e)


@app.task
def create_cvm(count=1):
    if count <= 0:
        return

    params = {
        'Version': '2017-03-12',
        'Placement': {
            'Zone': TENCENT_CLOUD_REGION + '-2',
        },
        'ImageId': UBUNTU_16_04,
        'LoginSettings': {
            'Password': TENCENT_CLOUD_LOGIN_PASSWORD,
        },
        'InstanceName': 'cloud-tree-cluster',
        'InstanceCount': count,
        'InternetAccessible': {
            'PublicIpAssigned': 'TRUE',
            'InternetMaxBandwidthOut': 1
        },
        'EnhancedService': {
            'SecurityService': {
                'Enabled': False
            },
            'MonitorService': {
                'Enabled': False
            }
        }
    }
    service = qcloud_api('cvm', CONFIG)
    ret = service.call('RunInstances', params)
    ret = json.loads(ret)
    if 'InstanceIdSet' in ret['Response']:
        # return ret['Response']['InstanceIdSet']
        for i in ret['Response']['InstanceIdSet']:
            cvm_info = list_cvm(i)[0]
            while cvm_info['status'] == CVM_STATUS_CREATING:
                cvm_info = list_cvm(i)[0]
                time.sleep(1)

            if ret['Response']['InstanceIdSet'].index(i) == 0:
                time.sleep(20)

            install.delay(cvm_info['wan_ip'])
    else:
        raise Exception('Create failed: %s' % ret['Response']['Error']['Message'])


@app.task
def destroy_cvm(instance_ids):
    if isinstance(instance_ids, (str, unicode)):
        instance_ids = [instance_ids]
    if not isinstance(instance_ids, list):
        raise Exception('Invalid instance id set')
    if not instance_ids:
        return

    params = {
        'Version': '2017-03-12',
        'InstanceIds': instance_ids
    }
    service = qcloud_api('cvm', CONFIG)
    ret = service.call('TerminateInstances', params)
    return ret


if __name__ == '__main__':
    destroy_cvm(list(map(lambda s: s['instance_id'], list_cvm())))
    create_cvm()
