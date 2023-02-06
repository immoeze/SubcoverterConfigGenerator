import os


class File:
    root = os.getcwd()
    main = os.path.join(root, 'main.py')
    resourecs_folder = os.path.join(root, 'resources')

    config = os.path.join(root, 'config.yml')
    default_config = os.path.join(resourecs_folder, 'config.yml')

    clash_template = os.path.join(root, 'clash_template.yml')
    quanx_template = os.path.join(root, 'quanx_template.yml')
    default_clash_template = os.path.join(resourecs_folder, 'clash_template.yml')

    dump_proxy_root = os.path.join(root, 'proxy')
    dump_proxy_clash = os.path.join(dump_proxy_root, 'clash')
    dump_proxy_quanx = os.path.join(dump_proxy_root, 'quanx')
