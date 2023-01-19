#  ╭─────────────────────────────────────────╮
#  │ UDump to Blender                        │
#  │                                         │
#  │ M4X4#6494, zwei#0001 • discord.gg/gator │
#  ╰─────────────────────────────────────────╯

#  ╶─────────────────────────────────────────── #

#  ╭──────────╮
#  │ Settings │
#  ╰──────────╯

DumpDirectory = "C:\\Users\\maxst\\Downloads\\Fnaf99GatorGames-main\\Fnaf99GatorGames-main\\testing-main\\Fnaf99\\bin\\x64\\Debug\\Dump\\"
DeleteObjects = True
ProcessTextures = True
TextureExtension = ".png"

#  ╶─────────────────────────────────────────── #

"""

Print settings. Customize what gets printed to the console

    - Verbose    |   Regular info prints
    - Warning    |   Printed as [WARN]
    - Debug      |   Development purposes, currently unused

"""

Verbose = True
Warning = True
Debug = False

#  ╶─────────────────────────────────────────╴ #

#  ╭─────────╮
#  │ Imports │
#  ╰─────────╯

import os
import bpy
import sys
import json
import shutil
import subprocess
from bpy import *
from math import *
from pathlib import Path

#  ╶─────────────────────────────────────────╴ #

#  ╭────────────────────────────╮
#  │ Get modules if unavailable │
#  ╰────────────────────────────╯

try:   
    import cv2
    import wget
except Exception:
    subprocess.check_call(
        [sys.executable, '-m', 'pip', 'install', '--upgrade', '--user', '--no-warn-script-location', 'pip',])
    subprocess.check_call(
        [sys.executable, '-m', 'pip', 'install', '--user', 'opencv-python==4.5.3.56',])
    subprocess.check_call(
        [sys.executable, '-m', 'pip', 'install', '--upgrade', 'wget',])
    try:
        import cv2
        import wget
    except Exception:
        shutil.rmtree(f'{os.getenv("APPDATA")}\\Python\\')
        
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '--user', '--upgrade', 'pip',])
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '--user', 'opencv-python==4.5.3.56',])
        subprocess.check_call(
        [sys.executable, '-m', 'pip', 'install', '--upgrade', 'wget',])

    
    import cv2
    import wget

BlendPY = f"{os.getcwd()}\\{os.getcwd()[-3:]}\\"

try:
    from io_import_scene_unreal_psa_psk_280 import pskimport
except Exception:
    wget.download('https://raw.githubusercontent.com/Befzz/blender3d_import_psk_psa/master/addons/io_import_scene_unreal_psa_psk_280.py', f'{BlendPY}scripts\\addons\\io_import_scene_unreal_psa_psk_280.py')
    from io_import_scene_unreal_psa_psk_280 import pskimport

#  ╶─────────────────────────────────────────╴ #

#  ╭───────────╮
#  │ Variables │
#  ╰───────────╯

SuccessfulObjects = 0
FailedObjects = 0
NonImportedObjects = []
MatCache = []
PSKObjectCache = {}
CWD = os.getcwd()

#  ╶─────────────────────────────────────────╴ #

#  ╭───────────╮
#  │ Functions │
#  ╰───────────╯

# Tied to DeleteObjects
def removeAll():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    main()

# Print functions, read 22-26.
def print_v(msg):
    if Verbose:
        print(msg)

def print_w(msg):
    if Warning:
        print(msg)

def print_d(msg):
    if Debug:
        print(f"DEBUG: {msg}")

# Main Import Funtion, Used in createObject()
def importMesh(filePath):
    return pskimport(filePath,bpy.context,bReorientBones=True)

# Fixes NaN Values in mesh
def fixNan(value):
    if(value=="NaN"):
        return 0
    else:
        return value

# All texture processing functions
if ProcessTextures:
    def splitORM(root, file):
        fname = ((file.split(".tga"))[0])
        path = os.path.join(root,fname).replace('\\', r'\\')
        base = os.path.splitext(fname)[0]

        img = cv2.imread(f'{path}')

        blue,green,red = cv2.split(img)
        del blue

        if "OcclusionRoughnessMetallic" in file:
            name = (base.split("OcclusionRoughnessMetallic"))[0]
        elif "ORM" in file:
            name = (base.split("ORM"))[0]
        elif "HRM" in file:
            name = (base.split("HRM"))[0]
        elif "MTRAO" in file:
            name = (base.split("MTRAO"))[0]

        cv2.imwrite(f"{root}\\{name}Roughness.png", red)
        cv2.imwrite(f"{root}\\{name}Metallic.png", green)
        os.remove(path)
        
        print_v(f" <-- --> Split {fname} into Roughness and Metallic textures!")

    def moveFile(root, file):
        path = (os.path.join(root,file)).replace('\\', r'\\')
        
        if not os.path.exists(f'{DumpDirectory}\\Resources\\'):
            os.mkdir(f'{DumpDirectory}\\Resources\\')

        dest = f"{DumpDirectory}Resources\\{file}"
        try:
            shutil.copyfile(path, dest)
        except Exception:
            try:
                path = path.replace('\\\\', r'\\')
                path = path.replace('\\\\', r'\\')
                shutil.copyfile(path,dest)
            except Exception as e:
                if not "same file" in str(e):
                    print_w(f'[WARN] --> Error in moving resource to folder: {e}')

    def findResources():
        for root, dirs, files in os.walk(DumpDirectory):
            for file in files:
                if file.endswith(".mat") or file.endswith(TextureExtension):
                    moveFile(root, file)
                    if "OcclusionRoughnessMetallic" in file or "ORM" in file or "HRM" in file or "MTRAO" in file:
                        splitORM(f"{DumpDirectory}Resources\\", file)

def createObject(jsonData):
    objectType = jsonData["type"]
    if(objectType=="mesh"):
        path = DumpDirectory+"UmodelExport"+(jsonData["path"].split('.')[0])

        if(Path(path + ".pskx").is_file()):
            path = path + ".pskx"
        elif(Path(path + ".psk").is_file()):
            path = path + ".psk"
        if path != DumpDirectory+"UmodelExportNone":
            importMesh(path)

            imported = bpy.context.active_object

            location = jsonData["position"]
            rotation = jsonData["rotation"]
            scale = jsonData["scale"]

            imported.location = (fixNan(location["X"])/100,fixNan(location["Y"])/100*-1,fixNan(location["Z"]/100))
            imported.rotation_euler = (radians(fixNan(rotation["Z"])),radians(fixNan(rotation["X"])*-1),radians(fixNan(rotation["Y"])*-1))
            imported.scale = (fixNan(scale["X"]),fixNan(scale["Y"]),fixNan(scale["Z"]))

#  ╶─────────────────────────────────────────╴ #

#  ╭───────────────╮
#  │ Main Function │
#  ╰───────────────╯

def main():
    
    jsonFileData = json.loads((open(DumpDirectory+"dump.json","r").read())) 
    listLen = len(jsonFileData)
    for i in range(0,listLen):
        createObject(jsonFileData[i])
        print_v("Imported object "+str(i)+"/"+str(listLen))

    # Delete SkySphere
    try:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['SM_SkySphere.mo'].select_set(True)
        bpy.ops.object.delete()
        print_v(" --> Found and deleted SkySphere")
    except Exception:
        print_v(f" --> SkySphere Not Found, Trying InvertedSphere.")

    # Delete InvertedSphere
    try:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['MOD_InvertedSphere.mo'].select_set(True)
        bpy.ops.object.delete()
        print_v(" --> Found and deleted InvertedSphere")
    except Exception:
        print_v(f" --> InvertedSphere Not Found, Continuing.")

    # Shade Smooth / Delete VCOLS / Nodes
    print_v(" --> Enabling nodes, shade smoothing, and deleting V-Colors")
    bpy.ops.object.select_all(action='SELECT')
    for ob in bpy.context.selected_objects:
        ob.active_material.use_nodes = True
        bpy.context.view_layer.objects.active = ob
        while len(ob.data.vertex_colors) > 0:
            try:
                bpy.ops.geometry.color_attribute_remove()
            except Exception:
                bpy.ops.mesh.vertex_color_remove()
        bpy.ops.object.shade_smooth()

    #Start Convertion
    if ProcessTextures:
        print_v(" --> Starting texture processing")
        findResources()
        print_v(" --> Finished texture processing")

        # AutoTexture
        print_v(" --> Starting auto-texturing")
        for i in bpy.data.materials:
            mat = (str(i).split('<bpy_struct, Material("')[1]).split('") at ')[0]

        for root, dirs, files in os.walk(f"{DumpDirectory}\\Resources\\"):
            for file in files:
                if file.endswith(".mat"):

                    texlist = {}
                    os.chdir(root)

                    path = (os.path.join(root,file)).replace('\\', r'\\')
                    base = os.path.splitext(file)[0]

                    with open(file) as f:
                        for line in f.readlines():
                            if 'Diffuse=' in line:
                                texPath = (line.split('Diffuse='))[1]
                                if '_Roughness' in line:
                                    texlist['Roughness'] = texPath
                                    texPath = texPath.split("Roughness")[0]
                                    texlist['Diffuse'] = (texPath) + "BaseColor"
                                else:
                                    texlist["Diffuse"] = texPath
                            elif 'Normal=' in line:
                                texPath = (line.split('Normal='))[1]
                                texlist["Normal"] = texPath
                            elif 'Roughness=' in line:
                                texPath = (line.split('Roughness='))[1]
                                if "OcclusionRoughnessMetallic" in texPath:
                                    texPath = (texPath.split("OcclusionRoughnessMetallic"))[0]
                                    texPath = f"{texPath}Roughness"
                                texlist['Roughness'] = texPath
                            elif 'Metallic=' in line:
                                texPath = (line.split('Metallic='))[1]
                                if "OcclusionRoughnessMetallic" in texPath:
                                    texPath = (texPath.split("OcclusionRoughnessMetallic"))[0]
                                    texPath = f"{texPath}Roughness"
                                texlist['Metallic'] = texPath
                            elif 'Other[0]=' in line:
                                texPath1 = line.split("Other[0]=")[1]
                                if 'OcclusionRoughnessMetallic' in line:
                                    texPath = texPath1.split("OcclusionRoughness")
                                    texPath = texPath[0] + texPath[1]
                                    texlist['Metallic'] = texPath
                                    texPath = texPath1.split("Occlusion")[0] + "Roughness"
                                    texlist['Roughness'] = texPath
                                elif '_Metallic' in line:
                                    texlist['Metallic'] = texPath
                                elif '_Roughness' in line:
                                    texlist['Roughness'] = texPath
                            elif 'Other[1]=' in line:
                                if 'OcclusionRoughnessMetallic' in line:
                                    split = line.split("Other[1]=")[1]
                                    texPath = split.split("OcclusionRoughness")
                                    texPath = texPath[0] + texPath[1]
                                    texlist['Metallic'] = texPath
                                    texPath = split.split("Occlusion")[0] + "Roughness"
                                    texlist['Roughness'] = texPath
                                elif '_Metallic' in line:
                                    texPath = line.split("Other[1]=")[1]
                                    texlist['Metallic'] = texPath
                                elif '_Roughness' in line:
                                    texPath = line.split("Other[1]=")[1]
                                    texlist['Roughness'] = texPath

                    for mat in bpy.data.materials:
                        if mat.name == base:
                            global MatCache
                            if mat.name not in MatCache:
                                mat.use_nodes = True
                                mat_nodes = mat.node_tree.nodes
                                mat_links = mat.node_tree.links
                                
                                try:
                                    ColorNode = mat_nodes.new('ShaderNodeTexImage')
                                    textPath = DumpDirectory.replace('\\', '/')
                                    ColorNode.image = bpy.data.images.load(filepath = "".join(f"{textPath}Resources/{texlist['Diffuse']}.png".split()))
                                    ColorNode.location = (-400,500)
                                    mat_links.new(ColorNode.outputs["Color"], mat_nodes.get("Principled BSDF").inputs["Base Color"])
                                except Exception as e:
                                    print_w(f"[WARN] {e}")
                                
                                try:
                                    NormalMap = mat_nodes.new("ShaderNodeNormalMap")
                                    NormalNode = mat_nodes.new('ShaderNodeTexImage')
                                    textPath = DumpDirectory.replace('\\', '/')
                                    NormalNode.image = bpy.data.images.load(filepath = "".join(f"{textPath}Resources/{texlist['Normal']}.png".split()))
                                    NormalNode.image.colorspace_settings.name = "Non-Color"
                                    NormalNode.location = (-475,-375)
                                    NormalMap.location = (-175,-275)
                                    mat_links.new(NormalNode.outputs["Color"], NormalMap.inputs["Color"])
                                    mat_links.new(NormalMap.outputs["Normal"], mat_nodes.get("Principled BSDF").inputs["Normal"])
                                except Exception as e:
                                    print_w(f"[WARN] {e}")
                                
                                try:
                                    if "Roughness" in texlist.keys():
                                        RoughNode = mat_nodes.new('ShaderNodeTexImage')
                                        textPath = DumpDirectory.replace('\\', '/')
                                        RoughNode.image = bpy.data.images.load(filepath = "".join(f"{textPath}Resources/{texlist['Roughness']}.png".split()))
                                        RoughNode.image.colorspace_settings.name = "Non-Color"
                                        RoughNode.location = (-300,0)
                                        mat_links.new(RoughNode.outputs["Color"], mat_nodes.get("Principled BSDF").inputs["Roughness"])
                                except Exception as e:
                                    print_w(f"[WARN] {e}")
                                
                                try:
                                    if "Metallic" in texlist.keys():
                                        MetalNode = mat_nodes.new('ShaderNodeTexImage')
                                        textPath = DumpDirectory.replace('\\', '/')
                                        MetalNode.image = bpy.data.images.load(filepath = "".join(f"{textPath}Resources/{texlist['Metallic']}.png".split()))
                                        MetalNode.image.colorspace_settings.name = "Non-Color"
                                        MetalNode.location = (-600,200)
                                        mat_links.new(MetalNode.outputs["Color"], mat_nodes.get("Principled BSDF").inputs["Metallic"])
                                except Exception as e:
                                    print_w(f"[WARN] {e}")

                            MatCache.append(mat.name)
                    del texlist
    print_v(" --> Done!")
#  ╭───────╮
#  │ Start │
#  ╰───────╯
if __name__ == '__main__':
    if DeleteObjects:
        removeAll()
    else:
        main()
