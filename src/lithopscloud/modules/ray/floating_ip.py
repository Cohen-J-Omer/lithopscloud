from lithopscloud.config_builder import update_decorator
from lithopscloud.modules.endpoint import EndpointConfig
from typing import Any, Dict

from lithopscloud.vpc_config_helper import get_option_from_list

class FloatingIpConfig(EndpointConfig):
    
    def __init__(self, base_config: Dict[str, Any]) -> None:
        super().__init__(base_config)

    def run(self) -> Dict[str, Any]:
        head_ip = None
        floating_ips = self.ibm_vpc_client.list_floating_ips().get_result()['floating_ips']
        
        free_floating_ips = [x for x in floating_ips if not x.get('target')]
        if free_floating_ips:
            ALLOCATE_NEW_FLOATING_IP = 'Allocate new floating ip'
            head_ip_obj = get_option_from_list("Choose head ip", free_floating_ips, choice_key='address', do_nothing=ALLOCATE_NEW_FLOATING_IP)
            if head_ip_obj and (head_ip_obj != ALLOCATE_NEW_FLOATING_IP):
                head_ip = head_ip_obj['address']
                
            if self.base_config.get('available_node_types'):
                for available_node_type in self.base_config['available_node_types']:
                    if head_ip:
                        self.base_config['available_node_types'][available_node_type]['node_config']['head_ip'] = head_ip
                    else:
                        self.base_config['available_node_types'][available_node_type]['node_config'].pop('head_ip', None)
            else:
                self.base_config['available_node_types']['ray_head_default']['node_config']['head_ip'] = head_ip

        return self.base_config