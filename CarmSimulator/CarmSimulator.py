import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import copy


#
# Carm Simulator
#

class CarmSimulator(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "CarmSimulator"  # TODO make this more human readable by adding spaces
        self.parent.categories = ["Examples"]
        self.parent.dependencies = []
        self.parent.contributors = [
            "Daniel Allen(Western University)"]  # replace with "Firstname Lastname (Organization)"
        self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
        self.parent.helpText += self.getDefaultModuleDocumentationLink()
        self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""  # replace with organization, grant and thanks.


#
# HelloPythoWidget
#

class CarmSimulatorWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        ScriptedLoadableModuleWidget.__init__(self,parent)
        slicer.mymod = self


    @vtk.calldata_type(vtk.VTK_INT)
    def updateTransforms(self, caller, event, calldata):
        if calldata == 1:
            self.xRotationSliderWidget.value += 1
            self.logic.UpdateCRotation(self.xRotationSliderWidget.value)
        elif calldata == 2:
            self.xRotationSliderWidget.value -= 1
            self.logic.UpdateCRotation(self.xRotationSliderWidget.value)
        elif calldata == 3:
            self.zRotationSliderWidget.value += 1
            self.logic.UpdateGantryRotation(self.zRotationSliderWidget.value)
        elif calldata == 4:
            self.zRotationSliderWidget.value -= 1
            self.logic.UpdateGantryRotation(self.zRotationSliderWidget.value)

    @vtk.calldata_type(vtk.VTK_OBJECT)
    def interactorCallback(self, caller, event, calldata):
        matr = calldata
        #print(matr)
        trackpadPositionX = matr.GetElement(0,0)
        trackpadPositionY = matr.GetElement(0,1)
        device = matr.GetElement(0,2)
        input = matr.GetElement(0,3)
        action = matr.GetElement(1,0)
        #print("Input")  # 0 for trigger 1 for trackpad
        #print(input)
        #print("Action") # 2.0 for pressed 3.0 for released
        #print(action)

        # Do Nothing unless we receive a release event from the trigger
        if input == 0:
            if action == 3:
                if device == 1:
                    self.logic.ToggleDRR(True)
                    self.logic.UpdateDRR()
                    self.logic.ToggleDRR(False)
                elif device == 2:
                    self.logic.CollectImage(True)
            return


        if trackpadPositionX == 0:
            self.direction = 0
            return

        # Set C-arm Movement Direction
        if device == 1:
            if trackpadPositionX > 0:
                if trackpadPositionY > 0:
                    self.direction = 1
                else:
                    self.direction = 2
            else:
                if trackpadPositionY > 0:
                    self.direction = 3
                else:
                    self.direction = 4
        elif device == 2:
            if trackpadPositionX > 0:
                if trackpadPositionY > 0:
                    self.direction = 5
                else:
                    self.direction = 6
            else:
                if trackpadPositionY > 0:
                    self.direction = 7
                else:
                    self.direction = 8


    def processOneThing(self):
        #if self.movement:
        #print(direction)
        if self.direction == 1:
            self.xRotationSliderWidget.value += 1
            self.logic.UpdateCRotation(self.xRotationSliderWidget.value)
        elif self.direction == 2:
            self.xRotationSliderWidget.value -= 1
            self.logic.UpdateCRotation(self.xRotationSliderWidget.value)
        elif self.direction == 3:
            self.zRotationSliderWidget.value += 1
            self.logic.UpdateGantryRotation(self.zRotationSliderWidget.value)
        elif self.direction == 4:
            self.zRotationSliderWidget.value -= 1
            self.logic.UpdateGantryRotation(self.zRotationSliderWidget.value)
        elif self.direction == 5:
            self.wagRotationSliderWidget.value += 1
            self.logic.UpdateWagRotation(self.wagRotationSliderWidget.value)
        elif self.direction == 6:
            self.wagRotationSliderWidget.value -= 1
            self.logic.UpdateWagRotation(self.wagRotationSliderWidget.value)
        elif self.direction == 7:
            self.tableSliderWidget.value += 1
            self.logic.UpdateTable(self.tableSliderWidget.value)
        elif self.direction == 8:
            self.tableSliderWidget.value -= 1
            self.logic.UpdateTable(self.tableSliderWidget.value)



    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        # Instantiate and connect widgets ...
        #
        # Parameters Area
        #
        parametersCollapsibleButton = ctk.ctkCollapsibleButton()
        parametersCollapsibleButton.text = "Parameters"
        self.layout.addWidget(parametersCollapsibleButton)

        # Layout within the dummy collapsible button
        parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

        # Generate Scene Button
        self.generateSceneButton = qt.QPushButton('Generate Scene')
        self.generateSceneButton.connect('clicked(bool)', self.onGenerateSceneButtonClicked)
        #self.generateSceneButton.setDisabled(True)
        parametersFormLayout.addRow(self.generateSceneButton)

        # Toggle DRR Button
        self.toggleDRRButton = qt.QCheckBox()
        self.toggleDRRButton.connect('toggled(bool)', self.onToggleDRRButtonClicked)
        parametersFormLayout.addRow("Toggle DRR", self.toggleDRRButton)

        # Toggle VR Button - TO DO
        self.toggleVRButton = qt.QCheckBox()
        self.toggleVRButton.connect('toggled(bool)', self.onToggleVRButtonClicked)
        parametersFormLayout.addRow("Toggle VR", self.toggleVRButton)

        # Transfer Function Presets
        self.fluoroButton = qt.QRadioButton()
        # parametersFormLayout.addRow("Fluoro", self.fluoroButton)

        # Field of View Slider
        self.fieldOfViewSlider = ctk.ctkSliderWidget()
        self.fieldOfViewSlider.singleStep = 0.1
        self.fieldOfViewSlider.minimum = 0
        self.fieldOfViewSlider.maximum = 60
        self.fieldOfViewSlider.setToolTip("Increase/Decrease Field of View.")
        self.fieldOfViewSlider.connect('valueChanged(double)', self.onFieldOfViewValueChanged)
        parametersFormLayout.addRow("Field Of View", self.fieldOfViewSlider)

        # Zoom Slider
        self.zoomSlider = ctk.ctkSliderWidget()
        self.zoomSlider.singleStep = 0.1
        self.zoomSlider.minimum = 0
        self.zoomSlider.maximum = 50
        self.zoomSlider.value = 0
        self.zoomSlider.setToolTip("Zoom Factor")
        self.zoomSlider.connect('valueChanged(double)', self.onZoomValueChanged)
        parametersFormLayout.addRow("Zoom", self.zoomSlider)

        # C Rotation
        self.xRotationSliderWidget = ctk.ctkSliderWidget()
        self.xRotationSliderWidget.singleStep = 0.1
        self.xRotationSliderWidget.minimum = 0
        self.xRotationSliderWidget.maximum = 90
        self.xRotationSliderWidget.value = 0.0
        self.xRotationSliderWidget.setToolTip("C Rotation about the Z axis.")
        self.xRotationSliderWidget.connect('valueChanged(double)', self.onCRotationValuesChanged)
        parametersFormLayout.addRow("C Rotation", self.xRotationSliderWidget)

        # Gantry Rotation
        self.zRotationSliderWidget = ctk.ctkSliderWidget()
        self.zRotationSliderWidget.singleStep = 0.1
        self.zRotationSliderWidget.minimum = -55
        self.zRotationSliderWidget.maximum = 55
        self.zRotationSliderWidget.value = 0.0
        self.zRotationSliderWidget.setToolTip("Gantry Rotation about the X axis.")
        self.zRotationSliderWidget.connect('valueChanged(double)', self.onGantryRotationValuesChanged)
        parametersFormLayout.addRow("Gantry Rotation", self.zRotationSliderWidget)

        # Wag Rotation
        self.wagRotationSliderWidget = ctk.ctkSliderWidget()
        self.wagRotationSliderWidget.singleStep = 0.1
        self.wagRotationSliderWidget.minimum = -40
        self.wagRotationSliderWidget.maximum = 40
        self.wagRotationSliderWidget.value = 0.0
        self.wagRotationSliderWidget.setToolTip("Wag Rotation about the Y axis.")
        self.wagRotationSliderWidget.connect('valueChanged(double)', self.onWagRotationValuesChanged)
        parametersFormLayout.addRow("Wag Rotation", self.wagRotationSliderWidget)

        self.tableSliderWidget = ctk.ctkSliderWidget()
        self.tableSliderWidget.singleStep = 0.1
        self.tableSliderWidget.minimum = -55
        self.tableSliderWidget.maximum = 55
        self.tableSliderWidget.value = 0.0
        self.tableSliderWidget.setToolTip("Table Translation.")
        self.tableSliderWidget.connect('valueChanged(double)', self.onTableValuesChanged)
        parametersFormLayout.addRow("Table Translation", self.tableSliderWidget)

        # Start Module Button
        self.startModuleButton = qt.QPushButton('Start Module')
        self.startModuleButton.connect('clicked(bool)', self.onStartModuleButtonClicked)
        parametersFormLayout.addRow(self.startModuleButton)

        self.collectImageButton = qt.QPushButton('Collect Image')
        # Generate Scene Button
        self.collectImageButton.connect('clicked(bool)', self.onCollectImageButtonClicked)
        # self.generateSceneButton.setDisabled(True)
        parametersFormLayout.addRow(self.collectImageButton)

        # Needle Slider
        #self.needleSliderWidget = ctk.ctkSliderWidget()
        #self.needleSliderWidget.singleStep = 0.1
        #self.needleSliderWidget.minimum = -55
        #self.needleSliderWidget.maximum = 55
        #self.needleSliderWidget.value = 0.0
        #self.needleSliderWidget.setToolTip("Needle Translation.")
        #self.needleSliderWidget.connect('valueChanged(double)', self.onNeedleValuesChanged)
        #parametersFormLayout.addRow("Needle Translation", self.needleSliderWidget)

        # Create Logic Instance
        self.logic = CarmSimulatorLogic()

        #self.interactorObserver = slicer.modules.virtualReality

        self.vrInteractorObserver = 0
        self.gestureObserverNum = 0
        self.vrInteractor = None

        # Grab gesturerecognition logic instance so we can observe for events
        #self.gestureObserver = slicer.modules.gesturerecognition.logic()
        #self.useGestureRecognition = True
        #self.gestureObserverNum = 0
        #if not self.gestureObserver:
        #    self.useGestureRecognition = False

        #self.useGestureRecognition = False
        self.timer = qt.QTimer()
        self.elapsed = qt.QElapsedTimer()
        self.timerIteration = 0
        self.movement = 1
        self.direction = 0
        self.timer.connect('timeout()', self.processOneThing)
        #self.timer.setInterval(30)
        self.timer.start()



        # Add vertical Spacer
        self.layout.addStretch(1)



    def onCRotationValuesChanged(self, value):
        self.logic.UpdateCRotation(value)

    def onGantryRotationValuesChanged(self, value):
        self.logic.UpdateGantryRotation(value)

    def onWagRotationValuesChanged(self, value):
        self.logic.UpdateWagRotation(value)

    def onToggleDRRButtonClicked(self, value):
        self.logic.ToggleDRR(value)

    def onToggleVRButtonClicked(self, value):

        w = None
        for i in slicer.app.topLevelWidgets():
            if i.name == "VirtualRealityWidget":
                w = i

        if w is None:
            print("Could not connect to VR")
            return

        self.vrInteractor = w.renderWindow().GetInteractor()
        self.vrInteractorObserver = self.vrInteractor.AddObserver(123456, self.interactorCallback)

    def onGenerateSceneButtonClicked(self, value):
        #if self.useGestureRecognition == True:
            #if self.gestureObserverNum != 0:
                #self.gestureObserver.RemoveObserver(self.gestureObserverNum)
            #self.gestureObserverNum = self.gestureObserver.AddObserver(self.gestureObserver.GestureRecognizedEvent, self.updateTransforms)
        self.logic.GenerateScene(value)

    def onCollectImageButtonClicked(self, value):


    def onNeedleValuesChanged(self, value):
        self.logic.UpdateNeedle(value)

    def onTableValuesChanged(self, value):
        self.logic.UpdateTable(value)

    def onFieldOfViewValueChanged(self, value):
        self.logic.ChangeFOV(value)

    def onZoomValueChanged(self, value):
        self.logic.ChangeZoomFactor(value)

    def cleanup(self):
        #if self.gestureObserverNum is not 0:
        #    self.gestureObserver.RemoveObserver(self.gestureObserverNum)

        if self.vrInteractor is not None:
            self.vrInteractor.RemoveObserver(self.vrInteractorObserver)


        print("HELLO")
        # Cleanup any memory leaks
        self.logic.cleanup()
        pass


#
# HelloPythoLogic
#

class CarmSimulatorLogic(ScriptedLoadableModuleLogic):

    def __init__(self, parent = None):
        ScriptedLoadableModuleLogic.__init__(self, parent)
        self.resourcePath = os.path.dirname(os.path.abspath(__file__))
        self.slicerRenderer = slicer.app.layoutManager().threeDWidget(0).threeDView().renderWindow().GetRenderers().GetFirstRenderer()
        slicer.mymod = self

    def Initialize(self):

        # Get Volume from mrml Scene
        self.volume = self.slicerRenderer.GetVolumes().GetItemAsObject(0)

        # Set up FOV and dummy renderer
        self.renderer = vtk.vtkRenderer()
        self.rendererFOV = vtk.vtkRenderer()
        self.pngReader = vtk.vtkPNGReader()
        self.imageViewer = vtk.vtkImageViewer2()
        self.fovPath = os.path.join(self.resourcePath, 'Resources\FieldOfViewMedium.png')
        self.DRRToMonitorTransformNode = slicer.mrmlScene.GetNodesByName("DRRToMonitor").GetItemAsObject(0)
        self.pngReader.SetFileName(self.fovPath)
        self.pngReader.Update()
        self.imageViewer.SetInputConnection(self.pngReader.GetOutputPort())
        self.imageViewer.SetRenderer(self.rendererFOV)
        self.renderer.AddVolume(self.volume)
        self.renderWindow = vtk.vtkRenderWindow()
        self.renderWindow.SetNumberOfLayers(2)
        self.renderWindow.AddRenderer(self.renderer)
        self.renderWindow.AddRenderer(self.rendererFOV)
        # self.rendererFOV.ResetCamera()
        self.rendererFOV.GetActiveCamera().SetPosition(750.0, 750.0, 700)
        self.rendererFOV.GetActiveCamera().SetFocalPoint(750.0, 750.0, 0.0)
        self.renderer.SetLayer(0)
        self.rendererFOV.SetLayer(1)
        self.renderWindow.SetSize(530, 335)
        # self.ChangeFOV(0)
        self.renderWindow.SetOffScreenRendering(1)

        # Add Needle
        #self.needle = vtk.vtkCylinderSource()
        #self.needle.SetRadius(0.5)
        #self.needle.SetHeight(100)
        #self.needleMapper = vtk.vtkPolyDataMapper()
        #self.needleMapper.SetInputConnection(self.needle.GetOutputPort())
        #self.needleMapper.Update()
        #self.needleActor = vtk.vtkActor()
        #self.needleActor.SetMapper(self.needleMapper)
        #self.needleActor.GetProperty().SetColor(0.3, 0.3, 0.3)
        #self.renderer.AddActor(self.needleActor)

        # Initialize Carm Transforms
        self.cRotation = vtk.vtkTransform()
        self.gantryRotation = vtk.vtkTransform()
        self.wagRotation = vtk.vtkTransform()
        self.tableTranslationTransform = vtk.vtkTransform()
        self.focalPointTransform = vtk.vtkTransform()
        self.xRotationValue = 0.0
        self.zRotationValue = 0.0
        self.yRotationValue = 0.0
        self.tableTranslationValue = 0.0
        self.zoomFactor = 0.0
        self.DRRInitialized = False
        self.toggleDRR = False
        self.planeModelNode = None

    def GenerateScene(self, value):
        # Load in models from resources folder if they are not in the scene already

        self.cModel = slicer.mrmlScene.GetNodesByName("C").GetItemAsObject(0)
        if self.cModel is None:
            self.cModel = slicer.util.loadModel(os.path.join(self.resourcePath, 'Resources/C.stl'))
            self.cModel.GetDisplayNode().SetColor(0.91, 0.91, 0.91)

        self.floorModel = slicer.mrmlScene.GetNodesByName("Floor").GetItemAsObject(0)
        if self.floorModel is None:
            self.floorModel = slicer.util.loadModel(os.path.join(self.resourcePath, 'Resources/Floor.stl'))
            self.floorModel.GetDisplayNode().SetColor(1, 1, 1)

        self.fluoroDisplayModel = slicer.mrmlScene.GetNodesByName("FluoroDisplayV2").GetItemAsObject(0)
        if self.fluoroDisplayModel is None:
            self.fluoroDisplayModel = slicer.util.loadModel(os.path.join(self.resourcePath, 'Resources/FluoroDisplayV2.stl'))
            self.fluoroDisplayModel.GetDisplayNode().SetColor(0.5, 0.5, 0.5)

        self.gantryModel = slicer.mrmlScene.GetNodesByName("GantryV3").GetItemAsObject(0)
        if self.gantryModel is None:
            self.gantryModel = slicer.util.loadModel(os.path.join(self.resourcePath, 'Resources/GantryV3.stl'))
            self.gantryModel.GetDisplayNode().SetColor(0.79, 0.79, 0.79)

        self.spinePlateModel = slicer.mrmlScene.GetNodesByName("SpinePlate").GetItemAsObject(0)
        if self.spinePlateModel is None:
            self.spinePlateModel = slicer.util.loadModel(os.path.join(self.resourcePath, 'Resources/SpinePlate.stl'))
            self.spinePlateModel.GetDisplayNode().SetColor(1, 0, 0)

        self.tableModel = slicer.mrmlScene.GetNodesByName("Stanless steel table").GetItemAsObject(0)
        if self.tableModel is None:
            self.tableModel = slicer.util.loadModel(os.path.join(self.resourcePath, 'Resources/Stanless steel table.stl'))
            self.tableModel.GetDisplayNode().SetColor(0.5, 0.5, 0.5)

        self.supportModel = slicer.mrmlScene.GetNodesByName("Support").GetItemAsObject(0)
        if self.supportModel is None:
            self.supportModel = slicer.util.loadModel(os.path.join(self.resourcePath, 'Resources/Support.stl'))
            self.supportModel.GetDisplayNode().SetColor(0.96, 0.96, 0.96)


        # Load in transforms if they are not already in the scene
        self.cTransform = slicer.mrmlScene.GetNodesByName("CTransform").GetItemAsObject(0)
        if self.cTransform is None:
            self.cTransform = slicer.util.loadTransform(os.path.join(self.resourcePath, 'Resources/CTransform.h5'))

        self.gantryTransform = slicer.mrmlScene.GetNodesByName("GantryTransform").GetItemAsObject(0)
        if self.gantryTransform is None:
            self.gantryTransform = slicer.util.loadTransform(os.path.join(self.resourcePath, 'Resources/GantryTransform.h5'))

        self.dRRToMonitorTransform = slicer.mrmlScene.GetNodesByName("DRRToMonitor").GetItemAsObject(0)
        if self.dRRToMonitorTransform is None:
            self.dRRToMonitorTransform = slicer.util.loadTransform(os.path.join(self.resourcePath, 'Resources/DRRToMonitor.h5'))

        self.floorTransform = slicer.mrmlScene.GetNodesByName("FloorTransform").GetItemAsObject(0)
        if self.floorTransform is None:
            self.floorTransform = slicer.util.loadTransform(os.path.join(self.resourcePath, 'Resources/FloorTransform.h5'))

        self.fluoroDisplayTransform = slicer.mrmlScene.GetNodesByName("FluoroDisplayTransform").GetItemAsObject(0)
        if self.fluoroDisplayTransform is None:
            self.fluoroDisplayTransform = slicer.util.loadTransform(os.path.join(self.resourcePath, 'Resources/FluoroDisplayTransform.h5'))

        self.sceneTransform = slicer.mrmlScene.GetNodesByName("SceneTransform").GetItemAsObject(0)
        if self.sceneTransform is None:
            self.sceneTransform = slicer.util.loadTransform(os.path.join(self.resourcePath, 'Resources/SceneTransform2.h5'))
        self.sceneTransform.SetSelectable(False)

        self.tableTransform = slicer.mrmlScene.GetNodesByName("TableTransform").GetItemAsObject(0)
        if self.tableTransform is None:
            self.tableTransform = slicer.util.loadTransform(os.path.join(self.resourcePath, 'Resources/TableTransform.h5'))

        self.spinePlateTransform = slicer.mrmlScene.GetNodesByName("SpinePlateTransform").GetItemAsObject(0)
        if self.spinePlateTransform is None:
            self.spinePlateTransform = slicer.util.loadTransform(os.path.join(self.resourcePath, 'Resources/SpinePlateTransform.h5'))

        self.tableZTranslation = slicer.mrmlScene.GetNodesByName("TableZTranslation").GetItemAsObject(0)
        if self.tableZTranslation is None:
            self.tableZTranslation = slicer.util.loadTransform(os.path.join(self.resourcePath, 'Resources/TableZTranslation.h5'))

        self.wagTransform = slicer.mrmlScene.GetNodesByName("WagTransform").GetItemAsObject(0)
        if self.wagTransform is None:
            self.wagTransform = slicer.util.loadTransform(os.path.join(self.resourcePath, 'Resources/WagTransform.h5'))


        # Set up transform hierarchy
        self.cTransform.SetAndObserveTransformNodeID(self.gantryTransform.GetID())
        self.tableTransform.SetAndObserveTransformNodeID(self.sceneTransform.GetID())
        self.spinePlateTransform.SetAndObserveTransformNodeID(self.tableZTranslation.GetID())
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
        self.spinePlateModel.SetAndObserveTransformNodeID(self.spinePlateTransform.GetID())
        self.tableModel.SetAndObserveTransformNodeID(self.tableZTranslation.GetID())

        # Load volume and set transfer function if not in scene already
        self.lumbarSpineVolume = slicer.mrmlScene.GetNodesByName("LumbarSpinePhantom_CT").GetItemAsObject(0)
        if self.lumbarSpineVolume is None:
            self.lumbarSpineVolume = slicer.util.loadVolume(os.path.join(self.resourcePath, 'Resources\LumbarSpinePhantom_CT.mha'))
            self.logic = slicer.modules.volumerendering.logic()
            slicer.modules.volumerendering.logic().CreateDefaultVolumeRenderingNodes(self.lumbarSpineVolume)
            asd1 = self.logic.AddVolumePropertyFromFile(os.path.join(self.resourcePath, 'Resources\VolumeProperty.vp'))
            self.lumbarSpineVolume.GetNthDisplayNode(1).SetAndObserveVolumePropertyNodeID(asd1.GetID())
            self.lumbarSpineVolume.SetDisplayVisibility(1)
        #logic.UpdateDisplayNodeFromVolumeNode(self.lumbarSpineVolume.GetDisplayNode(), self.lumbarSpineVolume)

        #self.lumbarSpineVolume.SetAndObserveTransformNodeID(self.tableTransform.GetID())


        self.Initialize()
        self.slicerRenderer.ResetCamera()
        self.slicerRenderer.Render()


    def UpdateNeedle(self, value):
        self.needleActor.SetPosition(value, 0, 0)
        if self.toggleDRR == True:
            self.slicerRenderer.Render()
            self.UpdateDRR()
            # self.UpdateCRotation(self.zRotationValue)


    def ChangeZoomFactor(self, value):
        self.zoomFactor = value
        if self.toggleDRR == True:
            self.slicerRenderer.Render()
            self.UpdateDRR()

    def ChangeFOV(self, value):
        if self.toggleDRR == False:
            return
        self.rendererFOV.GetActiveCamera().SetPosition(750.0, 750.0, 700 - value * 10)
        self.rendererFOV.GetActiveCamera().SetFocalPoint(750.0, 750.0, 0.0)
        self.slicerRenderer.Render()
        self.UpdateDRR()
        # self.UpdateCRotation(self.zRotationValue)

    def ToggleDRR(self, value):

        if self.DRRInitialized == True:
            if value == True:
                self.image.VisibilityOn()
                self.toggleDRR = True
                self.slicerRenderer.Render()
                return
            self.image.VisibilityOff()
            self.toggleDRR = False
            self.slicerRenderer.Render()
            return

        self.DRRInitialized = True
        self.toggleDRR = True

        # Initialize Window To Input Pipeline
        self.cameraTransform = vtk.vtkTransform()
        self.xRotationValue = 0.0
        self.zRotationValue = 0.0
        self.winToImage = vtk.vtkWindowToImageFilter()
        self.pixelData = vtk.vtkImageData()
        self.winToImage.SetInput(self.renderWindow)
        self.imageMapper = vtk.vtkImageSliceMapper()
        self.image = vtk.vtkImageSlice()
        self.imageMapper.SetInputData(self.winToImage.GetOutput())
        self.image.SetMapper(self.imageMapper)

        # Render DRR (replace with udpate DRR)
        self.cameraTransform.Identity()
        self.cameraTransform.PostMultiply()
        self.cameraTransform.Translate(0, -250, 0)
        self.cameraTransform.RotateX(self.xRotationValue)
        self.cameraTransform.RotateY(0.0)
        self.cameraTransform.RotateZ(-self.zRotationValue)
        self.renderer.GetActiveCamera().SetPosition(self.cameraTransform.GetPosition())
        self.renderer.GetActiveCamera().SetFocalPoint(0, 0, 0)
        self.renderer.GetActiveCamera().SetViewUp(0, 0, 1)
        self.renderer.SetBackground(1, 1, 1)
        self.renderWindow.Render()

        # Initialize Window To Image Pipeline
        self.winToImage = vtk.vtkWindowToImageFilter()
        self.winToImage.SetInput(self.renderWindow)
        self.winToImage.Update()

        # Add DRR Image to Scene using vtkPlaneSource
        self.plane = vtk.vtkPlaneSource()
        self.texture = vtk.vtkTexture()
        self.texture.SetInputConnection(self.winToImage.GetOutputPort())
        self.texture.Update()
        self.plane.SetPoint1(0, 530, 0)
        self.plane.SetPoint2(335, 0, 0)
        self.plane.SetOrigin(0, 0, 0)
        self.plane.Update()

        # Create DRR Model Node
        self.planeModelNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode')
        self.planeModelNode.CreateDefaultDisplayNodes()
        self.planeModelNode.CreateDefaultStorageNode()
        self.planeModelNode.SetAndObservePolyData(self.plane.GetOutput())

        self.planeModelNode.SetAndObserveTransformNodeID(self.DRRToMonitorTransformNode.GetID())
        self.planeModelDisplay = self.planeModelNode.GetDisplayNode()
        self.planeModelDisplay.SetTextureImageDataConnection(self.winToImage.GetOutputPort())
        self.planeModelDisplay.VisibilityOn()

        self.planeModelDisplay.SetFrontfaceCulling(False)
        self.planeModelDisplay.SetBackfaceCulling(False)

        self.renderWindow.Render()
        self.slicerRenderer.Render()

    def UpdateDRR(self):
        # Position Dummy Renderer Camera
        self.cameraTransform.Identity()
        self.cameraTransform.PostMultiply()
        self.cameraTransform.Translate(0, -250 + self.zoomFactor * 4, 0)
        self.cameraTransform.RotateX(self.xRotationValue)
        self.cameraTransform.RotateZ(-self.zRotationValue)

        self.cameraTransform.Translate(200, 0, 0)
        #self.cameraTransform.Translate(-1262.2704, -337.5527, 5.7)
        self.cameraTransform.RotateY(-self.yRotationValue)
        self.cameraTransform.Translate(-200, 0, 0)
        self.cameraTransform.Translate(0,0,self.tableTranslationValue)
        #self.cameraTransform.Translate(1262.2704, 337.5527, -5.7)


        self.focalPointTransform.Identity()
        self.focalPointTransform.Translate(200, 0, 0)
        self.focalPointTransform.RotateY(self.yRotationValue)
        self.focalPointTransform.Translate(-200, 0, 0)
        self.focalPointTransform.Translate(0,0,self.tableTranslationValue)
        zAxis = [0,0,0,0]
        up = [0,0,1,0]
        self.cameraTransform.MultiplyPoint(up, zAxis)


        self.renderer.GetActiveCamera().SetPosition(self.cameraTransform.GetPosition())
        self.renderer.GetActiveCamera().SetFocalPoint(self.focalPointTransform.GetPosition())
        self.renderer.GetActiveCamera().SetViewUp(zAxis[0], zAxis[1], zAxis[2])
        #self.renderer.GetActiveCamera().SetViewUp(0,0,1)
        #self.renderer.GetActiveCamera().SetFocalPoint(0,0,0)

        # Update WinToImage Filter and Render
        self.winToImage.Modified()
        self.renderWindow.Render()
        self.winToImage.Update()
        self.imageMapper.Update()
        self.renderer.Render()

        # Update C Rotation

    def UpdateCRotation(self, value):
        self.zRotationValue = value
        self.cRotation.Identity()
        self.cRotation.PostMultiply()
        self.cRotation.Translate(-1262.2704, -337.5527, 5.7)
        self.cRotation.RotateZ(value)
        self.cRotation.Translate(1262.2704, 337.5527, -5.7)
        self.cTransform.SetMatrixTransformToParent(self.cRotation.GetMatrix())
        if self.toggleDRR == True:
            self.UpdateDRR()

        # Update Gantry Rotation

    def UpdateGantryRotation(self, value):
        self.xRotationValue = value
        self.gantryRotation.Identity()
        self.gantryRotation.RotateX(value)
        self.gantryTransform.SetMatrixTransformToParent(self.gantryRotation.GetMatrix())
        if self.toggleDRR == True:
            self.UpdateDRR()

    def UpdateWagRotation(self, value):
        self.yRotationValue = value
        self.wagRotation.Identity()
        self.wagRotation.RotateY(value)
        self.wagTransform.SetMatrixTransformToParent(self.wagRotation.GetMatrix())
        if self.toggleDRR == True:
            self.UpdateDRR()

    def UpdateTable(self, value):
        self.tableTranslationValue = value
        self.tableTranslationTransform.Identity()
        self.tableTranslationTransform.Translate(0,4*self.tableTranslationValue,0)
        self.tableZTranslation.SetMatrixTransformToParent(self.tableTranslationTransform.GetMatrix())
        if self.toggleDRR == True:
            self.UpdateDRR()

    def StartModule(self, value):
        print("TEST")

    def CollectImage(self, value):
        print("TEST2")

    def cleanup(self):
        try:
            slicer.mrmlScene.RemoveNode(self.planeModelNode)
        except:
            print("DRR Model has not been initialized")

        del self.winToImage

class CarmSimulatorTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        # slicer.mrmlScene.Clear(0)

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_CarmSimulator()

    def test_CarmSimulator(self):
        self.delayDisplay("Starting the test")
        logic = CarmSimulatorLogic()
        result = "Need To Implement"
        self.assertIsNotNone(result)
        self.delayDisplay('Test passed!')
