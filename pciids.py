import os
import urllib2
import glob
import subprocess

global HOME
HOME = "https://pci-ids.ucw.cz"

class Vendor:
    def __init__(self, vendorStr):
        self.ID = vendorStr.split()[0]
        self.name = vendorStr.replace("%s " % self.ID,"")
        self.devices = {}

    def addDevice(self, deviceStr):
        s = deviceStr.strip()
        devID = s.split()[0]
        if devID in self.devices:
            pass
        else:
            self.devices[devID] = Device(deviceStr)

    def report(self):
        print self.ID, self.name
        for id, dev in self.devices.items():
            dev.report()

class Device:
    def __init__(self, deviceStr):
        s = deviceStr.strip()
        self.ID = s.split()[0]
        self.name = s.replace("%s  " % self.ID,"")
        self.subdevices = {}

    def report(self):
        print "\t%s\t%s" % (self.ID, self.name)
        for subID, subdev in self.subdevices.items():
            subdev.report()

    def addSubDevice(self, subDeviceStr):
        s = subDeviceStr.strip()
        spl = s.split()
        subVendorID  = spl[0]
        subDeviceID  = spl[1]
        subDeviceName = s.split("  ")[-1]
        devID = "%s:%s" % (subVendorID,subDeviceID)
        self.subdevices[devID] = SubDevice(subVendorID,subDeviceID,subDeviceName)

class SubDevice:
    def __init__(self, vendor, device, name):
        self.vendorID = vendor
        self.deviceID = device
        self.name = name

    def report(self):
        print "\t\t%s\t%s\t%s" % (self.vendorID, self.deviceID,self.name)

class PCIIds:
    def __init__(self):
        self.version = ""
        self.compressed = "pci.ids.bz2"
        subprocess.call(['mkdir -p data'], shell=True)
        self.vendors = {}
        self.contents = None
        self.loadLocal()
        self.parse()

    def reportVendors(self):
        for vid, v in self.vendors.items():
            print v.ID, v.name

    def report(self, vendor = None):
        if vendor != None:
            self.vendors[vendor].report()
        else:
            for vID, v in self.vendors.items():
                v.report()

    def parse(self):
        if len(self.contents) < 1:
            print "data/%s-pci.ids not found" % self.version
        else:
            vendorFound = False
            vendorID = ""
            deviceID = ""
            for l in self.contents:
                if l[0] == "#":
                    continue
                elif len(l.strip()) == 0:
                    continue
                else:
                    if l.find("\t\t") == 0:
                        self.vendors[vendorID].devices[deviceID].addSubDevice(l)
                    elif l.find("\t") == 0:
                        deviceID = l.strip().split()[0]
                        self.vendors[vendorID].addDevice(l)
                    else:
                        vendorID = l.split()[0]
                        self.vendors[vendorID] = Vendor(l)

    def getLatest(self):
        ver, url = self.latestVersion()
        outfile = "data/%s-%s" % (ver, self.compressed)
        out = open(outfile, "w")
        out.write(urllib2.urlopen(url).read())
        out.close()
        subprocess.call(['bzip2 -d %s' % outfile], shell=True) 
        self.version = ver
        self.readLocal()

    def readLocal(self):
        self.contents = open("data/%s-pci.ids" % self.version).readlines()

    def loadLocal(self):
        idsfile = glob.glob("data/*.ids")
        if len(idsfile) == 0:
            self.getLatest()
        else:
            self.version = idsfile[0].split("/")[1].split("-")[0]
            self.readLocal()

    def latestVersion(self):
        webPage = urllib2.urlopen(HOME).readlines()
        for line in webPage:
             if line.find(self.compressed) > -1:
                for tag in line.split("<"):
                    if tag.find(self.compressed) > -1:
                        path = tag.split('"')[1]
                        ver = path.split("/")[1]
                        return (ver, "%s%s" % (HOME, path))
                break
        return ""


if __name__ == "__main__":
    id = PCIIds()
    id.reportVendors()
