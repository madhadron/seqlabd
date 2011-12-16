import common
import copy
import pytest
import seqlablib.config
import cStringIO

conf_lines = [
    "[default]",
    "# All times are measured in seconds by default.",
    "batch_timeout=20",
    "slurp_timeout=900",
    "share_path = /var",
    "base_path = log",
    "inbox_path = /usr/bin",
    "unmatched_path = /usr/lib",
    "# The password must be handled by a .pgpass file or some other method",
    "db_server = localhost",
    "db_username = boris",
    "# How many time to retry something that didn't work out.",
    "max_retries = 5"]


def test_good_config_works():
    good_config = cStringIO.StringIO('\n'.join(conf_lines))
    assert seqlablib.config.read_configuration(good_config) == \
        {'batch_timeout': 20, 'slurp_timeout': 900,
         'share_path': '/var', 'base_path': 'log',
         'inbox_path': '/usr/bin', 'unmatched_path': '/usr/lib',
         'db_server': 'localhost', 'db_username': 'boris', 'max_retries': 5}


def test_bad_values_fail():
    for i,s in [(4,"share_path = /wasdfkshdf"),
                (5,"base_path = sdfkjshfdf/weraksdfhjds"),
                (6,"inbox_path = /dfsdfhljfwe/wefsdfh"),
                (7,"unmatched_path = /asdfsdhdsfsd/wasdfhfs"),
                (2,"batch_timeout=-51"),
                (3,"slurp_timeout=-3"),
                (12,"max_retries=-5")]:
        new_lines = copy.copy(conf_lines)
        new_lines[i] = s
        h = cStringIO.StringIO('\n'.join(new_lines))
        with pytest.raises(ValueError):
            seqlablib.config.read_configuration(h)
        

