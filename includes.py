import os.path
import re
import sys
import itertools
import collections as C

def get_includes(fp):
    edges = C.defaultdict(set)
    bad = 0
    for line in fp:
        o = re.match(r'^(.*):[0-9]+: *# *include ([<"])([^ ]*)[">].*', line)
        if o:
            includer, kind, includee = o.group(1), o.group(2), o.group(3)
            if kind == '"':
                includee = os.path.join(os.path.dirname(includer), includee)
            normed = os.path.normpath(includee)
            #if includee != normed:
            #    print("Normalize %r -> %r" % (includee, normed))
            includee = normed
            edges[includee.lower()].add(includer.lower())
        else:
            bad += 1
    #print("%d bad lines" % bad)
    edges = {k: tuple(v) for k, v in edges.items()}
    return edges

def transitive_closure(edges, initial):
    parents = {a: None for a in initial}
    seen = set(k for k, v in parents.items())
    frontier = set(seen)
    while frontier:
        n = set()
        for a in frontier:
            bs = frozenset(edges.get(a, ())) - seen
            n |= bs
            for b in bs:
                parents[b] = a
        frontier = n
        seen |= frontier
    return parents

def path(parents, initial):
    v = initial
    n = []
    while v:
        n.append(v)
        v = parents[v]
    return n

def remove_edges(edges, includers, includee):
    edges[includee] = tuple(frozenset(edges[includee]).difference(includers))

def main(library_includes, application_includes, winheaders):
    with open(winheaders) as fp:
        winheaders = frozenset(line.strip().lower() for line in fp)

    with open(library_includes) as fp:
        edges = get_includes(fp)

    with open(application_includes) as fp:
        app_edges = get_includes(fp)

    remove_edges(edges, ("""
        boost/detail/win/basic_types.hpp
        boost/smart_ptr/detail/yield_k.hpp
        boost/date_time/filetime_functions.hpp
        boost/detail/interlocked.hpp
        boost/thread/win32/thread_primitives.hpp
        boost/smart_ptr/detail/lwm_win32_cs.hpp
        boost/thread/win32/thread_heap_alloc.hpp
        """.split()), 'windows.h')

    parents = transitive_closure(edges, winheaders)
    #print(parents)

    def print_all_paths(f):
        edges_inv = C.defaultdict(list)
        for k, vs in sorted(edges.items(), key=lambda a:a[0]):
            for v in sorted(vs):
                edges_inv[v].append(k)
        edges_inv = {k: tuple(sorted(frozenset(v))) for k, v in list(edges_inv.items())}
        seen = set()
        def p(f, indent):
            print(' '*indent + f)
            if f in seen:
                return
            seen.add(f)
            for v in edges_inv.get(f, []):
                p(v, indent+1)
        p(f, 0)

    #print_all_paths('boost/asio/ip/host_name.hpp')

    #def is_tpie_header(f):
    #    return (f.startswith('tpie/') and f.endswith('.h') and 'deadcode' not in f)

    #app_edges = {k: tuple(filter(is_tpie_header, v)) for k, v in app_edges.items()}

    app_includes = frozenset(k for k, v in app_edges.items() if v)

    windows_parents = []
    for f in sorted(parents.keys() & app_includes):
        print('=' * 79)
        p = path(parents, f)
        if len(p) >= 2:
            windows_parents.append(p[-2])
        print(' -> '.join(p))
        print('\n'.join(sorted(app_edges[f])))

    print('')
    print(u'\n'.join(sorted(windows_parents)))

if __name__ == '__main__':
    main(*sys.argv[1:])
