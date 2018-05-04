#!/usr/bin/env python

import opscore.protocols.keys as keys
import opscore.protocols.types as types

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
            ('getVisit', '', self.getVisit),
        ]

        # Define typed command arguments for the above commands.
        self.keys = keys.KeysDictionary("seqno_seqno", (1, 1),
                                        keys.Key("text", types.String(), help=""),
                                        )

    def ping(self, cmd):
        """Query the actor for liveness/happiness."""

        cmd.finish("text='Present and (probably) well'")

    def status(self, cmd):
        """Report status and version; obtain and send current data"""

        cmd.inform('text="Present!"')
        cmd.finish()


    def getVisit(self, cmd):
        """ Query for a new PFS visit from Gen2.

        This is slightly tricky. OCS allocates 8-digit IDs for single
        image types, but we have four image types (PFS[ABCD]) and only
        want 6-digits of ID.

        So we

        """

        visit = self.actor.getPfsVisit()

        cmd.finish('visit=%d' % visit)