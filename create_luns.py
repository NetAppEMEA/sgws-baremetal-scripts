#/usr/bin/python

from netapp.santricity.configuration import Configuration
from netapp.santricity.api_client import ApiClient
from netapp.santricity.api.v2.storage_systems_api import StorageSystemsApi
from netapp.santricity.api.v2.volumes_api import VolumesApi
from netapp.santricity.api.v2.hardware_api import HardwareApi
from netapp.santricity.models.v2.drive_selection_request import DriveSelectionRequest
from netapp.santricity.models.v2.storage_pool_create_request import StoragePoolCreateRequest
from netapp.santricity.models.v2.volume_create_request import VolumeCreateRequest
from netapp.santricity.models.v2.volume_mapping_create_request import VolumeMappingCreateRequest

from pprint import pprint
import csv

config = Configuration()
config.host = "http://<E-Series Address>:18080" 
config.username = "rw"
config.password = "rw"

api_client = ApiClient()
config.api_client = api_client

storage_system = StorageSystemsApi(api_client=api_client)
ssr = storage_system.get_all_storage_systems()

print ssr

vol_api = VolumesApi(api_client=api_client)

with open('config.csv') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		lun_name=row['lun_name']
		size=row['size']
		count=int(row['count'])
		eseries_target=row['eseries_target']
		pool=row['pool']
		host_mapping=row['host_mapping']
		owning_controller_id=row['owning_controller_id']
	    print(lun_name, size)

        for x in range(0, int(count)):
            vol_req_obj = VolumeCreateRequest()
            
            # only add counter if more than one luns are created
            if (count > 1):
                vol_req_obj.name = lun_name + str(x)
            else:
                vol_req_obj.name = lun_name

            vol_req_obj.pool_id = pool
            vol_req_obj.size_unit = "gb"
            vol_req_obj.size = size
            vol_req_obj.owning_controller_id = owning_controller_id
            pprint("Creating volume: " + vol_req_obj.name)
            vol_h = vol_api.new_volume(system_id=eseries_target, body=vol_req_obj)
            pprint(vol_h)
            vol_map_req = VolumeMappingCreateRequest()
            vol_map_req.mappable_object_id = vol_h.id
            vol_map_req.target_id = host_mapping
            pprint("Mapping Volume" + vol_h.id + " to host: " + host_mapping)
            vol_m = vol_api.new_lun_mapping(system_id=eseries_target, body=vol_map_req)
            pprint(vol_m)