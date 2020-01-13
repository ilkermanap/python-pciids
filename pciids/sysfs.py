import glob
import os, sys
import subprocess 

from pciids import *

class SYSfs:
    def __init__(self):
        self.pci = PCI()
        self.modules = Modules()

def rF(p,f):
    if os.path.isfile("%s/%s" % (p,f)):
        return open("%s/%s" % (p,f)).readline().replace("0x","").strip()
    else:
        return ""

class Device:
    def __init__(self,p):
        self.path = p
        self.vendor = rF(p,"vendor")
        self.device = rF(p,"device")
        self.subdevice = "%s:%s" % (rF(p,"subsystem_vendor") , rF(p,"subsystem_device"))
        print pciids.deviceStr(self.vendor, self.device, self.subdevice)

class PCI:
    def __init__(self):
        self.path = "/sys/bus/pci/devices/0*"
        self.devices = {}
        self.inspect()

    def inspect(self):
        devPaths = glob.glob(self.path)
        for dp in devPaths:
            self.devices[dp] = Device(dp)

#rfcomm                 58009  4
class Module:
    def __init__(self, line):
        parse = line.split()
        self.name = parse[0]
        self.size = int(parse[1])
        self.usedBy = int(parse[2])
        self.uses = []
        for u in parse[3:]:
            self.uses.append(u)

        print self.name
        for u in self.uses:
            print "  ", u

class Modules:
    def __init__(self):
        self.modules = {}
        proc = subprocess.Popen(["lsmod"], shell=True, stdout=subprocess.PIPE)
        out = proc.communicate()[0].splitlines()
        for l in out[1:]:
            name = l.split()[0]
            self.modules[name] = Module(l)

if (__name__ == "__main__"):
    s = SYSfs()

