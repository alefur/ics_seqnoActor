#!/usr/bin/env python
import logging

from actorcore.Actor import Actor


class OurActor(Actor):
    def __init__(self, name, productName=None, configFile=None, logLevel=logging.INFO):
        # This sets up the connections to/from the hub, the logger, and the twisted reactor.
        #

        Actor.__init__(self, name,
                       productName=productName,
                       configFile=configFile)




def main():

    theActor = OurActor('seqno', productName='seqnoActor')
    theActor.run()


if __name__ == '__main__':
    main()
