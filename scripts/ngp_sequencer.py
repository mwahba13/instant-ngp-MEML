import time
import os
from collections import deque

class Sequencer:
    def __init__(self):
        self.startTime = 0.0
        self.isStarted = False
        self.isCompleted = False
        self.currentTime = 0.0
        self.currentCommand = SequenceCommand()
        self.commandQueue = deque()

    def StartSequencer(self):
        self.isStarted = True
        self.startTime = time.perf_counter()


    def Tick(self,testbed):
        if(self.isStarted and not self.isCompleted):
            self.currentTime = time.perf_counter() - self.startTime
            if(self.currentCommand.ExecuteCommand(testbed,self)):
                if(len(self.commandQueue) > 0):
                    self.currentCommand = self.commandQueue.popleft()
                else:
                    print("Completed queue")
                    self.isCompleted = True
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
    
    def AddLambdaCommand(self,func:callable):
        self.commandQueue.append(LambdaCommand(func))

class SequenceCommand:
    def ExecuteCommand(self,testbed,sequencer):
        return True


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
    

