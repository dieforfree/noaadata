#!/usr/bin/env python

__version__ = '$Revision: 7470 $'.split()[1]
__date__ = '$Date: 2007-11-06 10:31:44 -0500 (Tue, 06 Nov 2007) $'.split()[1]
__author__ = ''

__doc__='''
Produce reports of AIS message 5 reports


@requires: U{Python<http://python.org/>} >= 2.4
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0beta1
@requires: U{pyExcelerator<http://pyexcelerator.sourceforge.net/>}

@author: U{'''+__author__+'''<http://schwehr.org/>}
@version: ''' + __version__ +'''
@copyright: 2007
@var __date__: Date of last svn commit
@undocumented: __version__ __author__ __doc__ parser success
@since: 2007-May-05
@status: Intial working version.  Still needs development
@organization: U{CCOM<http://ccom.unh.edu/>}

@license: GPL v2


@todo: Deal with ships that have there messages wag back and forth
@todo: Maybe make a flag that has the code always check for the same message and not repeat
@todo: 


'''

import sys
import os
import pyExcelerator as excel
from datetime import datetime

from ais import binary
from ais import ais_msg_5 as m5
from ais import aisstring

######################################################################
# Code that runs when this is this file is executed directly
######################################################################
if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser(usage="%prog [options] [file1] [file2] ...",
                          version="%prog "+__version__+' ('+__date__+')')

    parser.add_option('-b','--basename',dest='basename'
                      ,default=None
                      ,help='Base name to use for all generated products.  '
                      +'Defaults to the filenames')

    (options,args) = parser.parse_args()

    if len(args)==0:
        sys.exit('ERROR: must specify at least one input file')

    if None==options.basename:
        options.basename=args[0]

    workbook = excel.Workbook()
    ws_report = workbook.add_sheet('Ship Data Report')

    ws_report_row=0
    
    col=0
    ws_report.write(ws_report_row,col,'Report generated by noaadata.ais_5report.py'); col += 1
    ws_report_row+=1

    col=0
    if len(args)>1:
        ws_report.write(ws_report_row,col,'Input files:'); col += 1
    else:
        ws_report.write(ws_report_row,col,'Input file:'); col += 1
    for filename in args:
        ws_report.write(ws_report_row,col,filename); col += 1
    ws_report_row+=1

    col=0
    ws_report.write(ws_report_row,col,'MMSI'); col += 1
    ws_report.write(ws_report_row,col,'IMOnumber'); col += 1
    ws_report.write(ws_report_row,col,'callsign'); col += 1
    ws_report.write(ws_report_row,col,'name'); col += 1
    ws_report.write(ws_report_row,col,'shipandcargo'); col += 1
    ws_report.write(ws_report_row,col,'dimA'); col += 1
    ws_report.write(ws_report_row,col,'dimB'); col += 1
    ws_report.write(ws_report_row,col,'dimC'); col += 1
    ws_report.write(ws_report_row,col,'dimD'); col += 1
    ws_report.write(ws_report_row,col,'ETAmin'); col += 1
    ws_report.write(ws_report_row,col,'ETAhour'); col += 1
    ws_report.write(ws_report_row,col,'draught'); col += 1
    ws_report.write(ws_report_row,col,'destination'); col += 1
    ws_report.write(ws_report_row,col,'first reported (UTCsec)'); col += 1
    
    #r['IMOnumber'],r['callsign'],r['name'],r['shipandcargo'],r['dimA'],r['dimB'],
    #print r['dimC'],r['dimD'],r['ETAminute'],r['ETAhour'],r['ETAday'],r['ETAmonth'],r['draught'],
    #print r['destination']
    ws_report_row += 1


    msgsByShip={}
    #timeByMsg={}
    # FIX: error checking?
    for filename in args:
        linenum=0
        for line in file(filename):
            line=line.strip()
            linenum +=1
            if linenum%1000==0:
                print linenum
            fields = line.split(',')
            bv = binary.ais6tobitvec(fields[5][:38])
            mmsi = m5.decodeUserID(bv)
            timestamp=fields[-1]
            
            if mmsi in msgsByShip:
                #if line not in msgsByShip:
                msgsByShip[mmsi].append(line)
            #if line in timeByMsgs
            else:
                msgsByShip[mmsi]=[line]

    print 'Finished scan.  Now processing ships.\n'

    ships = msgsByShip.keys()
    ships.sort()

    # FIX: use this to make sure that only these fields have changed
    critFields= ('IMOnumber'
                 ,'callsign'
                 ,'name'
                 ,'shipandcargo'
                 ,'dimA'
                 ,'dimB'
                 ,'dimC'
                 ,'dimD'
                 ,'ETAminute'
                 ,'ETAhour'
                 ,'draught'
                 ,'destination'
                 )

    for mmsi in ships:
        lastMsg=None # FIX:  maybe do a closer check? This is a good first cut but need to look closer after this
 #       lastMsgDict=None
        print 'mmsi',mmsi,'  count=',len(msgsByShip[mmsi])
        for line in msgsByShip[mmsi]:
            fields=line.split(',')
            if fields[5] == lastMsg:
                continue
#            if lastMsgDict!=None:
                
            lastMsg=fields[5]
            r = m5.decode(binary.ais6tobitvec(fields[5]))
            timestamp = fields[-1]
            col=0
            # MMSI and IMO numbers are too much for excel, so make them strings
            ws_report.write(ws_report_row,col,str(mmsi)); col += 1
            ws_report.write(ws_report_row,col,str(r['IMOnumber'])); col += 1
            ws_report.write(ws_report_row,col,aisstring.unpad(r['callsign'])); col += 1
            ws_report.write(ws_report_row,col,aisstring.unpad(r['name'])); col += 1
            ws_report.write(ws_report_row,col,r['shipandcargo']); col += 1
            ws_report.write(ws_report_row,col,r['dimA']); col += 1
            ws_report.write(ws_report_row,col,r['dimB']); col += 1
            ws_report.write(ws_report_row,col,r['dimC']); col += 1
            ws_report.write(ws_report_row,col,r['dimD']); col += 1
            ws_report.write(ws_report_row,col,r['ETAminute']); col += 1
            ws_report.write(ws_report_row,col,r['ETAhour']); col += 1
            ws_report.write(ws_report_row,col,float(r['draught'])); col += 1
            ws_report.write(ws_report_row,col,aisstring.unpad(r['destination'])); col += 1
            ws_report.write(ws_report_row,col,timestamp); col += 1
    

            # FIX: keep track of the last time reported and add that as a column along with number of the same messages.
            ws_report_row += 1


        del msgsByShip[mmsi]  # Hurry up and free that memory


    workbook.save(options.basename+'.shipdata.xls')

