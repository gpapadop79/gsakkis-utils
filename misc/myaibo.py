'''Python API to Sony Aibo.'''

# debug:
# - clean shutdown
# - world state thread
# - test sensors, buttons
# - test set posture
# - test load walk (!select "-WalkControllerBehavior")
# ? sleep(x)

# questions:
#- joint limits ?

# todo:
# ? add camera
# ? logging


import sys, struct, time, threading, socket

__all__ = ["AiboClient"]
__author__ = "George Sakkis <gsakkis@rutgers.edu>"

#=============================================================================

class AiboClient:
    '''Python API to Aibo using the TekkotsuMon servers.

    B{Note:} The following TekkotsuMon servers have to be running on the Aibo
    when the AiboClient is created (the number in the parenthesis is the
    respective port)::
        - Main Control (10020)
        - EStop Remote Control (10053)
        - Walk Remote Control (10050)
        - Head Remote Control (10052)
        - Aibo 3D (10051)
        - World State Serializer (10031)

    @group Emergency Mode: enableMotors, disableMotors
    @group Movement: walk, stop, translate, rotate, strafe, loadWalkEngine
    @group Joint Accessors: leg, head, tail, mouth
    @group Joint Setters: setBodyPosture, setHeadPosture
    @group Button Accessors: pawButton, chinButton, headButton, frontButton,
        middleButton, backButton, wirelessButton
    @group Sensors: infrared, acceleration, battery, temperature, capacity,
        voltage, current
    '''
    def __init__(self, host="192.168.0.58"):
        self._clients = {}
        try:
            for server,port in self._SERVER2PORT.iteritems():
                self._clients[server] = TekkotsuMonClient(host, port)
            # create sensor thread
            self._startSensorThread(timeout=0.1)
            time.sleep(1)
            # set some tekkotsu variables
            for var in ("vision.rawcam_interval", "vision.rle_interval",
                        "vision.worldState_interval"):
                self._clients["Main Control"].sendTextCommand("!set %s=0" % var)
        except:
            self._cleanup()
            raise

    def __del__(self):
        self._cleanup()

    #==== emergency mode =====================================================

    def enableMotors(self):
        self._clients["EStop Remote Control"].sendTextCommand("start")

    def disableMotors(self):
        self._clients["EStop Remote Control"].sendTextCommand("stop")

    #==== movement ===========================================================

    def walk(self, translate=None, rotate=None, strafe=None):
        if translate is not None:
            self.translate(translate)
        if rotate is not None:
            self.rotate(rotate)
        if strafe is not None:
            self.strafe(strafe)

    def stop(self):
        self.walk(0,0,0)

    def translate(self, value):
        # -1 (backward) to 1 (forward)
        self._clients["Walk Remote Control"].sendBinaryCommand(
            'f', bound(value,-1,1))

    def rotate(self, value):
        # -1 (right) to 1 (left)
        self._clients["Walk Remote Control"].sendBinaryCommand(
            'r', bound(value,-1,1))

    def strafe(self, value):
        # -1 (right) to 1 (left)
        self._clients["Walk Remote Control"].sendBinaryCommand(
            's', bound(value,-1,1))

    def loadWalkEngine(self, filename):
        '''Load previously saved walk parameters.

        @param filename: The path to a parameters ('.prm') binary file.
        '''
        if not os.path.exists(file):
            raise IOError("No such file: '%s'" % file)
        # file: PACE.PRM, TIGER.PRM, WALK.PRM (crawl)
        # when the walk is changed, we have to reconnect to the walk server
        host,port = self._clients["Walk Remote Control"].peername()
        self._clients["Walk Remote Control"].close()
        # forces files to be read
        self._setRemoteControl("Load Walk")
        # select file
        self._setRemoteControl(file)
        # XXX: check '#' and '-' flags
        # turn off
        self._setRemoteControl("#WalkControllerBehavior")
        # turn on
        self._setRemoteControl("-WalkControllerBehavior")
        time.sleep(2)
        # walk command
        self._clients["Walk Remote Control"] = TekkotsuMonClient(host,port)

    #==== joint accessors ====================================================

    def leg(self, back, right):
        '''Get the joint positions and 'duty-cycles' of a leg.

        @param back: True for back leg, False for front leg.
        @param right: True for right leg, False for left leg.
        @return: A [rotator,elevator,knee] list, where each item is a
            [position,duty-cycle] list of the leg's current values.
        '''
        legOffset = self._legOffset(back,right)
        return [self._joint(offset)
                for offset in xrange(legOffset,legOffset+3)]

    def head(self):
        '''Get the joint position and 'duty-cycle' of the head.

        @return: A [tilt,pan,nod] list, where each item is a
            [position,duty-cycle] list of the head's current values.
        '''
        headOffset = self._SPEC["headOffset"]
        return [self._joint(offset)
                for offset in xrange(headOffset,headOffset+3)]

    def tail(self):
        '''Get the joint position and 'duty-cycle' of the tail.

        @return: A [tilt,pan] list, where each item is a
            [position,duty-cycle] list of the tails's current values.
        '''
        tailOffset = self._SPEC["tailOffset"]
        return [self._joint(offset)
                for offset in xrange(tailOffset,tailOffset+2)]

    def mouth(self):
        '''Get the joint position and 'duty-cycle' of the tail.

        @return: A [position,duty-cycle] list of the mouth's current values.
        '''
        return self._joint(self._SPEC["mouthOffset"])

    #==== joint setters ======================================================

    def setBodyPosture(self, frontLeftLeg=None, frontRightLeg=None,
                       backLeftLeg=None, backRightLeg=None,
                       tail=None, mouth=None):
        '''Set the robot's joints.

        @param frontLeftLeg, frontRightLeg, backLeftLeg, backRightLeg: A
        (rotator, elevator, knee) triple of the values of the respective leg,
        or None (for no change of the leg joints).
        @param tail: A pair (tilt,pan) of the tails's values or None
        (for no change of the tail joints).
        @param mouth: The new mouth joint value or None (for no change of the
        mouth joint).
        '''
        #@param head: A (tilt,pan,nod) triple of the head's values or None
        #(for no change of the head joints).
        joints = list(self._positionRaw)
        for leg,back,right in (("frontLeftLeg",  False, False),
                               ("frontRightLeg", False, True),
                               ("backLeftLeg",   True,  False),
                               ("backRightLeg",  True,  True)):
            legJoints = eval(leg)
            if legJoints is not None:
                rotator,elevator,knee = legJoints
                start = self._legOffset(back,right)
                if rotator is not None:
                    joints[start] = bound(rotator, -0.3, 1.6)
                if elevator is not None:
                    joints[start+1] = bound(elevator, -2.2, 2.4)
                if knee is not None:
                    joints[star2+1] = bound(knee, -0.6, 2.3)
        if tail is not None:
            tilt,pan = tail
            start = _SPEC["tailOffset"]
            if tilt is not None: joints[start+1] = bound(tilt,-1,1)
            if pan is not None: joints[start] = bound(pan,-1,1)
        if mouth is not None:
            # the original command is bounded in (-1,0), so take the neg
            joints[_SPEC["mouthOffset"]] = -bound(mouth,0,1)
        self._clients["Aibo 3D"].sendBinaryCommand(None, *joints)

    def setHeadPosture(self, tilt=None, pan=None, nod=None):
        '''Set the head joints.

        @param tilt, pan, nod: The value of the joint or None (for no change).
        '''
        headCommand = self._clients["Head Remote Control"].sendBinaryCommand
        if tilt is not None: # 0 to -1 (straight ahead to down)
            headCommand('t', bound(tilt,-1,0))
        if pan is not None:  # -1 to 1 (right to left)
            headCommand('p', bound(pan,-1,1))
        if nod is not None: # 0 to 1 (straight ahead, to up (stretched))
            headCommand('r', bound(nod,0,1))

    #==== button accessors ===================================================

    def pawButton(self, back, right):
        pawID = 0
        if back:  pawID += 2
        if right: pawID += 1
        return self._buttonRaw[pawID]

    def chinButton(self):     return self._buttonRaw[4]
    def headButton(self):     return self._buttonRaw[5]
    def frontButton(self):    return self._buttonRaw[6]
    def middleButton(self):   return self._buttonRaw[7]
    def backButton(self):     return self._buttonRaw[8]
    def wirelessButton(self): return self._buttonRaw[9]

    #==== sensors ============================================================

    def infrared(self):
        '''Return a list of [near,far,chest] IR readings.'''
        return self._sensorRaw[0:3]

    def acceleration(self):
        '''Return a list of [backward,leftward,downward] acceleration readings.'''
        return self._sensorRaw[3:6]

    def battery(self):     return self._sensorRaw[6]
    def temperature(self): return self._sensorRaw[7]
    def capacity(self):    return self._sensorRaw[8]
    def voltage(self):     return self._sensorRaw[9]
    def current(self):     return self._sensorRaw[10]

    #==== 'private' members ==================================================

    def _cleanup(self, *servers):
        for server in servers or self._clients.keys():
            client = self._clients.pop(server)
            client.close()

    def _startSensorThread(self, timeout=0.01):
        '''Update the world state info continuously in a separate thread.'''
        client = self._clients["World State Serializer"]
        def readState():
            try:
                # infinite loop; it exits if an exception is raised
                # (e.g. when closing the client)
                while True:
                    self._timestamp = client.readLong()
                    # position
                    numPIDJoints = client.readLong()
                    self._positionRaw = client.readFloat(numPIDJoints)
                    # sensor data
                    numSensors = client.readLong()
                    self._sensorRaw = client.readFloat(numSensors)
                    # buttons
                    numButtons = client.readLong()
                    self._buttonRaw = client.readFloat(numButtons)
                    # duty cycles
                    self._dutyCycleRaw = client.readFloat(numPIDJoints)
                    time.sleep(timeout)
            except socket.error, err:
                _log("Terminating world state sensor thread (error %d: %s)" % (
                    err[0], err[1]))
                self._cleanup("World State Serializer")
        threading.Thread(target=readState).start()
        time.sleep(1)

    def _setRemoteControl(self, item, off=False):
        if off: item = "#" + item
        self._clients["Main Control"].sendTextCommand('!select "%s"' % item)

    def _joint(self, index):
        return [self._positionRaw[index], self._dutyCycleRaw[index]]

    def _legOffset(back, right):
        legID = 0
        if back:  legID += 2
        if right: legID += 1
        return self._SPEC["legOffset"] + self._SPEC["jointsPerLeg"] * legID

    _SERVER2PORT = {
        "Main Control"           : 10020,
        "EStop Remote Control"   : 10053,
        #"Walk Remote Control"    : 10050,
        #"Head Remote Control"    : 10052,
        #"Aibo 3D"                : 10051,
        "World State Serializer" : 10031,
    }

    _SPEC = {
        "legOffset"     : 0,
        "numLegs"       : 4,
        "jointsPerLeg"  : 3,
        "numHeadJoints" : 3,
        "numTailJoints" : 2,
    }
    _SPEC["numLegJoints"] = _SPEC["numLegs"]    * _SPEC["jointsPerLeg"]
    _SPEC["headOffset"]   = _SPEC["legOffset"]  + _SPEC["numLegJoints"]
    _SPEC["tailOffset"]   = _SPEC["headOffset"] + _SPEC["numHeadJoints"]
    _SPEC["mouthOffset"]  = _SPEC["tailOffset"] + _SPEC["numTailJoints"]

#=============================================================================

_sizeOfLong = struct.calcsize('L')
_sizeOfFloat = struct.calcsize('f')

class TekkotsuMonClient:
    '''Talks to a TekkotsuMon server.'''

    def __init__(self, host, port, maxRetries=5, timeout=None):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.s.settimeout(timeout)
        for i in xrange(maxRetries):
            try:
                _log("[%d] trying to connect to %s:%s ..." % (i,host,port))
                self._socket.connect((host,port))
                break
            except socket.error, err:
                _log("Error %d: %s" % (err[0], err[1]))
        else:
            _log("Could not connect to the server after %d attempts "
                 "- aborting" % maxRetries)
            raise err
        _log("connected to %s:%s !" % (host,port))

    def close(self):
        _log("Closing %s" % str(self.peername()))
        #self._socket.shutdown(2)
        self._socket.close()

    def peername(self):
        return self._socket.getpeername()

    def readLong(self, num=1):
        return self._read(num * _sizeOfLong, 'l', num)

    def readFloat(self, num=1):
        return self._read(num * _sizeOfFloat, 'f', num)

    def sendTextCommand(self, message):
        self._socket.sendall("%s\n" % message)

    def sendBinaryCommand(self, control=None, *floats):
        if control is None:
            format = "<%df" % len(floats)
            vals = floats
        else:
            format = "<b%df" % len(floats)
            vals = (ord(control),) + floats
        cmd = struct.pack(format, *vals)
        _log("sending binary command: %s" % cmd)
        self._socket.sendall(cmd)

    def _read(self, numbytes, format, num):
        data = ''
        while len(data) < numbytes:
            chunk = self._socket.recv(numbytes-len(data))
            if chunk:
                data += chunk
            else:
                raise socket.error("socket connection broken")
        result = struct.unpack("%d%s" % (num,format), data)
        if num == 1:
            result = result[0]
        return result

#=============================================================================

def bound(value, minimum=None, maximum=None):
    if maximum is not None and minimum > maximum:
        minimum,maximum = maximum,minimum
    if minimum is not None:
        value = max(minimum, value)
    if maximum is not None:
        value = min(maximum, value)
    return value

def _log(msg):
    print >> sys.stderr, msg
