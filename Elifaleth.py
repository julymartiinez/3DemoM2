# Intro to 3d with Panda3d

from direct.showbase.ShowBase import ShowBase

from panda3d.core import LVector3
from panda3d.core import AmbientLight, DirectionalLight

# panda samples extend ShowBase to provide specific application
class TutorialScene(ShowBase):
	def __init__(self):
		# call superclass init (no implicit chaining)
		ShowBase.__init__(self)

		self.pnode = loader.loadModel("models/queen")
		self.pnode.reparentTo(render)
		self.pnode.setPos(0, 5, -1)
		self.pnode.setH(-60)

		self.pnode2 = loader.loadModel("models/pawn")
		self.pnode2.reparentTo(self.pnode)
		self.pnode2.setScale(0.5)
		self.ground = 1.2
		self.pnode2.setPos(1, 0, self.ground)
		self.vz = 0
		self.vx = 0
		self.vy = 0

		############ lighting #############
	 	alight = AmbientLight('alight')
	 	alight.setColor((.7, .3, .3, 1))

	 	self.alnp = render.attachNewNode(alight)
	 	render.setLight(self.alnp)

	 	slight = DirectionalLight('slight')
	 	slight.setColor((1, .5, .5, 1))
	 	slight.setDirection(LVector3(-0.8, 0, 0))

	 	self.slnp = render.attachNewNode(slight)
	 	render.setLight(self.slnp)

		taskMgr.add(self.update, "update")

	def update(self, task):
		dt = globalClock.getDt()

		# rotate
		#self.pnode.setH(self.pnode.getH() + (50 * dt))

		# impulse
		if self.pnode2.getZ() <= self.ground:
			self.vz = 6.0
		else:
			# gravity
			self.vz = self.vz - 20.0 * dt

		# Moving pawn around queen
		if self.pnode2.getX() < 0:
			self.pnode2.setX(self.pnode2.getX() + 1 * dt)
		elif self.pnode2.getX()>=1:
			self.pnode2.setX(self.pnode2.getX() - 1 * dt)

		# integrate position
		print self.pnode2.getX()
		self.pnode2.setY(self.pnode2.getY() - 1 * dt)
		self.pnode2.setZ(self.pnode2.getZ() + self.vz * dt)

		return task.cont

demo = TutorialScene()
demo.run()
