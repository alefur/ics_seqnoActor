#!/usr/bin/env python
import logging
from actorcore.Actor import Actor

from fpga import SeqPath

class OurActor(Actor):
    def __init__(self, name, productName=None, configFile=None, logLevel=logging.INFO):
        # This sets up the connections to/from the hub, the logger, and the twisted reactor.
        #

        Actor.__init__(self, name,
                       productName=productName,
                       configFile=configFile)

        rootDir = self.config.get(self.name, 'rootDir')
        self.fileMgr = SeqPath.NightFilenameGen(rootDir)


    def getPfsVisit(self):
        seqno = self.fileMgr.consumeNextSeqno()
        return seqno

def main():

    theActor = OurActor('seqno', productName='seqnoActor')
    theActor.run()


if __name__ == '__main__':
    main()
