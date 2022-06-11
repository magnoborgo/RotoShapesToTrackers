import nuke
from RotoShapes_to_trackers import *
toolbar = nuke.menu("Nodes")
bvfxt = toolbar.addMenu("BoundaryVFX Tools", "BoundaryVFX.png")
bvfxt.addCommand('Bake Rotoshapes to Trackers',"RotoShape_to_Trackers()", icon='bvfx_RotoT.png')