#####################################################################################
##                                                                                 ##
## UDump Export to FBX | Modified by M4X4#6494 at Gator Games | discord.gg/gator   ##
##                                                                                 ##
#####################################################################################

# ================================================================================= #

##################
##   Settings   ##
##################
deleteAllObjects = True
# Change to false if all objects in collection should be kept upon nunning script. (e.g. Camera, Cube, Light)
workingDir = "D:\\C_Docs\\ResilioSync\\Imports\\UE\\Tools\\udump\\Dump\\"
# Change to your dump (DO NOT set inside of UModelExport).
autoExport = False
# Change to true if you want to automatically export
exportDir =  "C:\\Users\\user\\Documents\\"
# Change to the path you want the file to export to. If file doesn't show up, export manually.
# NOTE: REQUIRED autoExport TO BE SET TO True. INCLUDE \\ AT THE END
scaling = 1
# Change to the scale (XYZ) you need. Only need one number number.

#################
##   Imports   ##
#################
import bpy
from bpy import *
import json
import os
import time
from io_import_scene_unreal_psa_psk_280 import pskimport
from math import *
import json
from random import randint
import threading
from pathlib import Path

###################
##   Functions   ##
###################

# Tied to deleteAllObjects
def removeAll():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    main()

# Main Import Funtion, Used in createObject()
def importMesh(filePath):
    return pskimport(filePath,bpy.context,bReorientBones=True)

# Fixes NaN Values in mesh
def fixNan(value):
    if(value=="NaN"):
        return 0
    else:
        return value

# Actual Import
def createObject(jsonData):
    objectType = jsonData["type"]
    if(objectType=="mesh"):
        path = jsonData["path"]
        path=path.split('.')[0]
        path=workingDir+"UmodelExport"+path
        if(Path(path+".pskx").is_file()):
            path=path+".pskx"
        elif(Path(path+".psk").is_file()):
            path=path+".psk"
        else:
            if path != workingDir+"UmodelExportNone":
                raise ValueError("Can't find mesh file "+path)
        importMesh(path)
        
        imported = bpy.context.active_object
        location = jsonData["position"]
        rotation = jsonData["rotation"]
        scale = jsonData["scale"]
        imported.location = (fixNan(location["X"])/100,fixNan(location["Y"])/100*-1,fixNan(location["Z"]/100))
        imported.rotation_euler = (radians(fixNan(rotation["Z"])),radians(fixNan(rotation["X"])*-1),radians(fixNan(rotation["Y"])*-1))
        imported.scale = (scaling,scaling,scaling)
        
# Main data handler
def main():  
    jsonFileData = json.loads((open(workingDir+"dump.json","r").read())) 
    listLen = len(jsonFileData)
    for i in range(0,listLen):
        createObject(jsonFileData[i])
        print("Imported object "+str(i)+"/"+str(listLen))

    textfile = open(workingDir+"brokenObjects.txt", "w")
    for element in nonImportedObjects:
        textfile.write(element + "\n")
    textfile.close()
    
    try:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['SM_SkySphere.mo'].select_set(True)
        bpy.ops.object.delete()
        print("Found and deleted SkySphere")
    except Exception:
        print(f"SkySphere Not Found, Trying InvertedSphere.")
    
    try:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['MOD_InvertedSphere.mo'].select_set(True)
        bpy.ops.object.delete()
        print("Found and deleted InvertedSphere")
    except Exception:
        print(f"InvertedSphere Not Found, Continuing.")
        
    
    bpy.ops.object.select_all(action='SELECT')
    for ob in bpy.context.selected_objects:
        bpy.context.view_layer.objects.active = ob
        while len(ob.data.vertex_colors) > 0:
            bpy.ops.mesh.vertex_color_remove()
        bpy.ops.object.shade_smooth()
    
    if autoExport == True:
        print("Finished Importing! Attempting Auto Export.")
        export()

# Export Process. Tied to autoExport
def export():
    try:
        os.chdir(exportDir)
        bpy.ops.export_scene.fbx(filepath=f"{exportDir}untitled.fbx", bake_anim=True)
    except Exception as e:
        print(f"Export Failed: \n{e}\n")

###################
##   Variables   ##
###################
successfulObjects = 0
failedObjects = 0
nonImportedObjects = []
pskObjectCache = {}

###############
##   Start   ##
###############
if __name__ == '__main__':
    if deleteAllObjects:
        removeAll()
    else:
        main()