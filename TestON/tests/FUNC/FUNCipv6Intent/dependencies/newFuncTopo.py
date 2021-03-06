# !/usr/bin/python
"""
Copyright 2015 Open Networking Foundation ( ONF )

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    ( at your option ) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
Custom topology for Mininet
"""
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Host, RemoteController
from mininet.node import Node
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.util import dumpNodeConnections
from mininet.node import ( UserSwitch, OVSSwitch, IVSSwitch )


class VLANHost( Host ):

    def config( self, vlan=100, v6Addr='3000::1/64', **params ):
        r = super( Host, self ).config( **params )
        intf = self.defaultIntf()
        self.cmd( 'ifconfig %s inet 0' % intf )
        self.cmd( 'vconfig add %s %d' % ( intf, vlan ) )
        self.cmd( 'ifconfig %s.%d inet %s' % ( intf, vlan, params[ 'ip' ] ) )
        self.cmd( 'ip -6 addr add %s dev %s.%d' % ( v6Addr, intf, vlan ) )
        newName = '%s.%d' % ( intf, vlan )
        intf.name = newName
        self.nameToIntf[ newName ] = intf
        return r


class IPv6Host( Host ):

    def config( self, v6Addr='1000::1/64', **params ):
        r = super( Host, self ).config( **params )
        intf = self.defaultIntf()
        self.cmd( 'ifconfig %s inet 0' % intf )
        self.cmd( 'ip -6 addr add %s dev %s' % ( v6Addr, intf ) )
        return r


class dualStackHost( Host ):

    def config( self, v6Addr='2000:1/64', **params ):
        r = super( Host, self ).config( **params )
        intf = self.defaultIntf()
        self.cmd( 'ip -6 addr add %s dev %s' % ( v6Addr, intf ) )
        return r


class MyTopo( Topo ):

    def __init__( self ):
        # Initialize topology
        Topo.__init__( self )
        # Switch S5 Hosts
        host1 = self.addHost( 'h1', cls=IPv6Host, v6Addr='10:1:0::1/64' )
        host2 = self.addHost( 'h2', cls=IPv6Host, v6Addr='1000::2/64' )
        # Dual Stack Host
        host3 = self.addHost( 'h3', cls=dualStackHost, v6Addr='2000::2/64' )
        host4 = self.addHost( 'h4', cls=IPv6Host, v6Addr='3000::2/64' )
        # VLAN
        host5 = self.addHost( 'h5', cls=VLANHost, v6Addr='4000::2/64' )
        host6 = self.addHost( 'h6', cls=IPv6Host, v6Addr='11:1:0::2/64' )
        host7 = self.addHost( 'h7', cls=IPv6Host, v6Addr='12:1:0::2/64' )
        host8 = self.addHost( 'h8', cls=IPv6Host, v6Addr='10:1:0::4/64' )

        # Switch S6 Hosts
        host9 = self.addHost( 'h9', cls=IPv6Host, v6Addr='10:1:0::5/64' )
        host10 = self.addHost( 'h10', cls=IPv6Host, v6Addr='1000::3/64' )
        # Dual Stack Host
        host11 = self.addHost( 'h11', cls=dualStackHost, v6Addr='2000::3/64' )
        host12 = self.addHost( 'h12', cls=IPv6Host, v6Addr='3000::3/64' )
        host13 = self.addHost( 'h13', cls=IPv6Host, v6Addr='4000::3/64' )
        host14 = self.addHost( 'h14', cls=IPv6Host, v6Addr='11:1:0::3/64' )
        host15 = self.addHost( 'h15', cls=IPv6Host, v6Addr='12:1:0::3/64' )
        host16 = self.addHost( 'h16', cls=IPv6Host, v6Addr='10:1:0::7/64' )

        # Switch S7 Hosts
        host17 = self.addHost( 'h17', cls=IPv6Host, v6Addr='10:1:0::8/64' )
        host18 = self.addHost( 'h18', cls=IPv6Host, v6Addr='1000::4/64' )
        host19 = self.addHost( 'h19', cls=IPv6Host, v6Addr='10:1:0::9/64' )
        host20 = self.addHost( 'h20', cls=IPv6Host, v6Addr='100:1:0::4/64' )
        host21 = self.addHost( 'h21', cls=IPv6Host, v6Addr='200:1:0::4/64' )
        host22 = self.addHost( 'h22', cls=IPv6Host, v6Addr='11:1:0::4/64' )
        host23 = self.addHost( 'h23', cls=IPv6Host, v6Addr='12:1:0::4/64' )
        # VLAN
        host24 = self.addHost( 'h24', cls=VLANHost, v6Addr='4000::5/64' )

        s1 = self.addSwitch( 's1' )
        s2 = self.addSwitch( 's2' )
        s3 = self.addSwitch( 's3' )
        s4 = self.addSwitch( 's4' )
        s5 = self.addSwitch( 's5' )
        s6 = self.addSwitch( 's6' )
        s7 = self.addSwitch( 's7' )

        self.addLink( s5, host1 )
        self.addLink( s5, host2 )
        self.addLink( s5, host3 )
        self.addLink( s5, host4 )
        self.addLink( s5, host5 )
        self.addLink( s5, host6 )
        self.addLink( s5, host7 )
        self.addLink( s5, host8 )

        self.addLink( s6, host9 )
        self.addLink( s6, host10 )
        self.addLink( s6, host11 )
        self.addLink( s6, host12 )
        self.addLink( s6, host13 )
        self.addLink( s6, host14 )
        self.addLink( s6, host15 )
        self.addLink( s6, host16 )

        self.addLink( s7, host17 )
        self.addLink( s7, host18 )
        self.addLink( s7, host19 )
        self.addLink( s7, host20 )
        self.addLink( s7, host21 )
        self.addLink( s7, host22 )
        self.addLink( s7, host23 )
        self.addLink( s7, host24 )

        self.addLink( s1, s2 )
        self.addLink( s1, s3 )
        self.addLink( s1, s4 )
        self.addLink( s1, s5 )
        self.addLink( s2, s3 )
        self.addLink( s2, s5 )
        self.addLink( s2, s6 )
        self.addLink( s3, s4 )
        self.addLink( s3, s6 )
        self.addLink( s4, s7 )
        topos = { 'mytopo': ( lambda: MyTopo() ) }

# HERE THE CODE DEFINITION OF THE TOPOLOGY ENDS


def setupNetwork():
    "Create network"
    topo = MyTopo()
    network = Mininet( topo=topo, autoSetMacs=True, controller=None )
    network.start()
    CLI( network )
    network.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    # setLogLevel( 'debug' )
    setupNetwork()
