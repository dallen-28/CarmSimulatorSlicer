import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# Carm Simulator
#

class CarmSimulator(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "CarmSimulator" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["Daniel Allen(Western University)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# HelloPythoWidget
#

class CarmSimulatorWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """   
    
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
    
    # Toggle DRR Button 
    self.toggleDRRButton = qt.QCheckBox()
    self.toggleDRRButton.connect('toggled(bool)', self.onToggleDRRButtonClicked)
    parametersFormLayout.addRow("Toggle DRR", self.toggleDRRButton)
    
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
	
	# Needle Slider
    self.needleSliderWidget = ctk.ctkSliderWidget()
    self.needleSliderWidget.singleStep = 0.1
    self.needleSliderWidget.minimum = -55
    self.needleSliderWidget.maximum = 55
    self.needleSliderWidget.value = 0.0
    self.needleSliderWidget.setToolTip("Needle Translation.")
    self.needleSliderWidget.connect('valueChanged(double)', self.onNeedleValuesChanged)
    parametersFormLayout.addRow("Needle Translation", self.needleSliderWidget)
    
    # Create Logic Instance
    self.logic = CarmSimulatorLogic()
    
    # Add vertical Spacer
    self.layout.addStretch(1)
    
  def onCRotationValuesChanged(self, value):
    self.logic.UpdateCRotation(value)
    
  def onGantryRotationValuesChanged(self, value):
    self.logic.UpdateGantryRotation(value)
  
  def onToggleDRRButtonClicked(self, value):
    self.logic.ToggleDRR(value)
  def onNeedleValuesChanged(self, value):
    self.logic.UpdateNeedle(value)
  
  def cleanup(self):
    pass

#
# HelloPythoLogic
#

class CarmSimulatorLogic(ScriptedLoadableModuleLogic):
  
  def __init__(self):
    self.Initialize()
    
  def Initialize(self):
    # Get Volume from mrml Scene
    self.slicerRenderer = slicer.app.layoutManager().threeDWidget(0).threeDView().renderWindow().GetRenderers().GetFirstRenderer()
    self.volume = self.slicerRenderer.GetVolumes().GetItemAsObject(0)

    # Set up dummy render window
    self.renderer = vtk.vtkRenderer()
    self.renderWindow = vtk.vtkRenderWindow()
    self.renderWindow.AddRenderer(self.renderer)
    tran = vtk.vtkTransform()
    tran.Identity()
    tran.Translate(-67.799774*2, -67.799774*2, -109.199636*2)
    self.volume.SetUserTransform(tran)
    self.renderer.AddVolume(self.volume)
    #self.renderWindow.SetOffScreenRendering(1)
	
	# Add Needle
    self.needle = vtk.vtkCylinderSource()
    self.needle.SetRadius(0.5)
    self.needle.SetHeight(100)
    self.needleMapper = vtk.vtkPolyDataMapper()
    self.needleMapper.SetInputConnection(self.needle.GetOutputPort())
    self.needleMapper.Update()
    self.needleActor = vtk.vtkActor()
    self.needleActor.SetMapper(self.needleMapper)
    self.needleActor.GetProperty().SetColor(0.3,0.3,0.3)
    self.renderer.AddActor(self.needleActor)
     
    # Initialize Carm Transforms
    self.cRotation = vtk.vtkTransform()
    self.gantryRotation = vtk.vtkTransform()
    self.cTransformNode = slicer.mrmlScene.GetNodesByName("CTransform").GetItemAsObject(0)
    self.gantryTransformNode = slicer.mrmlScene.GetNodesByName("GantryTransform").GetItemAsObject(0)
    self.xRotationValue = 0.0
    self.zRotationValue = 0.0
    self.DRRInitialized = False
    self.toggleDRR = False

  def UpdateNeedle(self, value):
    self.needleActor.SetPosition(value, 0, 0)
    if self.toggleDRR == True:
      self.UpdateDRR()

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
    
    # Render DRR
    self.cameraTransform.Identity()
    self.cameraTransform.PostMultiply()
    self.cameraTransform.Translate(0,-400,0)
    self.cameraTransform.RotateX(self.xRotationValue)  
    self.cameraTransform.RotateY(0.0)
    self.cameraTransform.RotateZ(-self.zRotationValue)
    self.renderer.GetActiveCamera().SetPosition(self.cameraTransform.GetPosition())
    self.renderer.GetActiveCamera().SetFocalPoint(0,0,0)
    self.renderer.GetActiveCamera().SetViewUp(0,0,1)
    self.renderer.SetBackground(1,1,1)
    self.renderWindow.Render()

	
	# Initialize Window To Image Pipeline
    self.winToImage = vtk.vtkWindowToImageFilter()
    self.winToImage.SetInput(self.renderWindow)
    self.imageMapper.SetInputConnection(self.winToImage.GetOutputPort())
    self.winToImage.Update()
    self.imageMapper.Update()
    self.image.SetMapper(self.imageMapper)
    self.image.Update()
	
	# Add DRR Image to Scene
    tran = vtk.vtkTransform()
    tran.Identity()
    tran.Translate(2125.160,605.795,-340.272)
    self.image.SetUserTransform(tran)
    self.slicerRenderer.AddViewProp(self.image)
    self.renderWindow.Render()
    self.slicerRenderer.Render()
    
    
  def UpdateDRR(self):
	# Position Dummy Renderer Camera
    self.cameraTransform.Identity()
    self.cameraTransform.PostMultiply()
    self.cameraTransform.Translate(0,-400,0)
    self.cameraTransform.RotateX(self.xRotationValue)  
    self.cameraTransform.RotateY(0.0)
    self.cameraTransform.RotateZ(-self.zRotationValue)
    self.renderer.GetActiveCamera().SetPosition(self.cameraTransform.GetPosition())
    self.renderer.GetActiveCamera().SetFocalPoint(0,0,0)
    self.renderer.GetActiveCamera().SetViewUp(0,0,1)
	
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
    self.cRotation.Translate(-1262.2704,-337.5527,5.7)
    self.cRotation.RotateZ(value)
    self.cRotation.Translate(1262.2704,337.5527,-5.7)   
    self.cTransformNode.SetMatrixTransformToParent(self.cRotation.GetMatrix())
    if self.toggleDRR == True:
      self.UpdateDRR()
    
    # Update Gantry Rotation
  def UpdateGantryRotation(self, value):
    self.xRotationValue = value
    self.gantryRotation.Identity()
    self.gantryRotation.RotateX(value)
    self.gantryTransformNode.SetMatrixTransformToParent(self.gantryRotation.GetMatrix())
    if self.toggleDRR == True:
      self.UpdateDRR()


class CarmSimulatorTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    #slicer.mrmlScene.Clear(0)


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
