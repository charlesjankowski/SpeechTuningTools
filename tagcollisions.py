import argparse
import DistanceCalc
import ExcelData
import math

parser = argparse.ArgumentParser(description='Find candidates for tagging collisions.')

parser.add_argument('-tagfile', dest='tagfile', action='store', help='Name of tagss file', required=True)
parser.add_argument('-tagsheet', dest='tagsheet', action='store', help='Name of sheet in tagss file', default='Sheet1')
parser.add_argument('-phrasescolumn', dest='phrasescolumn', action='store', help='tab column with phrases', required=True)
parser.add_argument('-tagcolumn', dest='tagcolumn', action='store', help='tab column with phrase tags', required=True)
parser.add_argument('-outfile', dest='outfile', action='store', help='Name of output Excel file', default=None)
parser.add_argument('-outsheet', dest='outsheet', action='store', help='Name of output sheet', default='Sheet1')
parser.add_argument('-debuglevel', dest='debuglevel', action='store', help='Debug level', type=int, default=0)

args = parser.parse_args()

if args.outfile:
    import ExcelDataWrite

# Get the Excel data

exceldata = ExcelData.ExcelData(args.tagfile)
sheetdata = exceldata.getData(args.tagsheet)

# Go through tags

tags = {}
for (phrase,tag) in [(dic[args.phrasescolumn], dic[args.tagcolumn]) for dic in sheetdata]:
    if not tag in tags:
        tags[tag] = []

    tags[tag].append(phrase)

# Set up distance calc

lev = DistanceCalc.DistanceCalc()
#lev.setBasicMethod()
lev.setFreqMethod()
#lev.debugOn()

# Variance estimates of classes (tags)

sds = {}
for tag in tags:
    sumdistsq = 0.0
    numdist = 0
    for phrase1 in tags[tag]:
        for phrase2 in tags[tag]:
            if not phrase1 == phrase2:
                list1 = phrase1.split(' ')
                list2 = phrase2.split(' ')

                dist = lev.lev(list1,list2,key1=phrase1,key2=phrase2)

                if args.debuglevel >= 2:
                    print "tag %s phrase1 %s phrase2 %s dist %f" % (tag,phrase1,phrase2,dist)

                distsq = dist * dist
                sumdistsq += distsq
                numdist += 1
    sds[tag] = math.sqrt(sumdistsq / numdist)
    if args.debuglevel >= 1:
        print "tag %s variance %f" % (tag,sds[tag])

# Overall variance

sumdistsq = 0.0
numdist = 0

for tag1 in tags:
    for phrase1 in tags[tag1]:
        for tag2 in tags:
            for phrase2 in tags[tag2]:
                if not phrase1 == phrase2:
                    list1 = phrase1.split(' ')
                    list2 = phrase2.split(' ')

                    dist = lev.lev(list1,list2,key1=phrase1,key2=phrase2)

                    if args.debuglevel >= 2:
                        print "tag1 %s phrase1 %s tag2 %s phrase2 %s dist %f" % (tag1,phrase1,tag2,phrase2,dist)

                    distsq = dist * dist
                    sumdistsq += distsq
                    numdist += 1

sd = math.sqrt(sumdistsq / numdist)
if args.debuglevel >= 1:
    print "overall variance %f" % sd

# Go through phrases

for tag in tags:
    for phrase in tags[tag]:
        phdists = {}
        for tag2 in tags:
            sumdist = 0.0
            numdist = 0
            for phrase2 in tags[tag2]:
                list = phrase.split(' ')
                list2 = phrase2.split(' ')

                dist = lev.lev(list,list2,key1=phrase,key2=phrase2)
                sumdist += dist
                numdist += 1
            phdists[tag2] = (sumdist / numdist) / sds[tag2]
            
            if args.debuglevel >= 2:
                print "tag %s phrase %s tag2 %s ndist %f" % (tag,phrase,tag2,phdists[tag2])

# Look for similar phrases with different tags

distdic = []
for tag1 in tags:
    for phrase1 in tags[tag1]:
        for tag2 in tags:
            for phrase2 in tags[tag2]:
                if not tag1 == tag2:
                    list1 = phrase1.split(' ')
                    list2 = phrase2.split(' ')

                    dist = lev.lev(list1,list2,key1=phrase1,key2=phrase2)

                    if args.debuglevel >= 2:
                        print "tag1 %s phrase1 %s tag2 %s phrase2 %s dist %f" % (tag1,phrase1,tag2,phrase2,dist)

                    distdic.append({'TAG1': tag1, 'TAG2': tag2, 'PHRASE1': phrase1, 'PHRASE2': phrase2, 'DIST': dist})

def distsort(dic1,dic2):
    dif = dic1['DIST'] - dic2['DIST']

    if dif == 0:
        return 0
    else:
        return int(dif / abs(dif))

if args.outfile:
    excelwritedata = ExcelDataWrite.ExcelDataWrite()
    excelwritedata.setSheet(args.outsheet)

    excelwritedata.addColumn('TAG1')
    excelwritedata.addColumn('PHRASE1')
    excelwritedata.addColumn('TAG2')
    excelwritedata.addColumn('PHRASE2')
    excelwritedata.addColumn('DIST')
else:
    print 'TAG1,PHRASE1,TAG2,PHRASE2,DIST'

for dic in sorted(distdic,cmp=distsort):
    if args.outfile:
        excelwritedata.putData(dic)
    else:
        print '%s,%s,%s,%s,%f' % (dic['TAG1'],dic['PHRASE1'],dic['TAG2'],dic['PHRASE2'],dic['DIST'])

if args.outfile:
    excelwritedata.write(args.outfile)
