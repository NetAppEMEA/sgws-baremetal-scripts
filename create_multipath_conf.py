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


file = open('multipath.conf','w') 
file.write('multipaths {\n')

vol_a = vol_api.get_all_volumes(system_id='1c57c70c-bc5f-4f8c-a6a7-34cdb2cafc3a')
vol_b = vol_api.get_all_volumes(system_id='b6856c5b-5aa6-45d6-a64d-fcefcb2bf676')

volumes = vol_a + vol_b
for v in volumes:
	file.write('     multipath {\n')
	file.write('          wwid 3' + v.world_wide_name.lower() + '\n')
	file.write('          alias ' + v.label + '\n')
	file.write('     }\n')
	
file.write('}\n')
file.close() 

pprint(volumes)
