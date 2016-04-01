"""
Author: Carlos A. Pena-Caballero
SID#20227849
"""

from panda3d.core import *

from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
import math
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
import sys

font = TextNode.getDefaultFont()
focus=NodePath("tilerFocuse")
mouseControl = False
        
class keyTracker(DirectObject):
    """
    Borrowed Class
    """
    def __init__(self):
        DirectObject.__init__(self)
        self.keyMap = {}
        
    def setKey(self, key, value):
        """Records the state of key"""
        self.keyMap[key] = value
    
    def addKey(self,key,name,allowShift=True):
        self.accept(key, self.setKey, [name,True])
        self.accept(key+"-up", self.setKey, [name,False])  
        self.accept(key.upper()+"-up", self.setKey, [name,False])
        
        if allowShift:
            self.addKey("shift-"+key,name,False)
        
        self.keyMap[name]=False

class RoamingRalphDemo(ShowBase, keyTracker):
	def __init__(self):
		# Set up the window, camera, etc.
		ShowBase.__init__(self)
		keyTracker.__init__(self)

		# Set the background color to black
		self.win.setClearColor((0, 0, 0, 1))

		self.title = addTitle("Ralph new and Improved")
		self.inst1 = addInstructions(0.95, "[ESC]: Quit")
		self.inst2 = addInstructions(0.90, "WASD + Mouse (Or arrow Keys)")
		self.inst3 = addInstructions(0.85, "Shift for hyper")

		self.environ = loader.loadModel("models/environment")
		self.environ.reparentTo(render)
		
		# Create the main character, Ralph
		self.ralph = Actor("models/ralph",
						   {"run": "models/ralph-run",
							"walk": "models/ralph-walk"})
		self.ralph.reparentTo(render)
		self.ralph.setPos((0, 0, 0))
		self.ralph.setH(0)

		self.floater = NodePath(PandaNode("floater"))
		self.floater.reparentTo(self.ralph)
		self.floater.setZ(5.0)
		self.floater.setY(12.0)
			
		# Game state variables
		self.isMoving = False

		# Set up the camera
		self.disableMouse()
		camLens=self.camLens
		camLens.setNear(1)

		self.maxDist=100

		camLens.setFar(self.maxDist*20)
		self.cam.node().setLens(camLens)

		self.accept("escape",sys.exit, [0])
		self.addKey("w","forward")
		self.addKey("a","left")
		self.addKey("s","backward")
		self.addKey("d","right")
		self.addKey("arrow_left","turnLeft")
		self.addKey("arrow_right","turnRight")
		self.addKey("arrow_down","turnDown")
		self.addKey("arrow_up","turnUp")
		self.addKey("space","place")

		self.setKey('zoom',0)
		self.accept("wheel_up", self.setKey, ['zoom',1])
		self.accept("wheel_down", self.setKey, ['zoom',-1])

		self.addKey("shift","hyper")

		taskMgr.add(self.move,"moveTask")

		# Create some lighting
		ambientLight = AmbientLight("ambientLight")
		ambientLight.setColor((.3, .3, .3, 1))
		directionalLight = DirectionalLight("directionalLight")
		directionalLight.setDirection((-5, -5, -5))
		directionalLight.setColor((1, 1, 1, 1))
		directionalLight.setSpecularColor((1, 1, 1, 1))
		render.setLight(render.attachNewNode(ambientLight))
		render.setLight(render.attachNewNode(directionalLight))
			
		# Add a light to the scene.
		self.lightpivot = render.attachNewNode("lightpivot")
		self.lightpivot.setPos(self.ralph.getX(),self.ralph.getY(), self.ralph.getZ())
		self.lightpivot.hprInterval(0.9, LPoint3(360, 0, 0)).loop()
		plight = PointLight('plight')
		plight.setColor((1, 1, 1, 1))
		plight.setAttenuation(LVector3(7, 5, 0))
		self.plnp = self.lightpivot.attachNewNode(plight)
		self.plnp.setPos(2, 0, 0)
		self.environ.setLight(self.plnp)

		# skybox
		self.skybox = loader.loadModel("data/models/skybox.egg")
		# make big enough to cover whole terrain, else there'll be problems with the water reflections
		self.skybox.setScale(self.maxDist*3)
		self.skybox.setBin('background', 1)
		self.skybox.setDepthWrite(0)
		self.skybox.setLightOff()
		self.skybox.reparentTo(render)

		self.fog = Fog('distanceFog')
		# Set the initial color of our fog to black.
		self.fog.setColor(1, 1, 1)
		# Set the density/falloff of the fog.  The range is 0-1.
		# The higher the numer, the "bigger" the fog effect.
		self.fog.setExpDensity(.0008)
		render.setFog(self.fog)

		self.cTrav = CollisionTraverser()

		# Create a sphere to denote the light
		self.sphere = loader.loadModel("models/icosphere")
		self.sphere.setScale(1)
		self.sphere.reparentTo(self.plnp)
		self.sphere.setScale(0.5)
		self.sphere.setPos(self.ralph.getX(), self.ralph.getY(), self.ralph.getZ() + 5)
		
		base.disableMouse()
		base.camera.setH(180)
		base.camera.reparentTo(self.ralph)
		self.camDist=20.0
		self.place = False
		

			  
	def move(self, task):

		# Get the time elapsed since last frame. We need this
		# for framerate-independent movement.
		elapsed = globalClock.getDt()
		# move the skybox with the camera
		campos = base.camera.getPos()
		self.skybox.setPos(campos)
		
		self.lightpivot.setPos(self.ralph.getX(),self.ralph.getY(), self.ralph.getZ())
		
		turnRightAmount=self.keyMap["turnRight"]-self.keyMap["turnLeft"]
		turnUpAmmount=self.keyMap["turnUp"]-self.keyMap["turnDown"]

		turnRightAmount*=elapsed*100
		turnUpAmmount*=elapsed*100

		# Use mouse input to turn both Ralph and the Camera 
		if mouseControl and base.mouseWatcherNode.hasMouse(): 
			# get changes in mouse position 
			md = base.win.getPointer(0) 
			x = md.getX() 
			y = md.getY() 
			deltaX = md.getX() - 200 
			deltaY = md.getY() - 200 
			# reset mouse cursor position 
			base.win.movePointer(0, 200, 200) 
			
			turnRightAmount+=0.2* deltaX
			turnUpAmmount-= 0.2 * deltaY 
			
		zoomOut=self.keyMap["zoom"]
		self.camDist=max(min(self.maxDist,self.camDist+zoomOut*elapsed*50+zoomOut*self.camDist*elapsed*.5),.5)
		self.keyMap["zoom"]*=2.7**(-elapsed*4)# Smooth fade out of zoom speed


		self.ralph.setH(self.ralph.getH() - turnRightAmount)
		base.camera.setP(base.camera.getP() + turnUpAmmount)

		# save ralph's initial position so that we can restore it,
		# in case he falls off the map or runs into something.
		startpos = self.ralph.getPos()

		# If a move-key is pressed, move ralph in the specified direction.
		# Adding, subtracting and multiplying booleans (which get a value of 0 or 1)
		# for the keys here.
		forwardMove=self.keyMap["forward"]-.5*self.keyMap["backward"]
		rightMove=.5*(self.keyMap["right"]-self.keyMap["left"])

		# Slow forward when moving diagonal
		forwardMove*=1.0-abs(rightMove)

		# Hyper mode. Prabably just for debug
		speed=1+4*self.keyMap["hyper"]

		rightMove*=speed
		forwardMove*=speed

		self.ralph.setX(self.ralph, -elapsed*25*rightMove)
		self.ralph.setY(self.ralph, -elapsed*25*forwardMove)
		
		if self.keyMap["place"] == 1 and not self.place:
			self.frowney = loader.loadModel("frowney")
			self.frowney.reparentTo(render)
			self.frowney.setPos(self.ralph.getX(),self.ralph.getY(), self.ralph.getZ() + 1)
			self.place = True
		elif self.keyMap["place"] == 0:
			self.place = False
		
		def sign(n):
			if n>=0: return 1
			return -1

		# If ralph is moving, loop the run animation.
		# If he is standing still, stop the animation.
		if rightMove or forwardMove:
			self.ralph.setPlayRate(forwardMove+abs(rightMove)*sign(forwardMove), 'run')
			if self.isMoving is False:
				self.ralph.loop("run")
				
				#self.ralph.loop("walk")
				self.isMoving = True
		else:
			if self.isMoving:
				self.ralph.stop()
				self.ralph.pose("walk",5)
				self.isMoving = False
		if self.ralph.getZ() > 0:
			self.ralph.stop()
			self.ralph.pose("walk",5)
			self.isMoving = False

		# The camera should look in ralph's direction,
		# but it should also try to stay horizontal, so look at
		# a floater which hovers above ralph's head.


		base.camera.setPos(self.floater,0,0,0)
		base.camera.setPos(base.camera,0,-self.camDist,0)

		return Task.cont

		
# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1), font = font,
                        pos=(-1.3, pos), align=TextNode.ALeft, scale = .05)

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1,1,1,1), font = font,
                        pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)
#A simple function to make sure a value is in a given range, -1 to 1 by default
def restrain(i, mn = -1, mx = 1): return min(max(i, mn), mx)

w = RoamingRalphDemo()
base.run()