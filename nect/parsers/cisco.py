from ciscoconfparse import CiscoPassword
from collections import defaultdict
from nect.parsers.generic import BaseParser
from nect.helpers import keydefaultdict, chunker
from nect.items.generic import *
from weakref import WeakValueDictionary

class CiscoBaseParser(BaseParser):
    def _update_actions(self):
        self.actions.update({
            'logging': self._logging,
            'ntp': self._ntp,
            'clock': self._time,
            'tacacs-server': self._aaa,
            'ip': self._ip,
            'aaa': self._aaa,
            'snmp-server': self._snmp,
            '!': self._nothing,
        })
        self.pass7 = CiscoPassword()
        
    def __repr__(self):
        return '<CiscoBaseParser>'
    
    log_levels = {
        'emergencies': 0,
        'alerts': 1,
        'critical': 2,
        'errors': 3,
        'warnings': 4,
        'notifications': 5,
        'informational': 6,
        'debugging': 7
    }

    def device(self, conf):
        pass

    def _logging(self, conf):
        if conf.text.split()[1:] == 'host':
            self._log_server(conf)
        else:
            self._log_local(conf)

    @ensure_key(LocalLogging, LocalLogging)
    def _log_local(self, conf):
        cmd = conf.text.split()[1:]
        if cmd[0] == 'file':
            local_log = self.host[LocalLogging]
            local_log.filename = cmd[1]
            local_log.max_size = cmd[2]
            local_log.file_size = cmd[3]
            self.host[Logging].levels.append(('file', cmd[4]))
        elif cmd[0] == 'buffered':
            self.host[LocalLogging].buffer_size = cmd[1]
        elif cmd[0] in ('console', 'trap'):
            self.host[Logging].levels.append((cmd[0], cmd[1]))
        else:
            self.incompatible.append(
                NotConvertible(['logging ' + ''.join(cmd)]))

    @ensure_key(LogServer, keydefaultdict(LogServer))
    def _log_server(self, conf):
        cmd = conf.text.split()[1:]
        for key, value in chunker(cmd[2:], 2):
            if key == 'port':
                self.host[LogServer][cmd[1]].port = value
            elif key == 'transport':
                self.host[LogServer][cmd[1]].proto = value
            else:
                self.incompatible.append(
                    NotConvertible(conf.ioscfg))

    @ensure_key(NTP, NTP)
    def _ntp(self, conf):
        cmd = conf.text.split()[1:]
        if cmd[0] == 'server':
            self._ntp_server(conf)
        # TODO: Handle additional NTP options
        # elif cmd[0] == 'clock-period':
        #     self.config['ntp'][cmd[0]] = cmd[1]
        else:
            self.incompatible.append(NotConvertible(conf.ioscfg))

    @ensure_key(NTPServer, keydefaultdict(NTPServer))
    def _ntp_server(self, conf):
        cmd = conf.text.split()[2:]
        # keydefaultdict will pass the key value as a parameter. Will add more
        # in the future
        self.host[NTPServer][cmd[2]]

    @ensure_key()
    def time(self, conf):
        cmd = conf.text.split()[1:]
        if cmd[0] == 'timezone':
            self.config['clock'].update({
                    'zone': cmd[1],
                    'hours-offset': cmd[2]
                })
            if len(cmd) == 4:
                self.config['clock']['minutes-offset'] = cmd[3]
        elif cmd[0] == 'summer-time':
            if cmd[1] not in ('date', 'recurring'):
                self.config['clock']['DST']['zone'] = cmd[1]
                del cmd[1]
            if cmd[1] == 'date':
                pass
            elif cmd[1] == 'recurring':
                if ':' not in cmd[-1]:
                    self.config['clock']['DST']['offset'] = cmd[-1]
                    del cmd[-1]
                # TODO
        else:
            self.config['incompatible'].append(conf.ioscfg)
    
    def aaa(self, conf):
        cmd = conf.text.split()
        if cmd[0] == 'tacacs-server':
            if cmd[1] == 'host':
                try:
                    connection = cmd.index('single-connection')
                    self.config['aaa']['tacacs']['hosts'][cmd[2]]['single-connection'] = True
                    del cmd[connection]
                except ValueError:
                    pass
                self.config['aaa']['tacacs']['hosts'][cmd[2]].update({
                        key:value for key, value in chunker(cmd[3:], 2)
                    })
            elif cmd[1] == 'directed-request':
                self.config['aaa']['tacacs'][cmd[1]] = True
            elif cmd[1] == 'timeout':
                self.config['aaa']['tacacs'][cmd[1]] = cmd[2]
            elif cmd[1]== 'key':
                self.config['aaa']['tacacs'][cmd[1]] = self.pass7.decrypt(cmd[3]) if cmd[2] == '7' else cmd[3]
            else:
                self.config['incompatible'].append(conf.ioscfg)

        elif cmd[0] == 'aaa':
            if cmd[1] == 'new-model':
                self.config['aaa']['enabled'] = True
            elif cmd[1] in ('accounting', 'authentication', 'authorization'):
                self.config[cmd[0]][cmd[1]][cmd[2]][cmd[3]] = cmd[4:]
        else:
            self.config['incompatible'].append(conf.ioscfg)

    def ip(self, conf):
        cmd = conf.text.split()[1:]
        if cmd[0] == 'default-gateway':
            self.config['ip']['default-gateway'] = cmd[1]
        elif cmd[0] == 'domain-name':
            self.config['ip']['dns']['domain-name'] = cmd[1]
        elif cmd[0] == 'domain-list':
            if not 'domain-list' in self.config['ip']['dns']:
                self.config['ip']['dns']['domain-list'] = []
            self.config['ip']['dns']['domain-list'].append(cmd[1])
        elif cmd[0] == 'name-server':
            if not 'servers' in self.config['ip']['dns']:
                self.config['ip']['dns']['servers'] = []
            self.config['ip']['dns']['servers'].append(cmd[1])
        else:
            self.config['incompatible'].append(conf.ioscfg)

    def stp(self, conf):
        self.config['incompatible'].append(conf.ioscfg)

    def snmp(self, conf):
        self.config['incompatible'].append(conf.ioscfg)


