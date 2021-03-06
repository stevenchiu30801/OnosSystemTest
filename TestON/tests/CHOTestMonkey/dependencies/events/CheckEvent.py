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
This file contains classes for CHOTestMonkey that are related to check event
Author: you@onlab.us
"""
from tests.CHOTestMonkey.dependencies.events.Event import EventType, EventStates, Event


class CheckEvent( Event ):

    def __init__( self ):
        Event.__init__( self )

    def startCheckEvent( self ):
        return EventStates().PASS

    def startEvent( self, args ):
        with self.eventLock:
            main.log.info( "Event recorded: {} {}".format( self.typeIndex, self.typeString ) )
            result = self.startCheckEvent()
            return result


class IntentCheck( CheckEvent ):

    def __init__( self ):
        CheckEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startCheckEvent( self, args=None ):
        checkResult = EventStates().PASS
        intentDict = {}
        for intent in main.intents:
            intentDict[ intent.id ] = intent.expectedState
        for controller in main.controllers:
            if controller.isUp():
                with controller.CLILock:
                    intentState = controller.CLI.compareIntent( intentDict )
                if not intentState:
                    main.log.warn( "Intent Check - not all intent ids and states match that on ONOS%s" % ( controller.index ) )
                    # FIXME: ONOS leaves intents as WITHDRAWN state occasionally and we don't consider that as a FAIL for now
                    # checkResult = EventStates().FAIL
        return checkResult


class FlowCheck( CheckEvent ):

    def __init__( self ):
        CheckEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startCheckEvent( self, args=None ):
        import json
        checkResult = EventStates().PASS
        if main.enableIPv6:
            coreFlowNum = int( main.params[ 'EVENT' ][ 'FlowCheck' ][ 'coreFlowNum6' ] )
        else:
            coreFlowNum = int( main.params[ 'EVENT' ][ 'FlowCheck' ][ 'coreFlowNum' ] )
        for controller in main.controllers:
            if controller.isUp():
                with controller.CLILock:
                    # Check core flow number
                    for device in main.devices:
                        if device.isRemoved():
                            continue
                        coreFlowNumOnos = controller.CLI.flowAddedCount( device.dpid, core=True )
                        if coreFlowNumOnos is None:
                            main.log.warn( "Flow Check - error when trying to get flow number of %s on ONOS%s" % ( device.dpid, controller.index ) )
                            checkResult = EventStates().FAIL
                        else:
                            coreFlowNumOnos = int( coreFlowNumOnos )
                            if coreFlowNumOnos != coreFlowNum:
                                main.log.warn( "Flow Check - core flow number of %s on ONOS%s is %s" % ( device.dpid, controller.index, coreFlowNumOnos ) )
                                checkResult = EventStates().FAIL
                    # Get flows for comparison
                    flows = controller.CLI.flows()
                    try:
                        flows = json.loads( flows )
                    except ( TypeError, ValueError ):
                        main.log.exception( "Flow Check - Object not as expected: {!r}".format( flows ) )
                        return EventStates().FAIL
                    # Compare flow IDs in ONOS and Mininet
                    flowIDList = []
                    for item in flows:
                        for flow in item[ "flows" ]:
                            flowIDList.append( hex( int( flow[ 'id' ] ) ) )
                    main.log.info( "Flow Check - current flow number on ONOS%s: %s" % ( controller.index, len( flowIDList ) ) )
                    switchList = []
                    for device in main.devices:
                        switchList.append( device.name )
                    with main.mininetLock:
                        flowCompareResult = main.Mininet1.checkFlowId( switchList, flowIDList, debug=False )
                    if not flowCompareResult:
                        main.log.warn( "Flow Check - flows on ONOS%s do not match that in Mininet" % ( controller.index ) )
                        checkResult = EventStates().FAIL
                    # Check flow state
                    flowState = controller.CLI.checkFlowsState( isPENDING=False )
                    if not flowState:
                        main.log.warn( "Flow Check - not all flows are in ADDED state on ONOS%s" % ( controller.index ) )
                        checkResult = EventStates().FAIL
        return checkResult


class TopoCheck( CheckEvent ):

    def __init__( self ):
        CheckEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startCheckEvent( self, args=None ):
        import json
        checkResult = EventStates().PASS
        upLinkNum = 0
        upDeviceNum = 0
        upHostNum = 0
        with main.variableLock:
            for link in main.links:
                if not link.isDown() and not link.isRemoved():
                    upLinkNum += 1
            for device in main.devices:
                if not device.isDown() and not device.isRemoved():
                    upDeviceNum += 1
            for host in main.hosts:
                if not host.isDown() and not host.isRemoved():
                    upHostNum += 1
        clusterNum = 1
        with main.mininetLock:
            graphDictMininet = main.Mininet1.getGraphDict( useId=True )
        for controller in main.controllers:
            if controller.isUp():
                with controller.CLILock:
                    topoState = controller.CLI.checkStatus( upDeviceNum, upLinkNum )
                    # if not topoState:
                    #    main.log.warn( "Topo Check - link or device number discoverd by ONOS%s is incorrect" % ( controller.index ) )
                    #    checkResult = EventStates().FAIL
                    # Compare ONOS and Mininet topologies
                    graphDictONOS = controller.CLI.getGraphDict()
                    compareResult = main.graph.compareGraphs( graphDictONOS, graphDictMininet )
                    if not compareResult:
                        checkResult = EventStates().FAIL
                        main.log.warn( "Topo Check - ONOS and Mininet topologies do not match" )
                    try:
                        # Check links
                        links = controller.CLI.links()
                        links = json.loads( links )
                        if not len( links ) == upLinkNum:
                            checkResult = EventStates().FAIL
                            main.log.warn( "Topo Check - link number discoverd by ONOS%s is incorrect: %s expected and %s actual" % ( controller.index, upLinkNum, len( links ) ) )
                        # Check devices
                        devices = controller.CLI.devices()
                        devices = json.loads( devices )
                        availableDeviceNum = 0
                        for device in devices:
                            if device[ 'available' ]:
                                availableDeviceNum += 1
                        if not availableDeviceNum == upDeviceNum:
                            checkResult = EventStates().FAIL
                            main.log.warn( "Topo Check - device number discoverd by ONOS%s is incorrect: %s expected and %s actual" % ( controller.index, upDeviceNum, availableDeviceNum ) )
                        # Check hosts
                        hosts = controller.CLI.hosts()
                        hosts = json.loads( hosts )
                        if not len( hosts ) == upHostNum:
                            checkResult = EventStates().FAIL
                            main.log.warn( "Topo Check - host number discoverd by ONOS%s is incorrect: %s expected and %s actual" % ( controller.index, upHostNum, len( hosts ) ) )
                        # Check clusters
                        clusters = controller.CLI.clusters()
                        clusters = json.loads( clusters )
                        if not len( clusters ) == clusterNum:
                            checkResult = EventStates().FAIL
                            main.log.warn( "Topo Check - cluster number discoverd by ONOS%s is incorrect: %s expected and %s actual" % ( controller.index, clusterNum, len( clusters ) ) )
                    except ( TypeError, ValueError ):
                        main.log.exception( "Flow Check - Object not as expected" )
                        return EventStates().FAIL
        return checkResult


class ONOSCheck( CheckEvent ):

    def __init__( self ):
        CheckEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startCheckEvent( self, args=None ):
        import json
        checkResult = EventStates().PASS
        topics = []
        # TODO: Other topics?
        for i in range( 14 ):
            topics.append( "work-partition-" + str( i ) )
        dpidToAvailability = {}
        dpidToMaster = {}
        for device in main.devices:
            if device.isDown() or device.isRemoved():
                dpidToAvailability[ device.dpid ] = False
            else:
                dpidToAvailability[ device.dpid ] = True
            dpidToMaster[ device.dpid ] = 'unknown'
        # Check mastership, leaders and node states on each controller node
        for controller in main.controllers:
            if controller.isUp():
                # Check mastership
                try:
                    with controller.CLILock:
                        roles = controller.CLI.roles()
                    roles = json.loads( roles )
                    for device in roles:
                        dpid = device[ 'id' ]
                        if dpidToMaster[ dpid ] == 'unknown':
                            dpidToMaster[ dpid ] = device[ 'master' ]
                        elif dpidToMaster[ dpid ] != device[ 'master' ]:
                            checkResult = EventStates().FAIL
                            main.log.warn( "ONOS Check - Mastership of %s on ONOS%s is inconsistent with that on ONOS1" % ( dpid, controller.index ) )
                        if dpidToAvailability[ dpid ] and device[ 'master' ] == "none":
                            checkResult = EventStates().FAIL
                            main.log.warn( "ONOS Check - Device %s has no master on ONOS%s" % ( dpid, controller.index ) )
                    # Check leaders
                    with controller.CLILock:
                        leaders = controller.CLI.leaders()
                    leaders = json.loads( leaders )
                    ONOSTopics = [ j[ 'topic' ] for j in leaders ]
                    for topic in topics:
                        if topic not in ONOSTopics:
                            checkResult = EventStates().FAIL
                            main.log.warn( "ONOS Check - Topic %s not in leaders on ONOS%s" % ( topic, controller.index ) )
                    # Check node state
                    with controller.CLILock:
                        nodes = controller.CLI.nodes()
                    nodes = json.loads( nodes )
                    ipToState = {}
                    for node in nodes:
                        ipToState[ node[ 'ip' ] ] = node[ 'state' ]
                    for c in main.controllers:
                        if c.isUp() and ipToState[ c.ip ] == 'READY':
                            pass
                        elif not c.isUp() and c.ip not in ipToState.keys():
                            pass
                        else:
                            checkResult = EventStates().FAIL
                            main.log.warn( "ONOS Check - ONOS%s shows wrong node state: ONOS%s is %s but state is %s" % ( controller.index, c.index, c.status, ipToState[ c.ip ] ) )
                    # TODO: check partitions?
                except ( TypeError, ValueError ):
                    main.log.exception( "ONOS Check - Object not as expected" )
                    return EventStates().FAIL
                except Exception as e:
                    main.log.exception( "ONOS Check - Uncaught Exception: {}".format( e ) )
                    return EventStates().FAIL
        return checkResult


class TrafficCheck( CheckEvent ):

    def __init__( self ):
        CheckEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startCheckEvent( self, args=None ):
        checkResult = EventStates().PASS
        pool = []
        wait = int( main.params[ 'EVENT' ][ 'TrafficCheck' ][ 'pingWait' ] )
        timeout = int( main.params[ 'EVENT' ][ 'TrafficCheck' ][ 'pingTimeout' ] )
        dstIPv4List = {}
        dstIPv6List = {}
        upHosts = []
        for host in main.hosts:
            if host.isUp():
                upHosts.append( host )
        for host in upHosts:
            dstIPv4List[ host.index ] = []
            dstIPv6List[ host.index ] = []
            for correspondent in host.correspondents:
                if correspondent not in upHosts:
                    continue
                for ipAddress in correspondent.ipAddresses:
                    if ipAddress.startswith( str( main.params[ 'TEST' ][ 'ipv6Prefix' ] ) ):
                        dstIPv6List[ host.index ].append( ipAddress )
                    elif ipAddress.startswith( str( main.params[ 'TEST' ][ 'ipv4Prefix' ] ) ):
                        dstIPv4List[ host.index ].append( ipAddress )
            thread = main.Thread( target=host.handle.pingHostSetAlternative,
                                  threadID=main.threadID,
                                  name="pingHostSetAlternative",
                                  args=[ dstIPv4List[ host.index ], 1 ] )
            pool.append( thread )
            thread.start()
            with main.variableLock:
                main.threadID += 1
        for thread in pool:
            thread.join( 10 )
            if not thread.result:
                checkResult = EventStates().FAIL
                main.log.warn( "Traffic Check - ping failed" )

        if not main.enableIPv6:
            return checkResult
        # Check ipv6 ping
        for host in upHosts:
            thread = main.Thread( target=host.handle.pingHostSetAlternative,
                                  threadID=main.threadID,
                                  name="pingHostSetAlternative",
                                  args=[ dstIPv6List[ host.index ], 1, True ] )
            pool.append( thread )
            thread.start()
            with main.variableLock:
                main.threadID += 1
        for thread in pool:
            thread.join( 10 )
            if not thread.result:
                checkResult = EventStates().FAIL
                main.log.warn( "Traffic Check - ping6 failed" )
        return checkResult

class RaftLogSizeCheck( CheckEvent ):

    def __init__( self ):
        CheckEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startCheckEvent( self, args=None ):
        checkResult = EventStates().PASS
        main.log.info( "Starting checking Raft Log size" )
        if not main.Cluster.checkPartitionSize():
            checkResult = EventStates().FAIL
            main.log.warn( "Raft Log Size Check - Raft log grew too big" )

        return checkResult
