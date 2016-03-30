# Author: Judith Lizette Martinez
# Date: 03/29/2016
#
#
#

from direct.showbase.ShowBase import ShowBase
from sys import exit

# panda samples extend ShowBase to provide specific application
class TutorialScene(ShowBase):

   def __init__(self):
      # call superclass init (no implicit chaining)
      ShowBase.__init__(self)

demo = TutorialScene()
demo.run()