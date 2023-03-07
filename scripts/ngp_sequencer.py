import time
import os
import numpy as np
from collections import deque
class SequenceCommand:
    def ExecuteCommand(self,testbed,sequencer):
        return True

class CameraMovementCommand(SequenceCommand):
    def __init__(self,posA:np.array,posB:np.array,t:float,startTime):
        self.posA = posA
        self.posB = posB
        self.startTime = startTime
        self.t = t
        print("\nstarttime cam move command: " + str(startTime))
        self.endTime = float(startTime) + t
        print("\nendTime cam move command: " + str(self.endTime))
        self.isComplete = False

    def ExecuteCommand(self, testbed, sequencer):
        print("\nExecute Command")
        sequencer._AddCameraMovementCommand(self)
        return True

class Sequencer:
    def __init__(self):
        self.startTime = 0.0
        self.isStarted = False
        self.isCompleted = False
        self.currentTime = 0.0
        self.currentCommand = SequenceCommand()
        self.commandQueue = deque()
        self.cameraMovementCommand = None
        self.cameraMovementCommandQueue = deque()

    def StartSequencer(self):
        self.isStarted = True
        self.startTime = time.perf_counter()


    def Tick(self,testbed):
        if(self.isStarted and not self.isCompleted):
            self.currentTime = time.perf_counter() - self.startTime
            if(self.currentCommand.ExecuteCommand(testbed,self)):
                if(type(self.currentCommand) is CameraMovementCommand):
                    self.currentCommand = SequenceCommand()
                if(len(self.commandQueue) > 0):
                    self.currentCommand = self.commandQueue.popleft()
                elif(len(self.cameraMovementCommandQueue) <= 0 
                     and self.cameraMovementCommand == None):
                    print("\nCompleted queue")
                    self.isCompleted = True
                    
        
            if(self.cameraMovementCommand != None):
                self.cameraMovementCommand.ExecuteCommand(testbed,self)
                if(self.cameraMovementCommand.isComplete):
                    if(len(self.cameraMovementCommandQueue) >0):
                        self.cameraMovementCommand = self.cameraMovementCommandQueue.popleft()
                    else:
                        self.cameraMovementCommand = None

                    
        else:
            return 

            #print("\nSequence Timer: %s",str(self.currentTime))

    #todo - fix bug with time not being cumulative
    def AddWaitCommand(self,time:float):
        """Adds a command that halts execution until defined time has passed (in seconds)"""
        print("\nAdd Wait Command")
        self.commandQueue.append(WaitCommand(time))

    def AddSceneTransitionCommand(self,scene:str):
        print("\nAdd Scene Transition Command")
        self.commandQueue.append(SceneTransitionCommand(scene))

    def AddSetSceneScaleCommand(self,scale:float):
        self.commandQueue.append(SetSceneScaleCommand(scale))

    #moves camera from posA to posB (in nerf space) over t seconds
    def AddCameraMovementCommand(self,posA:np.array,posB:np.array,t:float):
        self.commandQueue.append(CameraMovementCommand(posA,posB,t,self.currentTime))

    #internal - do not use
    def _AddCameraMovementCommand(self,_camMoveCommand):
        if(len(self.cameraMovementCommandQueue) != 0):
            self.cameraMovementCommandQueue.append(_CameraMovementCommand(
                _camMoveCommand.posA,_camMoveCommand.posB,_camMoveCommand.t,self.currentTime))
        else:
            self.cameraMovementCommand = _CameraMovementCommand(
                _camMoveCommand.posA,_camMoveCommand.posB,_camMoveCommand.t,self.currentTime)
    
    
    def AddLambdaCommand(self,func:callable):
        self.commandQueue.append(LambdaCommand(func))


#internal - do not use
class _CameraMovementCommand(SequenceCommand):
    def __init__(self,posA:np.array,posB:np.array,t:float,startTime):
        self.posA = posA
        self.posB = posB
        self.startTime = startTime
        self.endTime = float(startTime) + t
        print("\nendTime: " + str(self.endTime))
        self.isComplete = False

    #sets camera at current interpolated position
    def ExecuteCommand(self, testbed, sequencer):
        t = float(sequencer.currentTime) / float(self.endTime)
        if(t >= 1.0):
            t = 1.0
            self.isComplete = True
        interpVec = (1 - t)*self.posA + t*self.posB
        testbed.set_camera_position_from_nerf_space(interpVec)
        


class WaitCommand(SequenceCommand):
    def __init__(self,time:float):
        self.time = time
        self.startTime = 0.0
        self.isStarted = False

    def ExecuteCommand(self,testbed,sequencer):
        if(not self.isStarted):
            self.startTime = sequencer.currentTime
            self.isStarted = True
        if(sequencer.currentTime >= self.startTime + self.time):
            print("\nFinished wait command at: " + str(sequencer.currentTime))
            return True
        return False
    
class SceneTransitionCommand(SequenceCommand):
    def __init__(self,scene:str):
        self.scene = scene
    
    def ExecuteCommand(self, testbed, sequencer):
        print("loading scene: " + self.scene)
        msgpackPath = str(self.scene) + "\\base.ingp"
        testbed.load_file(self.scene)

        if(os.path.exists(msgpackPath)):
            testbed.load_snapshot(msgpackPath)
        return True
    
class SetSceneScaleCommand(SequenceCommand):

    def __init__(self,scale:float):
        self.scale = scale

    def ExecuteCommand(self, testbed, sequencer):
        testbed.scale = self.scale
        return True
    
class LambdaCommand(SequenceCommand):
    def __init__(self, func:callable):
        self.function = func
        
    def ExecuteCommand(self, testbed, sequencer):
        if(callable(self.function)):
            self.function()
            return True
        return False
    

