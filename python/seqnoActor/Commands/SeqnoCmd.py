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
