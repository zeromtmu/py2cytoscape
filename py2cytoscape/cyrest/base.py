import requests
import urllib2
import sys
import json

HOST = 'localhost'
IP=HOST # temporary
PORT = 1234
VERSION = 'v1'
BASE_URL = 'http://' + HOST + ':' + str(PORT) + '/' + VERSION + '/'
HEADERS = {'Content-Type': 'application/json'}
VERBOSE=False


SUID_LIST = 'suid'

BASE_URL_NETWORK = BASE_URL + 'networks'

def set_param(parameters,values):
    PARAMS={}
    for p,v in zip(parameters,values):
        if v:
            PARAMS[p]=v
    return PARAMS

def check_network(cyrest_network,network,verbose=False):
    if not network:
        try:
            network_name=cyrest_network.network_name
        except:
            network_name='CURRENT'
    else:
        network_name=network
    if verbose:
        print("Working on '%s' network." %str(network_name) )
    return network_name

def checkresponse(r,verbose=False):
    status=str(r.status_code)
    if status == "200":
        if verbose:
            print "response status 200"
            sys.stdout.flush()
        res=None
    elif status == "201":
        print "response status 201"
        sys.stdout.flush()
        res="error::"+str(r.status_code)
    else:
        print r, r.status_code
        sys.stdout.flush()
        res="error::"+str(r.status_code)
    return res

def handle_status_codes(x,verbose=False):
    if type(x) == str:
        if "error::" in x:
            res=int(x.lstrip("error::"))
        else:
            res=None
    else:
        res=None

    if res or verbose:
        if res:
            res=res
        else:
            res=x
    else:
        res=None

    if not res:
        if x:
            res=x

    return res


def api(namespace=None,command="",PARAMS={},host=HOST,port=str(PORT),version=VERSION,method="POST",verbose=VERBOSE, url=None):
    """
    General function for interacting with Cytoscape API.

    :param namespace: namespace where the request should be executed. eg. "string"
    :param commnand: command to execute. eg. "protein query"
    :param PARAMs: a dictionary with the parameters. Check your swagger normaly running on
    http://localhost:1234/v1/swaggerUI/swagger-ui/index.html?url=http://localhost:1234/v1/commands/swagger.json
    :param host: cytoscape host address, default=cytoscape_host
    :param port: cytoscape port, default=1234
    :param version: API version
    :param method: type of http call, ie. "POST" or "GET" or "HELP".
    :param verbose: print more information

    :returns: For "POST" the data in the content's response. For "GET" None.

    eg.
    cytoscape("string","pubmed query",{"pubmed":"p53 p21","limit":"50"})
    """

    if url:
        baseurl=url
    else:
        if namespace:
            baseurl="http://"+str(host)+":"+str(port)+"/"+str(version)+"/commands/"+str(namespace)+"/"+str(command)
        else:
            baseurl="http://"+str(host)+":"+str(port)+"/"+str(version)+"/commands"

    if (method == "GET") or (method == "G"):
        P=[]
        for p in PARAMS.keys():
            v=str(PARAMS[p])
            v=v.replace(" ","%20")
            P.append(str(p)+"="+str(PARAMS[p]))
        P="&".join(P)
        if not url:
            if namespace:
                URL=baseurl+"?"
        else:
            URL=baseurl
        if len(P)>0:
            URL=URL+P
        if verbose:
            print "'"+URL+"'"
            sys.stdout.flush()
        r = requests.get(url = URL)

        verbose_=checkresponse(r, verbose=verbose)
        if (verbose) or (verbose_):
            print "'"+URL+"'"
            sys.stdout.flush()
        if verbose_:
            res=verbose_
        else:
            res=r

    elif (method == "POST") or (method == "P"):
        if verbose:
            print "'"+baseurl+"'"
            sys.stdout.flush()
        r = requests.post(url = baseurl, json = PARAMS)
        verbose_=checkresponse(r, verbose=verbose)
        if (verbose) or (verbose_):
            verbose=True
        res=r.content
        if (verbose) or (verbose_):            
            print res
            sys.stdout.flush()
        res=json.loads(res)
        #if "errors" in res.keys():
        #    if len(res["errors"]) > 0:
        #        verbose=True
        #        for e in res["errors"]:
        #            print(e)
        if not verbose:
            res=res["data"]
        else:
            res=verbose_

    elif (method=="HTML") or (method == "H") or (method=="HELP"):
        P=[]
        for p in PARAMS.keys():
            v=str(PARAMS[p])
            v=v.replace(" ","%20")
            P.append(str(p)+"="+str(PARAMS[p]))
        P="&".join(P)
        if not url:
            if namespace:
                URL=baseurl+"?"
        else:
            URL=baseurl
        if len(P)>0:
            URL=URL+P
        if verbose:
            print "'"+URL+"'"
            sys.stdout.flush()
        response = urllib2.urlopen(URL)

        res = response.read()
        res = res.split("\n")
        def clean(x):
            r=x.split("</p>")[0].split(">")[-1]
            return r
        res="\n".join([ clean(x) for x in res ])
        #print res
        #sys.stdout.flush()

    res=handle_status_codes(res,verbose=verbose)    

    return res
