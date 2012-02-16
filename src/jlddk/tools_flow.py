"""
    Data-Flow related tools

    Created on 2012-02-16
    @author: jldupont
"""

def build_pipeline(blocks):
    """
    Builds a data-flow pipeline
    
    Errors are propagated downstream.
    
    :param blocks: a list of python modules with a 'run' function, order must be from head to tail
    
        (mod, config_params)
    
    Run function must have this signature:
    
        run(params, nxt_handler, (context, msg))
        
    The 'tail' of the pipeline will be receiving None for 'nxt_handler' parameter. 
    """
    pipe=None
    rblocks=reversed(blocks)   
    for block in rblocks:
        mod, params=block
        try:
            run=getattr(mod, "run")
        except:
            raise Exception("Can't find 'run' function in module '%s'" % str(mod))
        if pipe is None:
            pipe=_processor((None, run, params))
        else:
            pipe=_processor((pipe, run, params))
    return pipe



def _processor((nxt, run, params)):

    def loop():
        try:
            while True:
                ctx, msg=(yield)
                msg=run(params, nxt, (ctx, msg))
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


