#!/usr/bin/env python
import logging

from actorcore.Actor import Actor
from pfs.utils.opdb import opDB
from pfscore import SeqPath


class OurActor(Actor):
    def __init__(self, name, productName=None, configFile=None, logLevel=logging.INFO):
        # This sets up the connections to/from the hub, the logger, and the twisted reactor.
        #

        Actor.__init__(self, name,
                       productName=productName,
                       configFile=configFile)

    def getPfsVisit(self, description=''):
        fileMgr = SeqPath.NightFilenameGen(self.config.get(self.name, 'rootDir'))
        visit = int(fileMgr.consumeNextSeqno())
        opDB.insert('pfs_visit', pfs_visit_id=visit, pfs_visit_description=description)
        return visit


def main():
    theActor = OurActor('gen2', productName='seqnoActor')
    theActor.run()


if __name__ == '__main__':
    main()
