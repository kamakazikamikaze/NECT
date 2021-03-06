from weakref import WeakSet
import pytz


class ConfigItem(object):

    def __init__(self, **kwargs):
        for arg, val in kwargs.iteritems():
            setattr(self, arg, val)

    _regex = None

# Equipment


class Stackable(ConfigItem):
    r'''
    Logical representation of a multi-device stack
    '''

    def __init__(self, hostname='AutoGenerated', devices=[]):
        kwargs = locals()
        del kwargs['self']
        super(Stackable, self).__init__(**kwargs)

    def add_device(self, device, member=None):
        if member and member <= len(self.devices):
            self.devices.insert(member, device)
        else:
            self.devices.append(device)


class Equipment(ConfigItem):
    r'''
    Layer 2/3 device, such as a Switch, Router, Firewall, etc.
    '''

    def __init__(self, hostname='AutoGenerated'):
        self.hostname = hostname

# Interfaces


class Interface(ConfigItem):
    r'''
    Base class for all configurable Layer 2 and 3 objects that deal with
    logical data flow
    '''

    def __init__(self, **kwargs):
        if 'self' in kwargs:
            del kwargs['self']
        super(Interface, self).__init__(**kwargs)


class Vlan(Interface):
    r'''
    VLAN definitions and configuration
    '''

    def __init__(self, number=1, descr=None, ip_addr=None,
                 subnet_mask=None, ports={}):
        kwargs = locals()
        del kwargs['self']
        super(Vlan, self).__init__(**kwargs)
        ports['tagged'] = WeakSet()
        ports['untagged'] = WeakSet()

    def add_port(self, port, tagging=('untagged',)):
        r'''
        Declare that a VLAN is to be (un)tagged on the given port

        :param Port port: Port object to associate to
        :param tagging: 'tagged', 'untagged', or both in an iterative object
        :type tagging: str, iter(str)
        '''
        if not tagging:
            tagging = ('untagged', )
        elif isinstance(tagging, str):
            tagging = (tagging, )
        for tag in tagging:
            self.ports[tag].add(port)

    def del_port(self, port, tagging=('tagged', 'untagged')):
        r'''
        Declare that a VLAN is no longer (un)tagged on the given port.

        :param Port port: Port object to disassociate from
        :param tagging: 'tagged', 'untagged', or both in an iterative object
        :type tagging: str or iter(str)
        '''
        if isinstance(tagging, str):
            tagging = (tagging, )
        for tag in tagging:
            try:
                self.ports[tag].remove(port)
            except ValueError:
                pass


class Port(Interface):
    r'''
    Physical Interface
    '''

    def __init__(self, name, descr=None, baseT=1000, speed='auto',
                 duplex='auto', mode=None, vlans={}):
        # Lazy parameter setting
        kwargs = locals()
        del kwargs['self']
        super(Port, self).__init__(**kwargs)
        vlans['tagged'] = WeakSet()
        vlans['untagged'] = WeakSet()

    def add_vlan(self, vlan, tagging=('untagged',)):
        r'''
        Set a Vlan to be (un)tagged for this Port.

        :param vlan:
        '''
        if isinstance(tagging, str):
            tagging = (tagging, )
        for tag in tagging:
            self.vlans[tag].add(vlan)

    def del_vlan(self, vlan, tagging=('tagged', 'untagged')):
        r'''
        Set a Vlan to be (un)tagged for this Port.

        :param vlan:
        '''
        if isinstance(tagging, str):
            tagging = (tagging, )
        for tag in tagging:
            try:
                self.vlans[tag].remove(vlan)
            except ValueError:
                pass

    def set_ip(self, address, mask):
        self.address = address
        self.mask = mask


class LinkAgg(Interface):
    r'''
    LACP, PAgP, plain Etherchannel, etc.
    '''

    def __init__(self, name, members):
        kwargs = locals()
        del kwargs['self']
        super(LinkAgg, self).__init__(**kwargs)


Mgmt = Interface


class Console(Mgmt):

    def __init__(self, enabled=True, timeout=300, usb=False, baud=None):
        kwargs = locals()
        del kwargs['self']
        super(Console, self).__init__(**kwargs)


class OOBM(Mgmt):
    r'''
    Out-of-band Management interface configuration
    '''

    def __init__(self):
        pass


class Web(Mgmt):
    r'''
    Web UI
    '''

    def __init__(self, enabled=False, secure=False):
        kwargs = locals()
        del kwargs['self']
        super(Web, self).__init__(**kwargs)


# IP


class IP(ConfigItem):
    r'''
    IP settings
    '''

    def __init__(self, **kwargs):
        super(IP, self).__init__(**kwargs)


class IPv6(ConfigItem):
    r'''
    '''


class DNS(IP):
    r'''
    Domain settings
    '''

    def __init__(self, domain_name, servers=[], domain_list=None):
        kwargs = locals()
        del kwargs['self']
        super(DNS, self).__init__(**kwargs)


# Auth


Auth = ConfigItem


class AAA(Auth):
    r'''
    Authentication, Authorization, and Accounting objects
    '''

    def __init__(self, authentication, authorization, accounting):
        kwargs = locals()
        del kwargs['self']
        super(AAA, self).__init__(**kwargs)


class Tacacs(Auth):
    r'''
    '''

    def __init__(self, servers=[], key='', timeout=1):
        self.servers = servers
        self.key = key
        self.timeout = timeout


class Radius(Auth):
    r'''
    Stub
    '''

    def __init__(self):
        pass


class User(Auth):
    r'''
    '''

    def __init__(self, username, password, password_type, privilege, **meta):
        kwargs = locals()
        del kwargs['self']
        del kwargs['meta']
        kwargs.update(meta)
        super(User, self).__init__(**kwargs)

# Logging


class Logging(ConfigItem):
    r'''
    Logging settings and services
    '''

    def __init__(self, levels=[], **kwargs):
        kwargs.update({'levels': levels})
        super(Logging, self).__init__(**kwargs)


class LogServer(Logging):
    r'''
    Logging servers and preferences
    '''

    def __init__(self, address, name=None, port=None, proto=None):
        kwargs = locals()
        del kwargs['self']
        super(LogServer, self).__init__(**kwargs)


LANSecurity = ConfigItem


class DHCPSnooping(LANSecurity):

    def __init__(self, enabled, vlans, ports):
        kwargs = locals()
        del kwargs['self']
        super(DHCPSnooping, self).__init__(**kwargs)

# SNMP


SNMP = ConfigItem


class SNMPServer(SNMP):
    r'''
    '''

    def __init__(self, ip, community):
        kwargs = locals()
        del kwargs['self']
        super(SNMPServer, self).__init__(**kwargs)


class SNMPCommunity(SNMP):
    r'''
    '''

    def __init__(self, community, permissions='ro'):
        kwargs = locals()
        del kwargs['self']
        super(LogServer, self).__init__(**kwargs)


class SNMPTraps(SNMP):
    r'''
    '''

    def __init__(self, traps=[]):
        kwargs = locals()
        del kwargs['self']
        super(LogServer, self).__init__(**kwargs)


# Spanning Tree


Discovery = ConfigItem


class STP(Discovery):
    r'''
    Spanning-tree protocol
    '''

    def __init__(self):
        pass


class CDP(Discovery):
    r'''
    Cisco Discovery Protocol preferences
    '''

    def __init__(self, enabled=False):
        pass


class LLDP(Discovery):
    r'''
    Link-Layer Discovery Protocol preferences
    '''

    def __init__(self, enabled=False):
        pass


# Time


class Time(ConfigItem):
    r'''
    Local time options
    '''

    def __init__(self, zone):
        self.zone = zone


class NTP(ConfigItem):
    r'''
    (S)NTP preferences
    '''

    def __init__(self, address, name='NTP', proto=None):
        self.address = address
        self.name = name
        # TCP or UDP
        self.proto = None

# Quirks


class Banner(ConfigItem):
    r'''
    Login, MOTD, or Logout messages for legal reasons
    '''

    def __init__(self, message, when):
        # when is any of ['connect', 'login', 'logout']
        kwargs = locals()
        del kwargs['self']
        super(Banner, self).__init__(**kwargs)


class NonConvertable(ConfigItem):
    r'''
    Commands that are either vendor-proprietary or are not directly
    translatable, such as `alias` commands
    '''

    def __init__(self, commands=[], **kwargs):
        extras = locals()
        del extras['self']
        del extras['kwargs']
        kwargs.update(extras)
        super(NonConvertable, self).__init__(**kwargs)
