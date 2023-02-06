import shutil
import sys
import os
import ruamel.yaml

from utils.file_path import File


class __BASE__:
    """
    Base class for config loader and template loader
    """
    def __init__(self) -> None:
        # Init an empty template object
        self.file_data = None
        
        # Judge the file is config or template
        self.file_type = None

        # Custom yaml style
        self.yaml = ruamel.yaml.YAML()
        self.yaml.preserve_quotes = True
        self.yaml.allow_unicode = True
        self.yaml.default_flow_style = True
        self.yaml.indent = 4
        self.yaml.block_seq_indent = 2

        # Preserver a flat to keey yaml comments that is not used yet.
        self.keep_yaml_comments = False
    
    def load(self, filepath: str):
        """
        Load yaml file, and return it as a ruamel yaml object
        """
        try:
            with open(file=filepath, mode='r', encoding='utf-8') as fr:
                content = ruamel.yaml.load(fr, Loader=ruamel.yaml.RoundTripLoader)
            self.file_data = content
            return content
        except FileNotFoundError as e:
            # File not found, copy it from /resources and exit
            self.copy_to_root()
            print(f'File {self.file_type} not existed, it has been generated, please modify it or run again.')
            sys.exit(0)
    
    def copy_to_root(self):
        """
        If file is not exist, copy it from /resuorces or system resource folder to the root
        """
        # BUG: 严重错误涉及 pyinstaller 打包文件资源路径
        bundle_resource_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        path_to_file = os.path.abspath(os.path.join(bundle_resource_dir, self.file_type + '.yml'))
        
        _file_type = File.default_config if self.file_type == 'config' else File.default_clash_template
        if os.path.exists(path_to_file):
            shutil.copy(src=path_to_file, dst=_file_type)
        else:
            shutil.copy(src=_file_type, dst=File.root)


class TemplateProcessor(__BASE__):
    """
    Load and dump template
    """

    def __init__(self) -> None:
        super().__init__()
        self.file_type = 'template'

    def dump(self, filepath: str, data):
        """
        Some comments will get lost during the run.
        """
        try:
            # If folder not exist, create it
            if not os.path.exists(_dir := os.path.dirname(filepath)):
                os.makedirs(name=os.path.dirname(filepath))
            # Write yaml-data to the file
            with open(file=filepath, mode='w+', encoding='utf-8') as fo:
                ruamel.yaml.dump(
                    data=data, stream=fo,
                    Dumper=ruamel.yaml.RoundTripDumper,
                    allow_unicode=True, default_flow_style=False,
                    indent=4, block_seq_indent=2
                )
        except IOError as ioerror:
            raise ioerror

    

class ConfigProcessor(__BASE__):
    """
    Load config only
    """

    def __init__(self) -> None:
        super().__init__()
        self.file_type = 'config'
