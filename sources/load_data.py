import yaml
from os.path import join


def load_config(file_name="config.yaml"):
    try:
        with open(join(file_name)) as yaml_file:
            doc = yaml.load(yaml_file)
        return doc
    except:
        raise Exception("Can't load config file")
