#!/usr/bin/env python

import opscore.protocols.keys as keys
import opscore.protocols.types as types
from ics.utils import opdb
from pfscore import SeqPath


class SeqnoCmd(object):
    def __init__(self, actor):
        # This lets us access the rest of the actor.
        self.actor = actor

        # Declare the commands we implement. When the actor is started
        # these are registered with the parser, which will call the
        # associated methods when matched. The callbacks will be
        # passed a single argument, the parsed and typed command.
        #
        self.vocab = [
            ('ping', '', self.ping),
            ('status', '', self.status),
            ('getVisit', '[<caller>] [<designId>]', self.getVisit),
            ('updateTelStatus', '[<caller>]', self.updateTelStatus),

        ]

        # Define typed command arguments for the above commands.
        self.keys = keys.KeysDictionary("core_core", (1, 1),
                                        keys.Key("text", types.String(), help=""),
                                        keys.Key("caller", types.String(),
                                                 help='who should be listed as requesting a visit.'),
                                        keys.Key("designId", types.Long(), help="PFS design ID"),
                                        )

    def ping(self, cmd):
        """Query the actor for liveness/happiness."""

        cmd.finish("text='Present and (probably) well'")

    def status(self, cmd):
        """Report status and version; obtain and send current data"""

        cmd.inform('text="Present!"')
        cmd.finish()

    def getDesignId(self, cmd):
        """Return the current designId for the instrument.

        For INSTRM-1102, hardwire to use the DCB key. Once INSTRM-1095
        is done, switch to the IIC key.

        """
        cmdKeys = cmd.cmd.keywords

        if 'designId' in cmdKeys:
            designId = cmdKeys['designId'].values[0]

        else:
            cmd.inform('text="getting designId from model"')

            dcbModel = self.actor.models['dcb'].keyVarDict
            iicModel = self.actor.models['iic'].keyVarDict

            if 'designId' in iicModel:
                designId = iicModel['designId'].getValue()

            elif 'designId' in dcbModel:
                designId = dcbModel['designId'].getValue()

            else:
                raise RuntimeError('well, let set it to invalid then...')

        designId = int(designId)  # The Long() opscore type yields 0x12345678 values.
        return designId

    def getVisit(self, cmd):
        """Query for a new PFS visit from Gen2.

        This is a critical command for any successful exposure. It really cannot be allowed to fail.

        If we cannot get a new frame id from Gen2 we fail over to a
        filesystem-based sequence. If that fails we blow up.

        We also survive opdb outages. The actors will have to be
        robust against missing pfs_visit table entries.

        """

        def getPfsVisit(config):
            """consume next seqno"""
            fileMgr = SeqPath.NightFilenameGen(config.get('gen2', 'rootDir'))
            return int(fileMgr.consumeNextSeqno())

        caller = str(cmd.cmd.keywords['caller'].values[0]) if 'caller' in cmd.cmd.keywords else None

        visit = getPfsVisit(self.actor.config)
        try:
            designId = self.getDesignId(cmd)
        except Exception as e:
            cmd.warn(f'text="failed to get designId: {e}"')
            designId = -9999

        cmd.debug(f'updating opdb.pfs_visit with visit={visit}, design_id={designId}, and description={caller}')
        try:
            opdb.opDB.insert('pfs_visit', pfs_visit_id=visit, pfs_visit_description=caller,
                             pfs_design_id=designId, issued_at='now')
        except Exception as e:
            cmd.warn('text="failed to insert into pfs_visit: %s"' % (e))

        cmd.finish('visit=%d' % (visit))

    def updateTelStatus(self, cmd):
        """Simulating gen2 status."""

        cmd.inform("inst_ids=NAOJ,Subaru,PFS")
        cmd.inform("program=#,SPEC_ENG,Standby,None")
        cmd.inform("object=YAMASHITA4,21:35:13.354,+19:43:55.600,21:35:13.354,+19:43:55.600")
        cmd.inform("pointing=19:14:00.000,-21:40:00.000")
        cmd.inform("offsets=0.0000,0.0000")
        cmd.inform("coordinate_system_ids=FK5,180.0,2000.0")
        cmd.inform("tel_axes=89.9965,89.9186,0.08140674000000558,1.000")
        cmd.inform("tel_rot=0.0,-0.000742")
        cmd.inform("tel_focus=P_OPT2,PRIME,3.52")
        cmd.inform("tel_adc=IN,0.0")
        cmd.inform("dome_env=23.000,622.400,277.950,0.000")
        cmd.inform("outside_env=21.200,622.400,278.250,4.500")
        cmd.inform("m2=Opt,-0.000237,0.001034,-0.000425")
        cmd.inform("m2rot=0.0028,-0.0018,-0.0020")
        cmd.inform("pfuOffset=-1.800,-2.600,3.520")
        cmd.inform('autoguider="OFF"')
        cmd.inform('conditions=Fine,0.000,1.000')
        cmd.inform("moon=-41.919,131.962,0.149")
        cmd.inform('obsMethod="Classical"')

        cmd.finish()