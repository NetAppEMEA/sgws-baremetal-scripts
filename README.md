# sgws-baremetal-scripts

This repository contains some hacky scripts to semi-automate a StorageGRID Webscale deployment on bare metal RHEL/CentOS hosts with direct-attached E-Series as the backing store.

## Words of caution

*This is work in progres and might require significant effort to get running smoothly.*

## Prerequisits

* Make sure E-Series Webservices Proxy is configured and is aware of all controllers
* Make sure E-Series has host mappings configured

Install [NetApp SANtricity WebAPI - Python SDK](https://github.com/NetApp/santricity-webapi-pythonsdk) (E-Series Python Bindings).
```
$ pip install netapp.santricity
```

Install tools for helping mapping devices:
```
$ sudo yum install iscsi-initiator-utils
$ sudo yum install device-mapper-multipath
```

## Usage

Next, adapt the config for the LUNs that should be created and run the creation script:
```
$ vi config.csv
$ python create_luns.py
```

Validate that all LUNs are properly created and mapped. Now, create the `multipath.conf` which needs to be copied to each host under `/etc/multipath.conf`. Update `create_multipath_conf.py` with your E-Series UUIDs first (TODO: Needs to be simplified):
```
$ vi create_multipath_conf.py
$ python create_multipath_conf.py
```

Rescan devices and restart `multipathd` on all hosts, so that the `multipath.conf` gets pulled properly:
```
$ rescan-scsi-bus.sh
$ service multipathd restart
```

You can now deploy Docker on each host with `devicemapper` as the storage driver, e.g.:
```
$ cat /etc/docker/daemon.json
{
  "storage-driver": "devicemapper",
  "storage-opts": [
    "dm.directlvm_device=/dev/mapper/docker-storage-host1",
    "dm.thinp_percent=95",
    "dm.thinp_metapercent=1",
    "dm.thinp_autoextend_threshold=80",
    "dm.thinp_autoextend_percent=20",
    "dm.directlvm_device_force=false"
  ]
}
```
Use `dm.directlvm_device_force=true` in case Docker does not properly start (might complain that device is not formatted).

Now, you can deploy all StorageGRID nodes, starting with the Admin Node(s):
```
$ cat dc1-adm1.conf
NODE_TYPE = VM_Admin_Node
ADMIN_ROLE = Primary

BLOCK_DEVICE_VAR_LOCAL = /dev/mapper/sgws-adm1-var-local
BLOCK_DEVICE_AUDIT_LOGS = /dev/mapper/sgws-adm1-audit-logs
BLOCK_DEVICE_TABLES = /dev/mapper/sgws-adm1-tables
GRID_NETWORK_TARGET = ens2f0
GRID_NETWORK_IP = 10.10.10.x
GRID_NETWORK_MASK = 255.255.255.0
GRID_NETWORK_GATEWAY = 10.10.10.1
```

Then over to the Storage Nodes:
```
$ cat dc1-s1.conf
NODE_TYPE = VM_Storage_Node
ADMIN_IP = 10.10.10.x
BLOCK_DEVICE_VAR_LOCAL = /dev/mapper/sgws-s1-var-local
BLOCK_DEVICE_RANGEDB_00 = /dev/mapper/sgws-s1-rangedb0
BLOCK_DEVICE_RANGEDB_01 = /dev/mapper/sgws-s1-rangedb1
BLOCK_DEVICE_RANGEDB_02 = /dev/mapper/sgws-s1-rangedb2
BLOCK_DEVICE_RANGEDB_03 = /dev/mapper/sgws-s1-rangedb3
BLOCK_DEVICE_RANGEDB_04 = /dev/mapper/sgws-s1-rangedb4
BLOCK_DEVICE_RANGEDB_05 = /dev/mapper/sgws-s1-rangedb5
BLOCK_DEVICE_RANGEDB_06 = /dev/mapper/sgws-s1-rangedb6
BLOCK_DEVICE_RANGEDB_07 = /dev/mapper/sgws-s1-rangedb7
BLOCK_DEVICE_RANGEDB_08 = /dev/mapper/sgws-s1-rangedb8
BLOCK_DEVICE_RANGEDB_09 = /dev/mapper/sgws-s1-rangedb9
BLOCK_DEVICE_RANGEDB_10 = /dev/mapper/sgws-s1-rangedb10
BLOCK_DEVICE_RANGEDB_11 = /dev/mapper/sgws-s1-rangedb11
BLOCK_DEVICE_RANGEDB_12 = /dev/mapper/sgws-s1-rangedb12
BLOCK_DEVICE_RANGEDB_13 = /dev/mapper/sgws-s1-rangedb13
BLOCK_DEVICE_RANGEDB_14 = /dev/mapper/sgws-s1-rangedb14
BLOCK_DEVICE_RANGEDB_15 = /dev/mapper/sgws-s1-rangedb15

GRID_NETWORK_TARGET = ens2f0
GRID_NETWORK_IP = 10.10.10.x
GRID_NETWORK_MASK = 255.255.255.0
GRID_NETWORK_GATEWAY = 10.10.10.1

CLIENT_NETWORK_TARGET = ens2f1
CLIENT_NETWORK_IP = 10.11.11.x
CLIENT_NETWORK_MASK = 255.255.255.0
```

## Notice

```
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```