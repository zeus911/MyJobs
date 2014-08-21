import timeit
t = timeit.timeit(
        'requests.get("http://127.0.0.1", headers={"Host":"www.my.jobs"})',
        setup='import requests', number=1)
print "Time to request www.my.jobs: %f" % t
