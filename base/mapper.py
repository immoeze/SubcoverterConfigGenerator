import copy
import os
import ruamel.yaml

from utils.file_processor import ConfigProcessor, TemplateProcessor
from utils.file_path import File
from utils.uid_generator import touch_uid


class __BaseMapper__:

    class __ConfigGetter__():
        """
        An easier way to get key-value in config
        """
        def __init__(self, value: str) -> None:
            self._value = value
            self.default_value = self._value

        def get(self, target: None):
            self._value = self._value[target]
            return self
        
        def value(self):
            """
            return the value of the config session.
            """
            t = self._value
            self._value = self.default_value
            return t

    class __TemplateGetter__(__ConfigGetter__):
        def __init__(self, value: str) -> None:
            super().__init__(value)

    def __init__(self) -> None:
        self.config_processor_obj = ConfigProcessor()
        self.template_processor_obj = TemplateProcessor()

        self.raw_config_file = self.config_processor_obj.load(filepath=File.config)
        self.raw_template_file = self.template_processor_obj.load(filepath=File.clash_template)

        self.config_getter = self.__ConfigGetter__(self.raw_config_file)
        self.template_getter = self.__TemplateGetter__(self.raw_template_file)

        self.template_type: str = None


class ClashMapper(__BaseMapper__):

    def __init__(self) -> None:
        super().__init__()
        self.raw_clash_template = self.template_processor_obj.load(filepath=File.clash_template)
        self.template_type = 'clash'
    
    def _config(self, key: str) -> __BaseMapper__.__ConfigGetter__:
        """
        An easier way to get config file's value
        """
        _dict = {
            "sub_token": self.config_getter.get('SUB_TOKEN').value(),
            "airports": self.config_getter.get('AIRPORTS').value(),
            "uam": self.config_getter.get('USER_AIRPORTS_MAPPERS').value(),
            "sub_url_formatter": self.config_getter.get('SUB_URL_FORMATTER').value(),
        }
        return _dict.get(key)

    def start(self):
        for airports_type in self._config('uam'):
            if airports_type == 'clash':
                self.process_clash_template()
            elif airports_type == 'quanx':
                print('- Profile for quanx is defined in config but not designed complete yet.')
                continue
            else:
                raise 'TO BE DONE'

    def process_clash_template(self):
        """
        Dump sub-config for each user in a for-loop
        """
        for username in self._config('uam').get('clash'):
            # Create a clash template copy to edit
            clash_data = copy.deepcopy(self.raw_clash_template)
            # Edit proxy-providers and proxy-groups
            self.process_clash_template_proxy_providers(username, clash_data)
            self.process_clash_template_proxy_groups_use(username, clash_data)
            # Dump clash config file for the user
            self.dump_clash_template_for_users(username, clash_data)

    def process_clash_template_proxy_providers(self, username: str, clash_data: TemplateProcessor.load):

        def gen_proxy_provider(ap_name: str, ap_url: str):
            ap_url = ap_url.replace('{SUB_TOKEN}', self._config('sub_token'))
            rst = proxy_provider_template.replace('__name__', ap_name.lower()).replace('__url__', ap_url.lower())
            return ruamel.yaml.safe_load(rst)

        # Load proxy_provider_template and delete it from the config template
        proxy_provider_template = "{'type': 'http', 'url': '__url__', 'interval': 3600, 'path': './profiles/provider/__name__.yaml', 'health-check': {'enable': True, 'interval': 600, 'url': 'http://www.gstatic.com/generate_204'}}"
        
        ap_list: list[str,] = self._config('uam').get('clash').get(username)
        for ap in ap_list:
            ap_url = self.config_getter.get('AIRPORTS').get(ap).value()
            clash_data['proxy-providers'][ap.lower()] = gen_proxy_provider(ap, ap_url)
        del clash_data['proxy-providers']['__name__']

    def process_clash_template_proxy_groups_use(self, username: str, clash_data):
        loop_counter = 0
        for item in self.template_getter.get('proxy-groups').value():
            try:
                proxy_policy_all = self._config('uam').get('clash').get(username)
                proxy_policy_default = [proxy_policy_all[0]]
                if proxy_group_use_policy := item['use'][0]:
                    clash_data['proxy-groups'][loop_counter]['use'] = copy.deepcopy(proxy_policy_all if proxy_group_use_policy == 'all' else proxy_policy_default)
            except KeyError:
                continue
            finally:
                loop_counter += 1

    def dump_clash_template_for_users(self, username, clash_data):
        uuid = touch_uid(username)
        self.template_processor_obj.dump(filepath=os.path.join(File.dump_proxy_clash, uuid), data=clash_data)
        
        if (suf := self._config('sub_url_formatter')):
            url_fix_root = suf if suf.endswith('/') else suf+'/'
            print(f'+ Config file for user: {username} (uid:{uuid}) has been generated, url: {url_fix_root}proxy/{self.template_type}/{uuid}')


