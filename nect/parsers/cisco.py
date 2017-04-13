from ciscoconfparse import CiscoPassword
from collections import defaultdict
from nect.parsers.generic import BaseParser
from nect.helpers import chunker, ensure_key, keydefaultdict, infinite_dd
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

    @ensure_key(Logging, Logging)
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
        self.host[NTPServer][cmd[0]]

    def _time(self, conf):
        cmd = conf.text.split()[1:]
        if cmd[0] == 'timezone':
            if not Time in self.host.items:
                self.host.items[Time] = Time(cmd[1], cmd[2])
            else:
                try:
                    self.host[Time].zone = cmd[1]
                    self.host[Time].offset = cmd[2]
                except IndexError:
                    pass
            # TODO: minutes-offset option
            # if len(cmd) == 4:
            #     self.config['clock']['minutes-offset'] = cmd[3]
        # TODO
        # elif cmd[0] == 'summer-time':
        else:
            self.incompatible.append(NotConvertible(conf.ioscfg))
    
    @ensure_key(AAA, AAA)
    def _aaa(self, conf):
        cmd = conf.text.split()
        if cmd[0] == 'tacacs-server':
            self._tacacs(conf)
        elif cmd[0] == 'aaa':
            if cmd[1] == 'new-model':
                self.host[AAA].enabled = True
            elif cmd[1] in ('accounting', 'authentication', 'authorization'):
                getattr(self.host[AAA], cmd[1])[cmd[2]][cmd[3]] = cmd[4:]
                # self.host[AAA][cmd[1]][cmd[2]][cmd[3]] = cmd[4:]
        else:
            self.incompatible.append(NotConvertible(conf.ioscfg))

    @ensure_key(TACACS, TACACS)
    def _tacacs(self, conf):
        cmd = conf.text.split()[1:]
        if not hasattr(self.host[TACACS], 'extra'):
            self.host[TACACS].extra = infinite_dd()
        if cmd[0] == 'host':
            try:
                connection = cmd.index('single-connection')
                self.host[TACACS].extra[cmd[1]]['single-connection'] = True
                del cmd[connection]
            except ValueError:
                pass
            finally:
                self.host[TACACS].extra[cmd[1]].update({
                    key:value for key, value in chunker(cmd[2:], 2)
                })
        elif cmd[0] == 'directed-request':
            self.host[TACACS].extra[cmd[0]] = True
        elif cmd[0] == 'timeout':
            self.host[TACACS].timeout = int(cmd[1])
        elif cmd[0]== 'key':
            self.host[TACACS].key = self.pass7.decrypt(cmd[2]) if cmd[1] == '7' else cmd[2]
        else:
            self.incompatible.append(NotConvertible(conf.ioscfg))

    @ensure_key(DNS, DNS)
    def _ip(self, conf):
        cmd = conf.text.split()[1:]
        if cmd[0] == 'default-gateway':
            self.host.default_gateway = cmd[1]
        elif cmd[0] == 'domain-name':
            self.host[DNS].domain_name = cmd[1]
            # self.config['ip']['dns']['domain-name'] = cmd[1]
        elif cmd[0] == 'domain-list':
            self.host[DNS].domain_list.append(cmd[1])
            # if not 'domain-list' in self.config['ip']['dns']:
            #     self.config['ip']['dns']['domain-list'] = []
            # self.config['ip']['dns']['domain-list'].append(cmd[1])
        elif cmd[0] == 'name-server':
            # if not 'servers' in self.config['ip']['dns']:
            #     self.config['ip']['dns']['servers'] = []
            # self.config['ip']['dns']['servers'].append(cmd[1])
            self.host[DNS].name_servers.append(cmd[1])
        else:
            self.incompatible.append(NotConvertible(conf.ioscfg))

    def _stp(self, conf):
        self.incompatible.append(NotConvertible(conf.ioscfg))

    def _snmp(self, conf):
        self.incompatible.append(NotConvertible(conf.ioscfg))


