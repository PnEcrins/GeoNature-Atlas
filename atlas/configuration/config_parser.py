"""
Utils pour lire le fichier de conf et le valider selon le schéma Marshmallow
"""

from importlib.machinery import SourceFileLoader


def get_config_module(atlas_config_file_path):
    # imports the module from the given path
    atlas_config = SourceFileLoader("config", atlas_config_file_path).load_module()
    return atlas_config


def read_config_file(config_module):
    return {var: getattr(config_module, var) for var in remove_reserved_word(config_module)}


def remove_reserved_word(config_module):
    return [var for var in dir(config_module) if not var.startswith("__")]


def valid_config_from_dict(config_dict, config_schema):
    return config_schema().load(config_dict)
