from lithopscloud.modules.api_key import ApiKeyConfig
from lithopscloud.modules.gen2.lithops.ssh_key import LithopsSshKeyConfig
from lithopscloud.modules.gen2.lithops.endpoint import LithopsEndpointConfig
from lithopscloud.modules.gen2.lithops.vpc import LithopsVPCConfig
from lithopscloud.modules.gen2.lithops.image import LithopsImageConfig
from lithopscloud.modules.cos import CosConfig
from lithopscloud.modules.gen2.lithops.runtime import RuntimeConfig


MODULES = [ApiKeyConfig, LithopsEndpointConfig, LithopsVPCConfig, LithopsSshKeyConfig, LithopsImageConfig, CosConfig, RuntimeConfig]