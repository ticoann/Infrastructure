import json
import random
import os
import string
import datetime
from optparse import OptionParser

p = OptionParser()
o, a = p.parse_args()

if len(a) > 0:
    size = int(a[0])
else:
    size = 100

start_time = datetime.datetime.now()
for i in range(size):
    d = {
            'small_int': random.randint(0,10),
            'big_int': random.randint(1000, 100000000),
            'short_string': ''.join(random.choice(string.letters + string.digits) for i in xrange(10)),
            'long_string': ''.join(random.choice(string.letters + string.digits) for i in xrange(1000))
        }
    json.dump(d, open('data/data_%s.json' % i, 'w'))
end_time = datetime.datetime.now()
delta = end_time - start_time
print "generated %s data files in %s seconds" % (size, delta.seconds + float(delta.microseconds)/1000000)