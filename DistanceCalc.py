import math
import re

class DistanceCalc:

    def __init__(self):

        self.distances = []
        self.method = 'basic'
        self.params = {}
        self.debug = False

        self.params['freq.mindist'] = 1
        self.params['freq.maxdist'] = 10
        self.params['freq.missingdist'] = 10
        self.params['freq.minprob'] = 0.00001
        self.params['freq.freqfile'] = 'brown_freq.csv'
        
        self.freqLoaded = False
        self.probs = {}
        self.memdists = {}

    def loadFreq(self):
        self.maxprob = -1

        # Load file

        if 'freq.freqfile' in self.params:
            with open(self.params['freq.freqfile'], 'U') as f:
                for line in f:
                    line = re.sub('\n','',line)
                    fields = line.split(',')
                    
                    term = fields[0]
                    probstring = fields[1]
                    try:
                        prob = float(probstring)

                        if prob < 1.0:
                            if prob > self.maxprob:
                                self.maxprob = prob
                                if self.debug:
                                    print "loadFreq: new maxprob %f for item %s" % (self.maxprob,term)

                            self.probs[term.lower()] = prob

                    except ValueError:
                        pass

            # Set up params for distance calc

            a = 1.0
            b = 1.0 / self.maxprob
            c = float(self.params['freq.mindist'])
            d = 1.0
            e = 1.0 / self.params['freq.minprob']
            f = float(self.params['freq.maxdist'])

            denom = (a * e) - (d * b)
            xnum = (c * e) - (f * b)
            x = xnum / denom
            ynum = (a * f) - (d * c)
            y = ynum / denom

            if self.debug:
                print "loadFreq: maxprob = %f, x = %f, y = %f" % (self.maxprob,x,y)

            self.params['freq.x'] = x
            self.params['freq.y'] = y

            self.freqLoaded = True

    def setFreqMethod(self):

        self.method = 'freq'


    def setBasicMethod(self):

        self.method = 'basic'

    def debugOn(self):

        self.debug = True


    def debugOff(self):

        self.debug = False


    def freqDist(self,term):

        if not self.freqLoaded:
            self.loadFreq()

        if term in self.probs:
            prob = self.probs[term]
            dist = self.params['freq.x'] + (self.params['freq.y'] / prob)
            dist = min(dist,self.params['freq.maxdist'])
        else:
            prob = -1.0
            dist = self.params['freq.missingdist']

        if self.debug:
            print "freqDist: term %s, prob %f, dist %f" % (term,prob,dist)
        
        return dist

    # The cost functions

    def delcost(self,item):

        if self.method == 'freq':
            dist = self.freqDist(item)
        elif self.method == 'basic':
            dist = 1
        else:
            dist = 1

        if self.debug:
            print "delcost: item %s dist %s" % (item,dist)

        return dist


    def inscost(self,item):
        
        if self.method == 'freq':
            dist = self.freqDist(item)
        elif self.method == 'basic':
            dist = 1
        else:
            dist = 1

        if self.debug:
            print "inscost: item %s dist %s" % (item,dist)

        return dist



    def subcost(self,item1,item2):

        if item1 == item2:
            dist = 0
        else:
            if self.method == 'freq':
                dist1 = self.freqDist(item1)
                dist2 = self.freqDist(item2)
                dist = max(dist1,dist2)
            elif self.method == 'basic':
                dist = 1
            else:
                dist = 1

        if self.debug:
            print "subcost: item1 %s item2 %s dist %s" % (item1,item2,dist)

        return dist




    # Top-level calc

    def lev(self,list1,list2,**args):

        if 'key1' in args and 'key2' in args:
            if args['key1'] in self.memdists:
                if args['key2'] in self.memdists[args['key1']]:
                    return self.memdists[args['key1']][args['key2']]

        len1 = len(list1)
        len2 = len(list2)

        # Set up distance and backtrace arrays

        self.distances = []
        self.pathtypes = []

        for i in range(len1+1):
            rowlist = []
            for j in range (len2+1):
                rowlist.append(-1)
            self.distances.append(rowlist)

        for i in range(len1+1):
            rowlist = []
            for j in range (len2+1):
                rowlist.append('')
            self.pathtypes.append(rowlist)

        # Return value at string lengths

        dist = self.lev1(list1,list2,len1,len2)

        # If debug, go through the backtrace

        if self.debug:
            idx1 = len1
            idx2 = len2
            while idx1 > 0 or idx2 > 0:
                type = self.pathtypes[idx1][idx2]
                if type == 'sub':
                    newidx1 = idx1 - 1
                    newidx2 = idx2 - 1
                elif type == 'del':
                    newidx1 = idx1 - 1
                    newidx2 = idx2
                elif type == 'ins':
                    newidx1 = idx1
                    newidx2 = idx2 - 1
    
                distdiff = self.distances[idx1][idx2] - self.distances[newidx1][newidx2]
                
                print "lev backtrace: idx1 %d idx2 %d type %s dist %f cumdist %f" % (idx1,idx2,type,distdiff,self.distances[idx1][idx2])
                idx1 = newidx1
                idx2 = newidx2

        if 'key1' in args and 'key2' in args:
            if not args['key1'] in self.memdists:
                self.memdists[args['key1']] = {}
            self.memdists[args['key1']][args['key2']] = dist
            if not args['key2'] in self.memdists:
                self.memdists[args['key2']] = {}
            self.memdists[args['key2']][args['key1']] = dist

        return dist



    # Underlying recursive calc

    def lev1(self,list1,list2,idx1,idx2):

        if not self.distances[idx1][idx2] == -1:
            return self.distances[idx1][idx2]
        else:
            if max(idx1,idx2) == 0:
                dist = 0.0
                pathtype = 'initial'
            else:
                dist = 9999999999

                if idx1 > 0:
                    one = self.lev1(list1,list2,idx1-1,idx2) + self.delcost(list1[idx1-1])
                    if one < dist:
                        dist = one
                        pathtype = 'del'
                else:
                    one = 999999
                        
                if idx2 > 0:
                    two = self.lev1(list1,list2,idx1,idx2-1) + self.inscost(list2[idx2-1])
                    if two < dist:
                        dist = two
                        pathtype = 'ins'
                else:
                    two = 999999

                if idx1 > 0 and idx2 > 0:
                    three = self.lev1(list1,list2,idx1-1,idx2-1) + self.subcost(list1[idx1-1],list2[idx2-1])
                    if three < dist:
                        dist = three
                        pathtype = 'sub'
                else:
                    three = 999999

                if self.debug:
                    print "lev1: idx1 %d idx2 %d deldist %f insdist %f subdist %f pathtype %s" % (idx1,idx2,one,two,three,pathtype)

            self.distances[idx1][idx2] = dist
            self.pathtypes[idx1][idx2] = pathtype
            return(dist)

