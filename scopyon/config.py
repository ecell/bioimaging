import collections.abc
import contextlib
import io
import pkgutil

from logging import getLogger
_log = getLogger(__name__)


def dict_merge(dct, merge_dct):
    for k, v in merge_dct.items():
        if isinstance(dct.get(k), dict) and isinstance(v, collections.Mapping):
            dict_merge(dct[k], v)
        else:
            dct[k] = v

class Configuration(collections.abc.Mapping):
    """

    Note:
        Requires `yaml`.
    """

    def __init__(self, filename=None, yaml=None):
        if filename is not None:
            assert yaml is None
            import yaml
            try:
                from yaml import CLoader as Loader
            except ImportError:
                from yaml import Loader
            with open(filename) as f:
                self.__yaml = yaml.load(f.read(), Loader=Loader)
        elif yaml is not None:
            self.__yaml = yaml
        else:
            self.__yaml = None

    def __repr__(self):
        import yaml
        try:
            from yaml import CDumper as Dumper
        except ImportError:
            from yaml import Dumper
        return yaml.dump(self.__yaml, default_flow_style=False, Dumper=Dumper)

    def update(self, conf):
        if isinstance(conf, Configuration):
            dict_merge(self.__yaml, conf.yaml)
        elif isinstance(conf, dict):
            dict_merge(self.__yaml, conf)
        else:
            import yaml
            try:
                from yaml import CLoader as Loader
            except ImportError:
                from yaml import Loader
            dict_merge(self.__yaml, yaml.load(conf, Loader=Loader))

    @property
    def yaml(self):
        return self.__yaml

    def get(self, key, defaultobj=None):
        return self.__yaml.get(key, defaultobj)

    def __getitem__(self, key):
        return getattr(self, key)
        # value = self.__yaml[key]
        # if isinstance(value, dict):
        #     assert 'value' in value
        #     return value['value']
        # return value

    def __len__(self):
        return len(self.__yaml)

    def __iter__(self):
        return (key for key, value in self.__yaml.items() if not isinstance(value, dict) or 'value' in value)

    def __getattr__(self, key):
        assert key in self.__yaml
        value = self.__yaml[key]
        if isinstance(value, dict):
            if 'value' not in value:
                return Configuration(yaml=value)
            else:
                return value['value']
        return value

    def __setattr__(self, key, value):
        if key.startswith('_'):
            object.__setattr__(self, key, value)
            return

        assert key in self.__yaml
        assert not isinstance(value, dict)
        value_ = self.__yaml[key]
        if isinstance(value_, dict):
            if 'value' not in value_:
                return Configuration(yaml=value_)
            else:
                value_['value'] = value
        self.__yaml[key] = value

class DefaultConfiguration(Configuration):

    def __init__(self):
        import yaml
        try:
            from yaml import CLoader as Loader
        except ImportError:
            from yaml import Loader
        with contextlib.closing(io.StringIO(pkgutil.get_data("scopyon", "scopyon.yml").decode())) as f:
            data = yaml.load(f.read(), Loader=Loader)

        Configuration.__init__(self, yaml=data)
