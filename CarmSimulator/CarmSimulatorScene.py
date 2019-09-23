import vtk, qt, ctk, slicer
import os


class CarmSimulatorScene:
    def __init__(self, parent=None):
        self.resourcePath = os.path.dirname(os.path.abspath(__file__))

        self.cModel = None
        self.gantryModel = None
        self.floorModel = None

        # Initialize Transforms
        self.cTransform = None
        self.gantryTransform = None
        self.fluoroDisplayTransform = None
        self.dRRToMonitorTransform = None
        self.spinePlateTransform = None
        self.floorTransform = None
        self.tableZTranslation = None
        self.wagTransform = None
        self.tableTransform = None
        self.sceneTransform = None
        self.lumbarSpineVolume = None

        # self.fovPath = os.path.join(self.resourcePath, 'Resources\FieldOfViewMedium.png')

    def GenerateScene(self):

        # Load in models from resources folder if they are not in the scene already
        try:
            self.cModel = slicer.util.getNode("C")
        except:
            self.cModel = slicer.util.loadModel(os.path.join(self.resourcePath, 'Resources/C.stl'))
            self.cModel.GetDisplayNode().SetColor(0.91, 0.91, 0.91)
        self.cModel.SetSelectable(False)

        try:
            self.gantryModel = slicer.util.getNode("GantryV3")
        except:
            self.gantryModel = slicer.util.loadModel(os.path.join(self.resourcePath, 'Resources/GantryV3.stl'))
            self.gantryModel.GetDisplayNode().SetColor(0.79, 0.79, 0.79)
        self.gantryModel.SetSelectable(False)

        try:
            self.floorModel = slicer.util.getNode("Floor")
        except:
            self.floorModel = slicer.util.loadModel(os.path.join(self.resourcePath, 'Resources/Floor.stl'))
            self.floorModel.GetDisplayNode().SetColor(1, 1, 1)
        self.floorModel.SetSelectable(False)

        try:
            self.fluoroDisplayModel = slicer.util.getNode("FluoroDisplayV2")
        except:
            self.fluoroDisplayModel = slicer.util.loadModel(
                os.path.join(self.resourcePath, 'Resources/FluoroDisplayV2.stl'))
            self.fluoroDisplayModel.GetDisplayNode().SetColor(0.5, 0.5, 0.5)
        self.fluoroDisplayModel.SetSelectable(False)

        try:
            self.surfaceMesh = slicer.util.getNode("SpineSurfaceMesh")
        except:
            self.surfaceMesh = slicer.util.loadModel(
                os.path.join(self.resourcePath, 'Resources/SpineSurfaceMesh.stl'))
            self.surfaceMesh.GetDisplayNode().SetColor(0.7, 0.48, 0.4)
        self.surfaceMesh.SetSelectable(False)

        try:
            self.tableModel = slicer.util.getNode("Stanless steel table")
        except:
            self.tableModel = slicer.util.loadModel(os.path.join(self.resourcePath, 'Resources/Stanless steel table.stl'))
            self.tableModel.GetDisplayNode().SetColor(0.5, 0.5, 0.5)
        self.tableModel.SetSelectable(False)

        try:
            self.supportModel = slicer.util.getNode("Support")
        except:
            self.supportModel = slicer.util.loadModel(os.path.join(self.resourcePath, 'Resources/Support.stl'))
            self.supportModel.GetDisplayNode().SetColor(0.96, 0.96, 0.96)
        self.supportModel.SetSelectable(False)

        # Load in transforms if they are not already in the scene
        try:
            self.cTransform = slicer.util.getNode("CTransform")
        except:
            self.cTransform = slicer.util.loadTransform(
                os.path.join(self.resourcePath, 'Resources/CTransform.h5'))

        try:
            self.gantryTransform = slicer.util.getNode("GantryTransform")
        except:
            self.gantryTransform = slicer.util.loadTransform(
                os.path.join(self.resourcePath, 'Resources/GantryTransform.h5'))

        try:
            self.dRRToMonitorTransform = slicer.util.getNode("DRRToMonitor")
        except:
            self.dRRToMonitorTransform = slicer.util.loadTransform(
                os.path.join(self.resourcePath, 'Resources/DRRToMonitor.h5'))

        try:
            self.floorTransform = slicer.util.getNode("FloorTransform")
        except:
            self.floorTransform = slicer.util.loadTransform(
                os.path.join(self.resourcePath, 'Resources/FloorTransform.h5'))

        try:
            self.fluoroDisplayTransform = slicer.util.getNode("FluoroDisplayTransform")
        except:
            self.fluoroDisplayTransform = slicer.util.loadTransform(
                os.path.join(self.resourcePath, 'Resources/FluoroDisplayTransform.h5'))

        try:
            self.sceneTransform = slicer.util.getNode("SceneTransform")
        except:
            self.sceneTransform = slicer.util.loadTransform(os.path.join(self.resourcePath, 'Resources/SceneTransform.h5'))

        try:
            self.tableTransform = slicer.util.getNode("TableTransform")
        except:
            self.tableTransform = slicer.util.loadTransform(
                os.path.join(self.resourcePath, 'Resources/TableTransform.h5'))

        try:
            self.surfaceMeshTransform = slicer.util.getNode("SurfaceMeshTransform")
        except:
            self.surfaceMeshTransform = slicer.util.loadTransform(
                os.path.join(self.resourcePath, 'Resources/SurfaceMeshTransform.h5'))

        try:
            self.tableZTranslation = slicer.util.getNode("TableZTranslation")
        except:
            self.tableZTranslation = slicer.util.loadTransform(os.path.join(self.resourcePath, 'Resources/TableZTranslation.h5'))

        try:
            self.wagTransform = slicer.util.getNode("WagTransform")
        except:
            self.wagTransform = slicer.util.loadTransform(
                os.path.join(self.resourcePath, 'Resources/WagTransform.h5'))

        # Set up transform hierarchy
        self.cTransform.SetAndObserveTransformNodeID(self.gantryTransform.GetID())
        self.tableTransform.SetAndObserveTransformNodeID(self.sceneTransform.GetID())
        self.surfaceMeshTransform.SetAndObserveTransformNodeID(self.tableZTranslation.GetID())
        self.fluoroDisplayTransform.SetAndObserveTransformNodeID(self.sceneTransform.GetID())
        self.gantryTransform.SetAndObserveTransformNodeID(self.wagTransform.GetID())
        self.dRRToMonitorTransform.SetAndObserveTransformNodeID(self.fluoroDisplayTransform.GetID())
        self.wagTransform.SetAndObserveTransformNodeID(self.sceneTransform.GetID())
        self.floorTransform.SetAndObserveTransformNodeID(self.sceneTransform.GetID())
        self.tableZTranslation.SetAndObserveTransformNodeID(self.tableTransform.GetID())

        self.supportModel.SetAndObserveTransformNodeID(self.wagTransform.GetID())
        self.cModel.SetAndObserveTransformNodeID(self.cTransform.GetID())
        self.floorModel.SetAndObserveTransformNodeID(self.floorTransform.GetID())
        self.fluoroDisplayModel.SetAndObserveTransformNodeID(self.fluoroDisplayTransform.GetID())
        self.gantryModel.SetAndObserveTransformNodeID(self.gantryTransform.GetID())
        self.surfaceMesh.SetAndObserveTransformNodeID(self.surfaceMeshTransform.GetID())
        self.tableModel.SetAndObserveTransformNodeID(self.tableZTranslation.GetID())

        # Load volume and set transfer function if not in scene already
        try:
            self.lumbarSpineVolume = slicer.util.getNode("LumbarSpinePhantom_CT")
        except:
            self.lumbarSpineVolume = slicer.util.loadVolume(
                os.path.join(self.resourcePath, 'Resources\LumbarSpinePhantom_CT.mha'))
            logic = slicer.modules.volumerendering.logic()
            slicer.modules.volumerendering.logic().CreateDefaultVolumeRenderingNodes(self.lumbarSpineVolume)
            volumeProp = logic.AddVolumePropertyFromFile(
                os.path.join(self.resourcePath, 'Resources\VolumeProperty.vp'))
            self.lumbarSpineVolume.GetNthDisplayNode(1).SetAndObserveVolumePropertyNodeID(volumeProp.GetID())
            self.lumbarSpineVolume.SetDisplayVisibility(1)
