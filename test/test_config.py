import common
import copy
import pytest
import seqlab.config as config
import cStringIO

conf_lines = [
    "[default]",
    "target_path = /var",
    "inbox_path = /usr/bin",
    "db_server = localhost",
    "db_port = 5432",
    "db_username = boris",
    "db_credentials = data/dbcredential",
    "db_name = mdx"]


def test_good_config_works():
    good_config = cStringIO.StringIO('\n'.join(conf_lines))
    assert config.read_configuration(good_config) == \
        {'target_path': '/var',
         'inbox_path': '/usr/bin', 
         'db_port': 5432, 'db_name': 'mdx', 
         'db_server': 'localhost', 'db_username': 'boris', 
         'db_credentials': 'data/dbcredential', 'db_password': 'root'}



def test_bad_values_fail():
    for i,s in [(4,"target_path = /wasdfkshdf"),
                (6,"inbox_path = /dfsdfhljfwe/wefsdfh")]:
        new_lines = copy.copy(conf_lines)
        new_lines[i] = s
        h = cStringIO.StringIO('\n'.join(new_lines))
        with pytest.raises(ValueError):
            config.read_configuration(h)
        

