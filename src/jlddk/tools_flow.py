"""
    Data-Flow related tools

    Created on 2012-02-16
    @author: jldupont
"""

def build_pipeline(blocks):
    """
    Builds a data-flow pipeline
    
    Errors are propagated downstream.
    
    :param blocks: a list of handlers, order must be from head to tail
    
    Handler must be a callable with signature:
    
        handler(nxt_handler, (context, msg))
        
    The 'tail' of the pipeline will be receiving None for 'nxt_handler' parameter. 
    """
    pipe=None
    rblocks=reversed(blocks)   
    for block in rblocks:
        handler, name=block
        if pipe is None:
            pipe=_processor((None, handler, name))
        else:
            pipe=_processor((pipe, handler, name))
    return pipe



def _processor((nxt, handler, name)):

    def loop():
        try:
            while True:
                ctx, msg=(yield)
                msg=handler(nxt, (ctx, msg))
                if msg is not None:
                    nxt.send(msg)
                    
        except KeyboardInterrupt:
            raise
        
        except Exception,e:
            try:    nxt.send((ctx,  ("error", e)))
            except: nxt.send((None, ("error", e)))

    l=loop()
    l.next()    
    return l


