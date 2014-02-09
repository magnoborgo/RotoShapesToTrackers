#Boundary Visual Effects - Bake RotoShape Points to Trackers
#Version 1.2
#
#Created by Magno Borgo
#For greeting, bugs, and requests email me at mborgo[at]boundaryvfx.com
#If you like and use the script frequently, please consider a small donation via Paypal to the same email above.
#
#Compatibility: Nuke 6.1 and up (not tested on previous versions)
#
#
#Legal stuff:
#This script is provided "as is," without warranty of any kind, expressed
#or implied. In no event shall the author be held liable for any damages 
#arising in any way from the use of this script.
#
# Usage: This will bake the actual rotoshapes' points positions to trackers on the requested framerange, including transforms on the parent Layers
# Select a rotopaint node and run the script
#
#***********************************************************
#Changelog
#v1.0
#initial release.
#
#v1.1
#modified the script to run better from user interface (in menus/DAG/etc)
#Speed improvements, its now really fast (Thanks to Rafael Perez for the tip)
#Better shape detection and Cancelling the script works better
#v1.2 refined the walker obj detection, now works with all kinds of shapes sources (mocha/etc)


#***********************************************************
import nuke.rotopaint as rp, math

def walker(obj, list):
    for i in obj:
        x = i.getAttributes()  
        if isinstance(i, nuke.rotopaint.Shape):
            list.append([i, obj]) 
        if isinstance(i, nuke.rotopaint.Layer):
            list.append([i, obj])
            rptsw_walker(i, list)
    return list

    
def TransformToMatrix(point, transf, f):
    extramatrix = transf.evaluate(f).getMatrix()
    vector = nuke.math.Vector4(point[0], point[1], 1, 1)
    x = (vector[0] * extramatrix[0]) + (vector[1] * extramatrix[1]) + extramatrix[2] + extramatrix[3]
    y = (vector[0] * extramatrix[4]) + (vector[1] * extramatrix[5]) + extramatrix[6] + extramatrix[7]
    z = (vector[0] * extramatrix[8]) + (vector[1] * extramatrix[9]) + extramatrix[10] + extramatrix[11]
    w = (vector[0] * extramatrix[12]) + (vector[1] * extramatrix[13]) + extramatrix[14] + extramatrix[15]
    vector = nuke.math.Vector4(x, y, z, w)
    vector = vector / w
    return vector
    
  
def TransformLayers(point, Layer, f, rotoRoot, shapeList):
    if Layer == rotoRoot:
        transf = Layer.getTransform()
        newpoint = TransformToMatrix(point, transf, f)

    else:
        transf = Layer.getTransform()
        newpoint = TransformToMatrix(point, transf, f)
        for x in shapeList: 
            if x[0] == Layer:
                newpoint = TransformLayers(newpoint, x[1], f, rotoRoot, shapeList)
    return newpoint

def Roto_to_Trackers():
    rotoNode = nuke.selectedNode()
    if rotoNode.Class() not in ('Roto', 'RotoPaint'):
        if nuke.GUI:
            nuke.message('Unsupported node type. Selected Node must be Roto or RotoPaint')
        raise TypeError, 'Unsupported node type. Selected Node must be Roto or RotoPaint'

    fRange = nuke.FrameRange(nuke.getInput('Inform the Frame Range to bake', '%s-%s' % (nuke.root().firstFrame(), nuke.root().lastFrame())))
    rotoCurve = rotoNode['curves']
    rotoRoot = rotoCurve.rootLayer
    shapeList = []
    shapeList = walker(rotoRoot, shapeList)
    cancel = False
    for shape in shapeList:
        if isinstance(shape[0], nuke.rotopaint.Shape):
            if cancel:
                break
            count = 0
            trkList = []
            positionsList = []
            task = nuke.ProgressTask('Converting Shape(s)\nto Trackers\n')
            
            for points in shape[0]:
                positionsList.append([]) 
  
            for f in fRange:
                trker = 0
                for points in shape[0]:
                    if task.isCancelled():
                        cancel = True
                        break 
                    if cancel:
                        break
                    point = [points.center.getPosition(f)[0], points.center.getPosition(f)[1]]
                    transf = shape[0].getTransform()
                    xy = TransformToMatrix(point, transf, f)
                    xy = TransformLayers(xy, shape[1], f, rotoRoot, shapeList)
                    positionsList[trker].append(xy)
                    trker += 1;
            trker = 0
            for pos in positionsList:
                if task.isCancelled():
                    cancel = True
                    break                
                if cancel:
                    break
                            
                trackNode = nuke.createNode('Tracker3', inpanel=False)
                trackNode.setName("POINT_" + str(trker) + "_" + trackNode.name())
                trackNode["track1"].setAnimated(0)
                trackNode["track1"].setAnimated(1)
                task.setMessage(shape[0].name + '\nBaking point ' + str(trker + 1) + " of " + str(len(positionsList)))
                
                count = 0
                for f in fRange:
                    if task.isCancelled():
                        cancel = True
                        break   
                    task.setProgress(int(((float(f) - fRange.first()) / (fRange.last() - fRange.first())* 100)))
                    a = trackNode["track1"].animations()
                    a[0].setKey(f, pos[count][0])
                    a[1].setKey(f, pos[count][1])
                    count += 1
                trker += 1;

#remove the line below if you are using the script with menu.py (in menus/DAG/etc)
if __name__ == '__main__':
    Roto_to_Trackers()

