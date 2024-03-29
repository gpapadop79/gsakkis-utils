"""Use to verify the results generated by your solution.

My solution is safely hidden on a server so you can't peek :-)
The bad part is that you need internet access to use it.
"""

if 0:
    from fly_oracle import fly
else:
    import xmlrpclib

    s = xmlrpclib.Server('http://www.sweetapp.com/cgi-bin/pycontest/fly_oracle.py')

    def fly(from_, to, schedule):
        # Only strings can be XML-RPC dictionary keys, so flatten
        # dictionary into a list of key, value tuples
        s2 = [day.items() for day in schedule]

        try:
            return s.fly(from_, to, s2)
        except xmlrpclib.Fault, f:
            raise ValueError(f.faultString)

