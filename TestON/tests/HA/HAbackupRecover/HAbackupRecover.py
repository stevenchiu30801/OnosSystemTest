"""
Copyright 2018 Open Networking Foundation ( ONF )

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
Description: This test is to determine if ONOS can handle
    all of it's nodes restarting

List of test cases:
CASE1: Compile ONOS and push it to the test machines
CASE2: Assign devices to controllers
CASE21: Assign mastership to controllers
CASE3: Assign intents
CASE4: Ping across added host intents
CASE5: Reading state of ONOS
CASE6: The Failure case.
CASE7: Check state after control plane failure
CASE8: Compare topo
CASE9: Link s3-s28 down
CASE10: Link s3-s28 up
CASE11: Switch down
CASE12: Switch up
CASE13: Clean up
CASE14: start election app on all onos nodes
CASE15: Check that Leadership Election is still functional
CASE16: Install Distributed Primitives app
CASE17: Check for basic functionality with distributed primitives
"""
class HAbackupRecover:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        CASE1 is to compile ONOS and push it to the test machines

        Startup sequence:
        cell <name>
        onos-verify-cell
        NOTE: temporary - onos-remove-raft-logs
        onos-uninstall
        start mininet
        git pull
        mvn clean install
        onos-package
        onos-install -f
        onos-wait-for-start
        start cli sessions
        start tcpdump
        """
        main.log.info( "ONOS HA test: Restart all ONOS nodes - " +
                         "initialization" )
        # These are for csv plotting in jenkins
        main.HAlabels = []
        main.HAdata = []
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.cleanAndExit()
        main.testSetUp.envSetupDescription()
        try:
            from tests.HA.dependencies.HA import HA
            main.HA = HA()
            # load some variables from the params file
            cellName = main.params[ 'ENV' ][ 'cellName' ]
            main.apps = main.params[ 'ENV' ][ 'appString' ]
            stepResult = main.testSetUp.envSetup( includeCaseDesc=False )
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )

        try:
            if main.params[ 'topology' ][ 'topoFile' ]:
                main.log.info( 'Skipping start of Mininet in this case, make sure you start it elsewhere' )
                applyFuncs = None
            else:
                applyFuncs = main.HA.startingMininet
        except (KeyError, IndexError):
            applyFuncs = main.HA.startingMininet

        main.testSetUp.ONOSSetUp( main.Cluster, cellName=cellName, removeLog=True,
                                  extraApply=applyFuncs )

        main.HA.initialSetUp()

        main.step( 'Set logging levels' )
        logging = True
        try:
            logs = main.params.get( 'ONOS_Logging', False )
            if logs:
                for namespace, level in logs.items():
                    for ctrl in main.Cluster.active():
                        ctrl.CLI.logSet( level, namespace )
        except AttributeError:
            logging = False
        utilities.assert_equals( expect=True, actual=logging,
                                 onpass="Set log levels",
                                 onfail="Failed to set log levels" )

    def CASE2( self, main ):
        """
        Assign devices to controllers
        """
        main.HA.assignDevices( main )

    def CASE102( self, main ):
        """
        Set up Spine-Leaf fabric topology in Mininet
        """
        main.HA.startTopology( main )

    def CASE21( self, main ):
        """
        Assign mastership to controllers
        """
        main.HA.assignMastership( main )

    def CASE3( self, main ):
        """
        Assign intents
        """
        main.HA.assignIntents( main )

    def CASE4( self, main ):
        """
        Ping across added host intents
        """
        main.HA.pingAcrossHostIntent( main )

    def CASE104( self, main ):
        """
        Ping Hosts
        """
        main.case( "Check connectivity" )
        main.step( "Ping between all hosts" )
        pingResult = main.Mininet1.pingall()
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="All Pings Passed",
                                 onfail="Failed to ping between all hosts" )

    def CASE5( self, main ):
        """
        Reading state of ONOS
        """
        main.HA.readingState( main )

    def CASE6( self, main ):
        """
        The Failure case.
        """
        import time
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"
        try:
            main.HAlabels
        except ( NameError, AttributeError ):
            main.log.error( "main.HAlabels not defined, setting to []" )
            main.HAlabels = []
        try:
            main.HAdata
        except ( NameError, AttributeError ):
            main.log.error( "main.HAdata not defined, setting to []" )
            main.HAdata = []

        main.case( "Restart entire ONOS cluster with backed up state" )

        main.step( "Backup ONOS data" )
        location = "/tmp/" + main.TEST + ".tar.gz"
        backupResult = main.HA.backupData( main, location )
        utilities.assert_equals( expect=True, actual=backupResult,
                                 onpass="ONOS backup succeded",
                                 onfail="ONOS backup failed" )

        main.step( "Checking ONOS Logs for errors" )
        for ctrl in main.Cluster.active():
            main.log.debug( "Checking logs for errors on " + ctrl.name + ":" )
            main.log.warn( main.ONOSbench.checkLogs( ctrl.ipAddress ) )

        killTime = time.time()
        main.testSetUp.uninstallOnos( main.Cluster, uninstallMax=True )

        clusterSize = len( main.Cluster.active() )
        main.Cluster.setRunningNode( 0 )  # So we can install without starting ONOS
        main.testSetUp.installOnos( main.Cluster, installMax=True )
        main.Cluster.setRunningNode( clusterSize )

        main.step( "Restore ONOS data" )
        restoreResult = main.HA.restoreData( main, location )
        utilities.assert_equals( expect=True, actual=restoreResult,
                                 onpass="ONOS restore succeded",
                                 onfail="ONOS restore failed" )

        main.step( "Restart ONOS nodes" )
        started = main.Cluster.command( "onosStart",
                                        args=[ "ipAddress" ],
                                        getFrom=0,
                                        funcFromCtrl=True )
        for ctrl in main.Cluster.controllers:
            ctrl.active = True
            main.log.debug( repr( ctrl ) )

        main.testSetUp.setupSsh( main.Cluster )
        main.testSetUp.checkOnosService( main.Cluster )
        main.testSetUp.startOnosClis( main.Cluster )

        ready = utilities.retry( main.Cluster.command,
                                 False,
                                 kwargs={ "function": "summary", "contentCheck": True },
                                 sleep=30,
                                 attempts=10 )
        utilities.assert_equals( expect=True, actual=ready,
                                 onpass="ONOS summary command succeded",
                                 onfail="ONOS summary command failed" )
        if not ready:
            main.cleanAndExit()

        # Grab the time of restart so we chan check how long the gossip
        # protocol has had time to work
        main.restartTime = time.time() - killTime
        main.log.debug( "Restart time: " + str( main.restartTime ) )
        main.HAlabels.append( "Restart" )
        main.HAdata.append( str( main.restartTime ) )

        # Rerun for election on restarted nodes
        runResults = main.Cluster.command( "electionTestRun", returnBool=True )
        utilities.assert_equals( expect=True, actual=runResults,
                                 onpass="Reran for election",
                                 onfail="Failed to rerun for election" )

        main.HA.commonChecks()
        time.sleep(60)

    def CASE7( self, main ):
        """
        Check state after ONOS failure
        """
        # NOTE: Store has no durability, so intents are lost across system
        #       restarts
        main.HA.checkStateAfterEvent( main, afterWhich=0, isRestart=True )

        main.step( "Leadership Election is still functional" )
        # Test of LeadershipElection
        leaderList = []
        leaderResult = main.TRUE

        for ctrl in main.Cluster.active():
            leaderN = ctrl.CLI.electionTestLeader()
            leaderList.append( leaderN )
            if leaderN == main.FALSE:
                # error in response
                main.log.error( "Something is wrong with " +
                                 "electionTestLeader function, check the" +
                                 " error logs" )
                leaderResult = main.FALSE
            elif leaderN is None:
                main.log.error( ctrl.name +
                                 " shows no leader for the election-app." )
                leaderResult = main.FALSE
        if len( set( leaderList ) ) != 1:
            leaderResult = main.FALSE
            main.log.error(
                "Inconsistent view of leader for the election test app" )
            main.log.debug( leaderList )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=leaderResult,
            onpass="Leadership election passed",
            onfail="Something went wrong with Leadership election" )

    def CASE8( self, main ):
        """
        Compare topo
        """
        main.HA.compareTopo( main )

    def CASE9( self, main ):
        """
        Link down
        """
        src = main.params['kill']['linkSrc']
        dst = main.params['kill']['linkDst']
        main.HA.linkDown( main, src, dst )

    def CASE10( self, main ):
        """
        Link up
        """
        src = main.params['kill']['linkSrc']
        dst = main.params['kill']['linkDst']
        main.HA.linkUp( main, src, dst )

    def CASE11( self, main ):
        """
        Switch Down
        """
        # NOTE: You should probably run a topology check after this
        main.HA.switchDown( main )

    def CASE12( self, main ):
        """
        Switch Up
        """
        # NOTE: You should probably run a topology check after this
        main.HA.switchUp( main )

    def CASE13( self, main ):
        """
        Clean up
        """
        main.HA.cleanUp( main )

    def CASE14( self, main ):
        """
        Start election app on all onos nodes
        """
        try:
            main.HA.startElectionApp( main )
        except Exception as e:
            main.log.error( e )

    def CASE15( self, main ):
        """
        Check that Leadership Election is still functional
            15.1 Run election on each node
            15.2 Check that each node has the same leaders and candidates
            15.3 Find current leader and withdraw
            15.4 Check that a new node was elected leader
            15.5 Check that that new leader was the candidate of old leader
            15.6 Run for election on old leader
            15.7 Check that oldLeader is a candidate, and leader if only 1 node
            15.8 Make sure that the old leader was added to the candidate list

            old and new variable prefixes refer to data from before vs after
                withdrawl and later before withdrawl vs after re-election
        """
        main.HA.isElectionFunctional( main )

    def CASE16( self, main ):
        """
        Install Distributed Primitives app
        """
        main.HA.installDistributedPrimitiveApp( main )

    def CASE17( self, main ):
        """
        Check for basic functionality with distributed primitives
        """
        main.HA.checkDistPrimitivesFunc( main )
