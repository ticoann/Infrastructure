from WMCore.Database.CMSCouch import CouchServer
from optparse import OptionParser
import json
import os
import time
import datetime
from collections import defaultdict
def options():
    """
    get the options and arguments for the script
    """
    parser = OptionParser()

    parser.add_option("-a", "--app",
        metavar="COUCHAPP",
        dest="app",
        help="path to the directory containing COUCHAPP"
    )

    parser.add_option("-j", "--jsondata",
        metavar="DATA",
        dest="data",
        help="path to the directory containing DATA to push into CouchDB instance"
    )

    parser.add_option("-c", "--couchurl",
        metavar="COUCHURL",
        dest="couch",
        default="http://localhost:5984",
        help="CouchDB instance is available on COUCHURL (default: http://localhost:5984)"
    )

    parser.add_option("-p", "--preserve",
        dest="preserve",
        action="store_true",
        default=False,
        help="preserve the database used for profiling"
    )
    parser.add_option("-n", "--iterations",
        dest="iterations",
        type="int",
        default=1,
        metavar="N",
        help="run N iterations of the profiler, default is 1"
    )
    parser.add_option("-s", "--store",
        dest="store",
        action="store_true",
        default=False,
        help="write the profile results to CouchDB (in a database called profile_results)"
    )
    parser.add_option("--sleep",
        dest="sleep",
        type="int",
        default=0,
        metavar="N",
        help="sleep for N seconds between loading the data and running the profiler, default is 0"
    )

    opts, args = parser.parse_args()
    opts.couch = opts.couch.strip('/')
    return opts, args

def push_data(data_dir, database):
    """
    dir should contain a bunch of json files, this function will push all that
    delicious data into the database.
    """
    for data_file in os.listdir(data_dir):
        if data_file.endswith('.json'):
            database.queue(json.load(open(os.path.join(data_dir, data_file))))
    database.commit()

def push_views(view_dir, views, database):
    """
    push the view from dir into the database
    """
    document = {}
    document['_id'] = "_design/profiler_%s" % len(views)
    document['language'] = 'javascript'
    document['views'] = {}

    for view in views:
        document['views'][view] = {}
        functions = os.listdir(os.path.join(view_dir, view))
        # Only push the map.js and reduce.js files - assume anything else is bunk
        if 'map.js' in functions:
            map_file = open(os.path.join(view_dir, view, 'map.js'))
            document['views'][view]['map'] = map_file.read()
            if 'reduce.js' in functions:
                reduce_file = open(os.path.join(view_dir, view, 'reduce.js'))
                document['views'][view]['reduce'] = reduce_file.read()
    database.commitOne(document)

def profile(views, database):
    """
    time how long it takes to generate all the views in the current design doc
    """
    start_time = datetime.datetime.now()
    # Hit the view to generate it with limit = 0 so we're not measuring network IO
    database.loadView("profiler_%s" % len(views), views[0], options={'limit':0})
    end_time = datetime.datetime.now()
    delta = end_time - start_time
    return delta.seconds + float(delta.microseconds)/1000000

def print_report(results):
    """
    print the profile results out
    """
    for key in sorted(results.keys(), reverse=True):
        print '%s | %s' % (key, sum(results[key])/len(results[key]))

def save_report(results, srv):
    """
    save the profile results to profile_results database
    """
    db = srv.connectDatabase('profile_results')
    db.commitOne({'results': results}, timestamp=True)

if __name__ == "__main__":
    opts, args = options()
    srv = CouchServer(opts.couch)

    # Get the views we're going to profile
    app_path = os.path.realpath(os.path.join(os.path.dirname(__file__), opts.app))
    # and the dummy data
    data_path = os.path.realpath(os.path.join(os.path.dirname(__file__), opts.data))

    views_path = os.path.join(app_path, 'views')
    views = os.listdir(views_path)

    results = defaultdict(list)

    for iteration in range(opts.iterations):
        for i in range(1, len(views) + 1):
            timestamp = int(time.mktime(datetime.datetime.now().timetuple()))

            database = srv.connectDatabase('view_profiler_%s' % timestamp)

            push_data(data_path, database)

            push_views(views_path, views[:i], database)

            time.sleep(opts.sleep)

            results[str(views[:i])].append(profile(views[:i], database))

            if not opts.preserve:
                srv.deleteDatabase('view_profiler_%s' % timestamp)

    print_report(results)

    if opts.store:
        save_report(dict(results), srv)