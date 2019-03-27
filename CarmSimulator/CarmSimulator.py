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
    
	# Field of View Slider
    self.fieldOfViewSlider = ctk.ctkSliderWidget()
    self.fieldOfViewSlider.singleStep = 0.1
    self.fieldOfViewSlider.minimum = 0
    self.fieldOfViewSlider.maximum = 100
    self.fieldOfViewSlider.setToolTip("Increase/Decrease Field of View.")
    self.fieldOfViewSlider.connect('valueChanged(double)', self.onFieldOfViewValueChanged)
    parametersFormLayout.addRow("Field of View", self.fieldOfViewSlider)
	
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
  def onFieldOfViewValueChanged(self, value):
    self.logic.ChangeFOV(value)
  
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
    self.rendererFOV = vtk.vtkRenderer()
    self.renderWindow.AddRenderer(self.renderer)
    self.renderWindow.SetNumberOfLayers(2)
    self.renderWindow.AddRenderer(self.renderer)
    self.renderWindow.AddRenderer(self.rendererFOV)
    self.renderer.SetLayer(0)
    self.rendererFOV.SetLayer(1)
    self.renderer.AddVolume(self.volume)
    self.renderWindow.SetSize(530,335)
    #self.renderWindow.SetOffScreenRendering(1)
    self.imageFOV = vtk.vtkImageSlice()
    self.imageMapper = vtk.vtkImageSliceMapper()
    self.fieldOfViewSize = 50
    self.pngReader = vtk.vtkPNGReader()
    #self.pngReader.SetFileName("Resources\\FieldOfViewSmallTest.png")
    self.pngReader.SetFileName("C:/users/dallen/Documents/C-arm Simulator/DRR/FieldOfView2.png")
    self.pngReader.Update()
    self.imageMapper.SetInputConnection(self.pngReader.GetOutputPort())
    self.imageMapper.Update()
    self.imageFOV.SetMapper(self.imageMapper)
    self.rendererFOV.AddViewProp(self.imageFOV)
    self.imageFOV.ForceTranslucentOn()
    #self.rendererFOV.GetActiveCamera().SetPosition(3750,3750,20000)
    #self.rendererFOV.GetActiveCamera().SetFocalPoint(3750,3750,0)
    self.rendererFOV.ResetCamera()
    self.imageFOV.SetPosition(0,0,1000)
    print self.rendererFOV.GetActiveCamera().GetPosition()
    print self.rendererFOV.GetActiveCamera().GetFocalPoint()
	
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
      #self.UpdateDRR()
      self.UpdateCRotation(self.zRotationValue)
	  
  def ChangeFOV(self, value):
    #self.fieldOfViewSize = value
    pos1 = self.rendererFOV.GetActiveCamera().GetPosition()
    foc1 = self.rendererFOV.GetActiveCamera().GetFocalPoint()
    print pos1
    print value
    self.rendererFOV.GetActiveCamera().SetPosition(pos1[0], pos1[1], pos1[2] - value)
    self.rendererFOV.GetActiveCamera().SetFocalPoint(foc1[0], foc1[1], foc1[2])
    #self.rendererFOV.GetActiveCamera().SetFocalPoint(-3750,-3750,0)
    self.UpdateCRotation(self.zRotationValue)

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
    self.cameraTransform.Translate(0,-250,0)
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
    #tran.Translate(2125.160,605.795,-340.272)
    tran.Translate(2000.150,590.795,-340.272)
    self.image.SetUserTransform(tran)
    self.slicerRenderer.AddViewProp(self.image)
    self.renderWindow.Render()
    self.slicerRenderer.Render()
    #iren = vtk.vtkRenderWindowInteractor()
    #self.renderWindow.SetInteractor(iren)
    #iren.Initialize()
    #iren.Start()
    
    
  def UpdateDRR(self):
	# Position Dummy Renderer Camera
    self.cameraTransform.Identity()
    self.cameraTransform.PostMultiply()
    self.cameraTransform.Translate(0,-250,0)
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
