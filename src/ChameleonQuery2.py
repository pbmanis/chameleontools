from __future__ import print_function

"""
Read chameleon parameters and print to screen

Pbmanis 2017-2020
UNC Chapel Hill
It is important to keep compatibility with Python 2.7 for now.

"""
import os
import sys
import serial
import argparse
# from pathlib import Path
import struct
import datetime
from collections import OrderedDict
import time
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as mpl
import pandas as pd


queries = OrderedDict([
        ('SN', ['Serial Number', ""]), 
        ('UF', ['Power', "mW"]), 
        ('VW', ['Wavelength', "nm"]),
        ("ALIGN",[ "Alignment Mode", ""]),
        ("ALIGNP",[ "Alignment Power", "mW"]) ,
        ("ALIGNW",[ "Alignment Wavelength", "nm"]),
        ('RH', ['Relative Humidity', '%']), 
        ('ST', ['Operating Status', ""]), 
        ('AMDLK', ['Automodelock', ""]),
        ('PHLDC', ['Cavity Peak Hold', ""]), 
        ('PZTMC', ['Cavity PZT Mode', ""]),
        ('PZTXC', ['Cavity PZT X', ""]), 
        ('PZTYC', ['Cavity PZT Y', ""]),
         ('PHLDP',[ 'Pump Peak Hold', ""]), 
         ('PZTMP', ['PZT Pump Mode', ""]),
        ('PZTXP', ['PZT X voltage', "V"]), 
        ('PZTYP', ['PZT Y voltage', "V"]), 
        ('PTRK', ['Power Track', ""]),
        ('MDLK', ['ModeLocked', ""]), 
        ('PP', ['Pump Setting', ""]),
        ('TS', ['Tuning Status', ""]), 
        ('SM', ['Search Modelock', ""]),
        ('HM', ['Homed', ""]),
        ('STPRPOS',[ 'Stepper Position', "counts"]),
        ('C', ['Average Diode Current', "A"]),
        ('-1', ['', '']),
        ('D1C',[ 'Diode 1 Current', "A"]), ('D2C', ['Diode 1 Current', "A"]),
        ('D1V', ['Diode 1 Voltage', "V"]), ('D2V', ['Diode 2 Voltage', "V"]),
        ('D1T', ['Diode 1 Temperature', "degC"]), ('D2T', ['Diode 2 Temperature', "degC"]),
        ('D1ST', ['Diode 1 Set Temperature', "degC"]), ('D2ST', ['Diode 2 Set Temperature', "degC"]),
        ('D1TD', ['Diode 1 Temp Drive', '']), ('D2TD', ['Diode 2 Temp Drive', '']),
        ('D1HST', ['Diode 1 Heatsink', "degC"]), ('D2HST', ['Diode 2 Heatsink', "degC"]),
        ('D1H', ['Diode 1 Hours', '']), ('D2H', ['Diode 2 Hours', '']),
        ('-0', ['', '']),
        ('BT', ['Baseplate Temperature', "degC"]),
        ('VT', ['Vanadate Temperature', "degC"]), ('VST', ['Vanadate Set Temperature', "degC"]),
        ('LBOT', ['LBO Temperature', "degC"]),  ('LBOST', ['LBO Set Temperature', "degC"]),
        ('ET', ['Etalon Temperature', "degC"]), ('EST', ['Etalon Set Temperature', "degC"]),

        ('-2',[ '', '']),
        ('VD',[ 'Vanadate Drive', ""]), ('LBOD', ['LBO Drive', ""]),
        ('ED', ['Etalon Drive', '']),
        ('LBOH',[ 'LBO Heater', '']),
        ('-3', ['', '']),
        ('LRS', ['Light Loop Servo', '']),
         ('D1SS', ['Diode 1 Servo Status', '']), ('D2SS', ['Diode 2 Servo Status', '']),
        ('VSS', ['Vanadate Servo Status', '']),
        ('LBOSS', ['LBO Servo Status', '']), ('ESS', ['Etalon Servo Status', '']),
        ('-4', ['', '']),
        ('PZTS', ['PZT Control State', '']),
        ('P', ['P = ', '']),
        ('PZTXCM', ['PZT X Cavity Powermap', '']), ('PZTXCP', ['PZT X Cavity Position', '']),
        ('PZTXPM',[ 'PZT X Pump Powermap', '']), ('PZTXPP', ['PZT X Pump Position', '']),
        ('PZTYCM', ['PZT Y Cavity Powermap', '']), ('PZTYCP', ['PZT Y Cavity Position', '']),
        ('PZTYPM', ['PZT Y Pump Powermap', '']), ('PZTYPP', ['PZT Y Pump Position', '']),
        ('-5', ['', '']),
        ('HH', ['Head Hours', '']),
        ('SV', ['Software Version', '']), ('B', ['Baudrate', '']),
        ('BV', ['Battery Voltage', 'V']), 
        ])


class TimeoutError(Exception):
    pass


class Coherent(object):

    def __init__(self, port, baud=19200):
        """
        port: serial COM port (0==COM1, 1==COM2, ...)
        """
        self.port = port  # map it for us
        self.baud = baud
        print(self.port)
        self.open_chameleon()
        # try:
        #     # assert 1==0
        #     self.chameleon_serial = serial.Serial("COM{0:d}".format(int(self.port)), baudrate=self.baud, bytesize=serial.EIGHTBITS)
        # except:
        #     self.chameleon_serial = serial.Serial(int(self.port), baudrate=self.baud, bytesize=serial.EIGHTBITS)

        time.sleep(0.3)  ## Give devices a moment to chill after opening the serial line.
        # self.write(b"PROMPT=0\r\n")
        # self.readPacket()
        # self.write(b"ECHO=0\r\n")
        # self.readPacket()
        # self.write(b"HEARTBEAT=0\r\n")
        # self.readPacket()
        print("Connected to Chameleon Vision II")

    def open_chameleon(self):
        self.chameleon_serial = serial.Serial('COM%d' % self.port, self.baud, timeout=2)
        self.chameleon_serial.write(b'E=0\r\n')  # turn off echo
        self.chameleon_serial.readline()  # get the incoming line

    def close_chameleon(self):
        self.chameleon_serial.close()
        self.chameleon_serial = None

    def getPower(self):
        v = self['UF']
        try:
            return float(v)
        except:
            print(v, type(v))
            raise

    def getDiodeCurrents(self):
        d1 = self['D1C']
        d2 = self['D2C']
        try:
            return(float(d1), float(d2))
        except:
            print(d1, d2, type(d1), type(d2))
            raise

    def getDiodeTemps(self):
        d1 = self['D1T']
        d2 = self['D2T']
        try:
            return(float(d1), float(d2))
        except:
            print(d1, d2, type(d1), type(d2))
            raise

    def getBaseplateTemp(self):
        temp = self['BT']
        try:
            return float(temp)
        except:
            print(temp, type(temp))
            raise

    def getEtalonTemp(self):
        temp = self['ET']
        try:
            return float(temp)
        except:
            print(temp, type(temp))
            raise

    def getVanadateTemp(self):
        temp = self['VT']
        try:
            return float(temp)
        except:
            print(temp, type(temp))
            raise

    def getLBOTemp(self):
        temp = self['LBOT']
        try:
            return float(temp)
        except:
            print(temp, type(temp))
            raise


    def getWavelength(self):
        return float(self['VW'])

    def setWavelength(self, wl, block=False):
        """Set wavelength to wl in nanometers.
        If block=True, do not return until the tuning is complete."""
        self['WAVELENGTH'] = int(wl)
        if block:
            while True:
                if not self.isTuning():
                    break
                time.sleep(0.1)
                print("still tuning")

    def getWavelengthRange(self):
        return float(self['TMIN']), float(self['TMAX'])

    def getGDDMinMax(self):
        """
        find the gdd min and max for current wavelength, and return the tuple
        """
        gddmin = int(self['GDDMIN'])
        gddmax = int(self['GDDMAX'])
        return((gddmin, gddmax))

    def getGDD(self):
        return(self['GDD'])

    def getComp(self):
        comp = self['COMP']
        return comp

    def setGDD(self, gddValue):
        """
        set the GDD value as requested. We do nothing if it is outside the range
        """
        gddMinMax = self.getGDDMinMax()
        if int(gddValue) < gddMinMax[0] or int(gddValue) > gddMinMax[1]:
#            print 'apparently outside range'
            return
        self['GDD'] = gddValue

    def clearGDD(self):
        """
        set GDD curve to curve 0 (no dispersion)
        """
        self['GDDCURVE'] =b'0'


    def isTuning(self):
        """Returns True if the laser is currently tuning its wavelength"""
        return self['TS'] != b'0'

    def getShutter(self):
        """Return True if the shutter is open."""
        return bool(int(self['SHUTTER']))

    def setShutter(self, val):
        """Open (True) or close (False) the shutter"""
        self['SHUTTER'] = (1 if val else 0)

    def setAlignment(self, align):
        """Set (1) or unset (0) alignment mode
        Note: disabling alignment mode can take several seconds.
        """
        self['ALIGN'] = align

    def getAlignment(self):
        return self['ALIGN']

    def __getitem__(self, arg):  ## request a single value from the laser
        #print "write", arg
        cmd = "?%s\r\n" % arg
        self.write(cmd)
        ret = self.readPacket()
        # print(f"getitem: cmd: {cmd:s}   return: {str(ret):s}")
        return ret

    def __setitem__(self, arg, val):  ## set a single value on the laser
        #print "write", arg, val
        cmd = "%s=%s\r\n" % (arg,str(val))
        self.write(cmd)
        ret = self.readPacket()
        #print "   return:", ret
        return ret

    def clearBuffer(self):
        d = self.read()
        time.sleep(0.1)
        d += self.read()
        if len(d) > 0:
            print("Chameleon: Warning: tossed data ", repr(d))
        return d

    def read(self):
        ## read all bytes waiting in buffer; non-blocking.
        # n = self.chameleon_serial.inWaiting()
        # if n > 0:
        data = str(self.chameleon_serial.readline())
        # print("r: ", data)
        return data
    # return ''

    def write(self, data):
        self.read()  ## always empty buffer before sending command
        # print('w data: ', data)
        self.chameleon_serial.write(bytes(data, 'utf-8'))

    def close(self):
        self.chameleon_serial.close()

    #def raiseError(self, errVals):
        ### errVals should be list of error codes
        #errors = []
        #for err in errVals:
            #hit = False
            #for k in ErrorVals:
                #if ord(err) & k:
                    #hit = True
                    #errors.append((k,)+ErrorVals[k])
            #if not hit:
                #errors.append((ord(err), "Unknown error code", ""))
        #raise MP285Error(errors)

    def readPacket(self, expect=0, timeout=10, block=True):
        ## Read until a CRLF is encountered (or timeout).
        ## If expect is >0, then try to get a packet of that length, ignoring CRLF within that data
        ## if block is False, then return immediately if no data is available.
        start = time.time()
        s = b''
        errors = []
        packets = []
        while True:
            s += self.chameleon_serial.read()
            #print "read:", repr(s)
            if not block and len(s) == 0:
                return

            while len(s) > 0:  ## pull packets out of s one at a time
                if b'\r\n' in s[expect:]:
                    i = expect + s[expect:].index(b'\r\n')
                    packets.append(s[:i])
                    expect = 0
                    s = s[i+2:]
                else:
                    break

            if len(s) == 0:
                if len(packets) == 1:
                    if b'Error' in packets[0]:
                        raise Exception(packets[0])
                    return packets[0]   ## success
                if len(packets) > 1:
                    raise Exception("Too many packets read.", packets)

            time.sleep(0.01)
            if time.time() - start > timeout:
                raise TimeoutError("Timeout while waiting for response. (Data so far: %s)" % (repr(s)))


class ChameleonScan():
    def __init__(self, port=5, baud=19200):
        self.port = port
        self.baud = baud

    def scan(self):
        C = Coherent(port=self.port, baud=self.baud)  # opens as well
        wmin, wmax = C.getWavelengthRange()
        wlmin = np.min((wmin, wmax))
        wlmax = np.max((wmin, wmax))
        wavelength = np.arange(wlmin, wlmax, 10)
        truewavelength = np.zeros_like(wavelength)
        mtime = [0]*len(wavelength)
        power = np.zeros_like(wavelength)
        print('\nScanning power across wavelengths')
        print('='*60)
        print('WL   MeasWL   Power')

        for i, wl in enumerate(wavelength):
            C.setWavelength(wl, block=True)
            power[i] = C.getPower()
            truewavelength[i] = C.getWavelength()
            mtime[i] = datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S")
            print('{0:4.0f}  {1:4.0f}  {2:5.3f}'.format(wl, truewavelength[i], power[i]))
        C.close_chameleon()
        print('='*60)
        df = pd.DataFrame({'Date': mtime, 'Wavelength': truewavelength, 'Power': power})
        finishtime = datetime.datetime.now().strftime("%d-%b-%Y_%H-%M-%S")
        fn = os.path.join('data', 'scans', 'ChameleonScan_'+finishtime+'.csv')
        df.to_csv(fn)
        self.filename = fn
        self.data = df
        self.showscan()

    def showscan(self):
        fig, ax = mpl.subplots(1,1)
        wl = self.data['Wavelength']
        power = self.data['Power']
        ax.plot(wl, power, 'ko-')
        ax.set_ylim((0, 4000.))
        ax.set_xlim((650., 1100.))
        mpl.show()

    def allscans(self):
        datas = os.listdir(os.path.join('data', 'scans'))
        fig, ax = mpl.subplots(1,1)
        for i, d in enumerate(datas):
            fn = datas[int(i)]
            self.filename = fn
            self.data = pd.read_csv(os.path.join('data', 'scans', fn))
            wl = self.data['Wavelength']
            power = self.data['Power']
            ax.plot(wl, power,  markersize=4, label=fn.replace('_', '\_'))
        ax.set_ylim((0, 4000.))
        ax.set_xlim((650., 1100.))
        fig.legend(fontsize=6)
        mpl.show()

    def getdata(self):
        datas = os.listdir(os.path.join('data', 'scans'))
        for i, d in enumerate(datas):
            print("{0:d}  {1:s}".format(i, d))
        n = input("\nSelect a file to read ('q' to quit): ")
        if n == 'q':
            exit()
        n = int(n)
        if n < 0 or n >= len(datas):
            exit()
        fn = datas[int(n)]
        self.filename = fn
        self.data = pd.read_csv(os.path.join('data', 'scans', fn))
        print(self.data.columns)
        self.showscan( )


class ChameleonMonitor():
    def __init__(self, port=8, baud=19200, interval=20., writeflag=True):
        self.port = port
        self.baud = baud
        self.interval = interval
        self.writeflag = writeflag

    def monitor(self):
        C = Coherent(port=self.port, baud=self.baud)
        C.setWavelength(800, block=True)
        bt = []
        et = []  # etalon
        lbot = []  # lbo temp
        vt = []  # vanadate
        d1t = []
        d2t = []
        d1c = []
        d2c = []
        power = []
        wavelength = []
        tsec = []
        start_time = time.time()
        # make a filename for the date/time:
        tnow = datetime.datetime.now()
        fn0 = 'ChameleonMon_' + tnow.strftime('%Y.%d.%m_%H.%M.%S') + '.txt'
        fn = os.path.join('data', 'monitoring', fn0)
        print('\nStarting Monitor over time of temperatures and power')
        print('File: %s' % fn)
        if self.writeflag:
            fh = open(fn, 'w')
            fh.write('t(sec)\tBase(C)\tD1C(A)\tD2C(A)\tD1T(C)\tD2T(C)\tVT(C)\tLBOT(C)\tET(C)\tPower(W)\tWavelength(nm)\n')
            fh.close()
        tottime = 8.0 # hours
        ttsec = int(tottime*3600./interval)
        print('t(sec)\tBase(C)\tD1C(A)\tD2C(A)\tD1T(C)\tD2T(C)\tVT(C)\tLBOT(C)\tET(C)\tPower(W)\tWavelength(nm)')
        for i in range(ttsec):
            bt.append(C.getBaseplateTemp())
            diodes = C.getDiodeCurrents()
            d1c.append(diodes[0])
            d2c.append(diodes[1])
            dtemps = C.getDiodeTemps()
            d1t.append(dtemps[0])
            d2t.append(dtemps[1])
            lbot.append(C.getLBOTemp())
            et.append(C.getEtalonTemp())
            vt.append(C.getVanadateTemp())
            power.append(C.getPower())
            wavelength.append(C.getWavelength())
            tx = time.time()
            t = tx - start_time
            tsec.append(t)
            print('{0:6.1f}\t{1:6.2f}\t{2:5.1f}\t{3:5.1f}\t{4:6.1f}\t{5:6.1f}\t{6:7.1f}\t{7:7.1f}\t{8:6.1f}\t{9:5.1f}\t{10:6.0f}'.
                            format(t, bt[-1], diodes[0], diodes[1], dtemps[0], dtemps[1], vt[-1], lbot[-1], et[-1], power[-1], wavelength[-1]))
            if self.writeflag:
                fh = open(fn, 'a')
                fh.write('{0:6.1f}\t{1:6.2f}\t{2:5.1f}\t{3:5.1f}\t{4:6.1f}\t{5:6.1f}\t{6:7.1f}\t{7:7.1f}\t{8:6.1f}\t{9:5.1f}\t{10:6.1f}\n'.
                            format(t, bt[-1], diodes[0], diodes[1], dtemps[0], dtemps[1], vt[-1], lbot[-1], et[-1], power[-1], wavelength[-1]))
                fh.close()
            while(time.time() - tx) < interval:
                x = 1
        C.close_chameleon()
        self.data = pd.read_table(fn)
        self.filename = fn0
        self.showmonitor()

    def showmonitor(self):
        f, ax = mpl.subplots(4,1)
        # print(dir(f))
        f.set_size_inches((8.5, 6))
        ax[0].plot(self.data['t(sec)'], self.data['BaseTemp(C)'], 'ro-', markersize=3.5)
        ax[0].set_xlabel('Time (sec)')
        ax[0].set_ylabel('Base Temperature(deg C)', fontsize=8)
        ax[0].set_ylim(20., 45.)

        ax[1].plot(self.data['t(sec)'], self.data['D1C(A)'], 'ro-', markersize=3.5)
        ax[1].plot(self.data['t(sec)'], self.data['D2C(A)'], 'bs-', markersize=3.5)
        ax[1].set_xlabel('Time (sec)')
        ax[1].set_ylabel('Diode Current (A)', fontsize=8)
        ax[1].set_ylim(20., 50.)

        ax[2].plot(self.data['t(sec)'], self.data['D1T(C)'], 'ro-', markersize=3.5)
        ax[2].plot(self.data['t(sec)'], self.data['D2T(C)'], 'bs-', markersize=3.5)
        ax[2].set_xlabel('Time (sec)')
        ax[2].set_ylabel('Diode Temp(deg C)', fontsize=8)
        ax[2].set_ylim(20., 30.)

        ax[3].plot(self.data['t(sec)'], self.data['Power(W)']/1000., 'ro-', markersize=3.5)
        ax[3].set_xlabel('Time (sec)')
        ax[3].set_ylabel('Power (W)', fontsize=8)
        ax[3].set_ylim(0., 4.0)
        fn = self.filename.replace('_', '\_')
        f.suptitle("{0:s}".format(fn))
        mpl.show()

    def getdata(self):
        datas = os.listdir(os.path.join('data', 'monitoring'))
        for i, d in enumerate(datas):
            print("{0:d}  {1:s}".format(i, d))
        n = input("\nSelect a file to read ('q' to quit): ")
        if n == 'q':
            exit()
        n = int(n)
        if n < 0 or n >= len(datas):
            exit()
        fn = datas[int(n)]
        self.filename = fn
        self.data = pd.read_table(os.path.join('data', 'monitoring', fn))
        self.showmonitor()

class ChameleonInfo(object):
    def __init__(self, writeflag=True, port=8, baud=19200):
        self.port = port
        self.baud = baud
        self.writeflag = writeflag
       # self.open_chameleon()
        print('\nInformation on Laser\n')
        self.bulk_report()
       # self.close_chameleon()

    def open_chameleon(self):
        self.chameleon_serial = serial.Serial('COM%d' % self.port, self.baud, timeout=2)
        self.chameleon_serial.write(b'E=0\r\n')  # turn off echo
        self.chameleon_serial.readline()  # get the incoming line

    def close_chameleon(self):
        self.chameleon_serial.close()
        self.chameleon_serial = None


    def bulk_report(self):
        report_txt = []
        self.open_chameleon()
        tnow = datetime.datetime.now()
        fn0 = 'ChameleonInfo_' + tnow.strftime('%Y.%d.%m_%H.%M.%S') + '.txt'
        fn = os.path.join('data', 'monitoring', fn0)
        print('Info report saving to File: %s' % fn)

        print ('\nReport for Chameleon Vision II with OPO, Manis Lab')
        print ('     ' + tnow.strftime("%d %B %Y  %H:%M:%S")+'\r\n')
        if self.writeflag:
            fh = open(fn, 'w')
            fh.write('Report for Chameleon Vision II with OPO, Manis Lab\n')
            fh.write('Generated on: 0'+tnow.strftime('%Y.%d.%m_%H.%M.%S')+'\n')
            fh.close()
        for q in queries.keys():
            if q[0] == '-':
                print('')
            else:
                self.chameleon_serial.write(bytes('?'+q+'\r\n', 'utf8'))
                r = self.chameleon_serial.readline()
                report = f"{queries[q][0]:>26s}  {r.decode('utf-8').strip():<24s} {queries[q][1]:<5s} {q:<6s}"
                print(report)
                if self.writeflag:
                    fh = open(fn, 'a')
                    fh.write(report)
                    fh.close()

        r = self.chameleon_serial.readline()
        print('Faults: %s' % r)
        print('Fault History: ')
        self.chameleon_serial.write(b'?FH\r\n')
        r2 = self.chameleon_serial.readline()
        print('   %s' % r2)
        self.close_chameleon()
        if self.writeflag:
            fh = open(fn, 'a')
            fh.write('Faults: %s\n' % str(r))
            fh.write('Fault History:\n')
            fh.write('    %s' % str(r2))
            fh.close()


def main():
    parser = argparse.ArgumentParser('Chameleon Query')
    parser.add_argument('mode', choices=['info', 'scan', 'monitor', 'test', 'showmon',
            'showscan', 'allscans'],
        help='Select mode for query')
    args = parser.parse_args()
    # bulk report:
    if args.mode == 'info':
        Ch = ChameleonInfo(port=5, baud=19200)
    elif args.mode == 'scan':
        C=ChameleonScan(port=5, baud=19200)
        C.scan()
    elif args.mode == 'monitor':
        C = ChameleonMonitor(port=5)
        C.monitor()
    elif args.mode == 'test':
        C = ChameleonMonitor(writeflag=False)
        C.monitor()
    elif args.mode == 'showmon':
        C = ChameleonMonitor(writeflag=False)
        C.getdata()

    elif args.mode == 'showscan':
        C = ChameleonScan()
        C.getdata()

    elif args.mode == 'allscans':
        C = ChameleonScan()
        C.allscans()


    else:
        print('Mode: %s not implemented yet', mode)


if __name__ == '__main__':
    main()
