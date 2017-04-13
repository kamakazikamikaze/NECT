from collections import defaultdict
from ciscoconfparse import CiscoConfParse
import logging
from nect.items.generic import *
from weakref import WeakValueDictionary
from weakreflist import WeakList

try:
    range = xrange
except NameError:
    pass


class BaseParser(object):
    def __init__(self, configuration, comment='!',
                 logfile=None, log_severity=2):
        self.host = None
        self.parser = CiscoConfParse(
            configuration, factory=True, comment=comment)
        self.comment = comment
        # self.incompatible = WeakList()
        self.incompatible = []
        if logfile:
            self._setuplogging(logfile, log_severity)
        self.actions = {
            'alias': self._alias,
            'hostname': self._hostname,
            'interface': self._interface,
            'vlan': self._vlan,
            self.comment: self._nothing
        }
        self._update_actions()

    def _update_actions(self):
        pass

    def __repr__(self):
        return '<BaseParser>'

    def __getitem__(self, item):
        return self.host[item]

    # TODO
    def _setuplogging(self, logfile, log_severity):
        logging.getLogger(str(self.__class__))

    # We can't pass parameters to `pass`, An empty method is currently needed
    def _nothing(self, *args, **kwargs):
        pass

    def parse(self):
        self.host = Host()
        objs = self.parser.find_objects('^\S.+')
        for obj in objs:
            command = obj.text.split()
            # TODO: Handle 'no' definitions
            index = 0 if command[0] != 'no' else 1
            if command[index] not in self.actions:
                self.incompatible.append(NotConvertible(obj.ioscfg))
            else:
                self.actions[command[index]](obj)

    def _hostname(self, conf):
        self.host.name = conf.text.split()[1].strip('"')

    def _interface(self, conf):
        try:
            self.host[Interface].append(Interface(name=conf.text.split()[1],
                                                  config=conf.ioscfg[1:]))
        # Empty configuration
        except IndexError:
            pass

    def _vlan(self, conf):
        try:
            number = int(conf.text.split()[1])
            self.host[VLAN].append(VLAN(number))
        except ValueError:
            self.incompatible.append(NotConvertible(conf.ioscfg))

    def _alias(self, conf):
        self.host[Alias].append(Alias(conf.ioscfg))