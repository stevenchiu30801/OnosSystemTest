"""
Copyright 2016 Open Networking Foundation ( ONF )

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
This file contains classes for CHOTestMonkey that are related to network event
Author: you@onlab.us
"""
from tests.CHOTestMonkey.dependencies.events.Event import EventType, EventStates, Event
from tests.CHOTestMonkey.dependencies.elements.NetworkElement import NetworkElement, Device, Host, Link


class LinkEvent( Event ):

    def __init__( self ):
        Event.__init__( self )
        self.linkA = None
        self.linkB = None

    def startLinkEvent( self ):
        return EventStates().PASS

    def startEvent( self, args ):
        """
        args are the names of the two link ends, e.g. [ 's1', 's2' ]
        """
        with self.eventLock:
            # main.log.info( "%s - starting event" % ( self.typeString ) )
            if len( args ) < 2:
                main.log.warn( "%s - Not enough arguments: %s" % ( self.typeString, args ) )
                return EventStates().ABORT
            elif len( args ) > 2:
                main.log.warn( "%s - Too many arguments: %s" % ( self.typeString, args ) )
                return EventStates().ABORT
            if args[ 0 ] == 'random' or args[ 1 ] == 'random':
                if self.typeIndex == EventType().NETWORK_LINK_DOWN:
                    with main.mininetLock:
                        linkRandom = main.Mininet1.getLinkRandom()
                    if linkRandom is None:
                        main.log.warn( "No link available, aborting event" )
                        return EventStates().ABORT
                    args[ 0 ] = linkRandom[ 0 ]
                    args[ 1 ] = linkRandom[ 1 ]
                elif self.typeIndex == EventType().NETWORK_LINK_UP:
                    import random
                    with main.variableLock:
                        downLinks = []
                        for link in main.links:
                            if link.isDown():
                                downLinks.append( link )
                        if len( downLinks ) == 0:
                            main.log.warn( "None of the links are in 'down' state, aborting event" )
                            return EventStates().ABORT
                        linkList = random.sample( downLinks, 1 )
                        self.linkA = linkList[ 0 ]
                        self.linkB = linkList[ 0 ].backwardLink
            elif args[ 0 ] == args[ 1 ]:
                main.log.warn( "%s - invalid arguments: %s" % ( self.typeString, args ) )
                return EventStates().ABORT
            if self.linkA is None or self.linkB is None:
                for link in main.links:
                    if link.deviceA.name == args[ 0 ] and link.deviceB.name == args[ 1 ]:
                        self.linkA = link
                    elif link.deviceA.name == args[ 1 ] and link.deviceB.name == args[ 0 ]:
                        self.linkB = link
                    if self.linkA is not None and self.linkB is not None:
                        break
                if self.linkA is None or self.linkB is None:
                    main.log.warn( "Bidirectional link %s - %s does not exist: " % ( args[ 0 ], args[ 1 ] ) )
                    return EventStates().ABORT
            main.log.debug( "%s - %s" % ( self.typeString, self.linkA ) )
            return self.startLinkEvent()


class LinkDown( LinkEvent ):

    """
    Generate a link down event giving the two ends of the link
    """
    def __init__( self ):
        LinkEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startLinkEvent( self ):
        # TODO: do we need to handle a unidirectional link?
        assert self.linkA is not None and self.linkB is not None
        with main.variableLock:
            if self.linkA.isDown() or self.linkB.isDown():
                main.log.warn( "Link Down - link already down" )
                return EventStates().ABORT
            elif self.linkA.isRemoved() or self.linkB.isRemoved():
                main.log.warn( "Link Down - link has been removed" )
                return EventStates().ABORT
        main.log.info( "Event recorded: {} {} {} {}".format( self.typeIndex, self.typeString, self.linkA.deviceA.name, self.linkA.deviceB.name ) )
        with main.mininetLock:
            """
            result = main.Mininet1.link( END1=self.linkA.deviceA.name,
                                         END2=self.linkA.deviceB.name,
                                         OPTION="down" )
            """
            result = main.Mininet1.delLink( self.linkA.deviceA.name,
                                            self.linkA.deviceB.name )
        if not result:
            main.log.warn( "%s - failed to bring down link" % ( self.typeString ) )
            return EventStates().FAIL
        with main.variableLock:
            self.linkA.bringDown()
            self.linkB.bringDown()
        return EventStates().PASS


class LinkUp( LinkEvent ):

    """
    Generate a link up event giving the two ends of the link
    """
    def __init__( self ):
        LinkEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startLinkEvent( self ):
        assert self.linkA is not None and self.linkB is not None
        with main.variableLock:
            if self.linkA.isUp() or self.linkB.isUp():
                main.log.warn( "Link Up - link already up" )
                return EventStates().ABORT
            if self.linkA.isRemoved() or self.linkB.isRemoved():
                main.log.warn( "Link Up - link has been removed" )
                return EventStates().ABORT
        main.log.info( "Event recorded: {} {} {} {}".format( self.typeIndex, self.typeString, self.linkA.deviceA.name, self.linkA.deviceB.name ) )
        with main.mininetLock:
            """
            result = main.Mininet1.link( END1=self.linkA.deviceA.name,
                                         END2=self.linkA.deviceB.name,
                                         OPTION="up" )
            """
            result = main.Mininet1.addLink( self.linkA.deviceA.name,
                                            self.linkA.deviceB.name )
        if not result:
            main.log.warn( "%s - failed to bring up link" % ( self.typeString ) )
            return EventStates().FAIL
        with main.variableLock:
            self.linkA.bringUp()
            self.linkB.bringUp()
        return EventStates().PASS


class DeviceEvent( Event ):

    def __init__( self ):
        Event.__init__( self )
        self.device = None

    def startDeviceEvent( self ):
        return EventStates().PASS

    def startEvent( self, args ):
        """
        args are the names of the device, e.g. 's1'
        """
        with self.eventLock:
            # main.log.info( "%s - starting event" % ( self.typeString ) )
            if len( args ) < 1:
                main.log.warn( "%s - Not enough arguments: %s" % ( self.typeString, args ) )
                return EventStates().ABORT
            elif len( args ) > 1:
                main.log.warn( "%s - Too many arguments: %s" % ( self.typeString, args ) )
                return EventStates().ABORT
            if args[ 0 ] == 'random':
                import random
                if self.typeIndex == EventType().NETWORK_DEVICE_DOWN:
                    with main.mininetLock:
                        switchRandom = main.Mininet1.getSwitchRandom()
                    if switchRandom is None:
                        main.log.warn( "No switch available, aborting event" )
                        return EventStates().ABORT
                    args[ 0 ] = switchRandom
                elif self.typeIndex == EventType().NETWORK_DEVICE_UP:
                    with main.variableLock:
                        removedDevices = []
                        for device in main.devices:
                            if device.isRemoved():
                                removedDevices.append( device )
                        if len( removedDevices ) == 0:
                            main.log.warn( "None of the devices are removed, aborting event" )
                            return EventStates().ABORT
                        deviceList = random.sample( removedDevices, 1 )
                        self.device = deviceList[ 0 ]
            if self.device is None:
                for device in main.devices:
                    if device.name == args[ 0 ]:
                        self.device = device
                if self.device is None:
                    main.log.warn( "Device %s does not exist: " % ( args[ 0 ] ) )
                    return EventStates().ABORT
            main.log.debug( "%s - %s" % ( self.typeString, self.device ) )
            return self.startDeviceEvent()


class DeviceDown( DeviceEvent ):

    """
    Generate a device down event ( which actually removes this device for now ) giving its name
    """
    def __init__( self ):
        DeviceEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startDeviceEvent( self ):
        assert self.device is not None
        with main.variableLock:
            if self.device.isRemoved():
                main.log.warn( "Device Down - device has been removed" )
                return EventStates().ABORT
        main.log.info( "Event recorded: {} {} {}".format( self.typeIndex, self.typeString, self.device.name ) )
        with main.mininetLock:
            result = main.Mininet1.delSwitch( self.device.name )
        if not result:
            main.log.warn( "%s - failed to bring down device" % ( self.typeString ) )
            return EventStates().FAIL
        with main.variableLock:
            self.device.setRemoved()
            for link in self.device.outgoingLinks:
                link.setRemoved()
                link.backwardLink.setRemoved()
            for host in self.device.hosts:
                host.setRemoved()
            for intent in main.intents:
                if intent.deviceA == self.device or intent.deviceB == self.device:
                    intent.setFailed()
        return EventStates().PASS


class DeviceUp( DeviceEvent ):

    """
    Generate a device up event ( which re-adds this device in case the device is removed ) giving its name
    """
    def __init__( self ):
        DeviceEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startDeviceEvent( self ):
        assert self.device is not None
        with main.variableLock:
            if self.device.isUp():
                main.log.warn( "Device Up - device already up" )
                return EventStates().ABORT
        # Re-add the device
        main.log.info( "Event recorded: {} {} {}".format( self.typeIndex, self.typeString, self.device.name ) )
        with main.mininetLock:
            result = main.Mininet1.addSwitch( self.device.name, dpid=self.device.dpid[ 3: ] )
        if not result:
            main.log.warn( "%s - failed to re-add device" % ( self.typeString ) )
            return EventStates().FAIL
        with main.variableLock:
            self.device.bringUp()
        # Re-add links
        # We add host-device links first since we did the same in mininet topology file
        # TODO: a more rubust way is to add links according to the port info of the device
        for host in self.device.hosts:
            # Add host-device link
            with main.mininetLock:
                result = main.Mininet1.addLink( self.device.name, host.name )
            if not result:
                main.log.warn( "%s - failed to re-connect host %s to device" % ( self.typeString, host.name ) )
                return EventStates().FAIL
        for link in self.device.outgoingLinks:
            neighbor = link.deviceB
            # Skip bringing up any link that connecting this device to a removed neighbor
            if neighbor.isRemoved():
                continue
            with main.mininetLock:
                result = main.Mininet1.addLink( self.device.name, neighbor.name )
            if not result:
                main.log.warn( "%s - failed to re-add link to %s" % ( self.typeString, neighbor.name ) )
                return EventStates().FAIL
            with main.variableLock:
                link.bringUp()
                link.backwardLink.bringUp()
                for intent in main.intents:
                    if intent.isFailed():
                        if intent.deviceA == self.device and intent.deviceB.isUp() or\
                                intent.deviceB == self.device and intent.deviceA.isUp():
                            intent.setInstalled()
        # Re-assign mastership for the device
        with main.mininetLock:
            ips = main.Cluster.getIps()
            main.Mininet1.assignSwController( sw=self.device.name, ip=ips )
        # Re-discover hosts
        for host in self.device.hosts:
            correspondent = None
            for h in main.hosts:
                if h.isUp() and h != host:
                    correspondent = h
                    break
            if correspondent is None:
                with main.mininetLock:
                    main.Mininet1.pingall()
                    if main.enableIPv6:
                        main.Mininet1.pingall( protocol="IPv6" )
            else:
                ipv4Addr = None
                ipv6Addr = None
                for ipAddress in correspondent.ipAddresses:
                    if ipAddress.startswith( str( main.params[ 'TEST' ][ 'ipv6Prefix' ] ) ) and ipv6Addr is None:
                        ipv6Addr = ipAddress
                    elif ipAddress.startswith( str( main.params[ 'TEST' ][ 'ipv4Prefix' ] ) ) and ipv4Addr is None:
                        ipv4Addr = ipAddress
                assert ipv4Addr is not None
                host.handle.pingHostSetAlternative( [ ipv4Addr ], 1 )
                if main.enableIPv6:
                    assert ipv6Addr is not None
                    host.handle.pingHostSetAlternative( [ ipv6Addr ], 1, True )
            with main.variableLock:
                host.bringUp()
        return EventStates().PASS
