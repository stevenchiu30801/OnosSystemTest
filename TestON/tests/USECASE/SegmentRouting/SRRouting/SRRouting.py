
class SRRouting:
    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        Ping between all ipv4 hosts in the topology.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=1,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=1,
                               ipv6=0,
                               countFlowsGroups=False,
                               description="Ping between all ipv4 hosts in the topology")

    def CASE2( self, main ):
        """
        Ping between all ipv6 hosts in the topology.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=2,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=0,
                               ipv6=1,
                               countFlowsGroups=False,
                               description="Ping between all ipv6 hosts in the topology")

    def CASE3( self, main ):
        """
        Ping between all ipv4 and ipv6 hosts in the topology.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=3,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=1,
                               ipv6=1,
                               countFlowsGroups=False,
                               description="Ping between all ipv4 and ipv6 hosts in the topology")