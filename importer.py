#  ╭─────────────────────────────────────────────────────────╮
#  │                   UDump to Blender                      │
#  │                                                         │
#  │ M4X4#6494, zwei#0001 • github.com/M4X40/UModelToBlender │
#  ╰─────────────────────────────────────────────────────────╯

#  ╶─────────────────────────────────────────── #

#  ╭──────────╮
#  │ Settings │
#  ╰──────────╯

DumpDirectory = "C:\\Users\\maxst\\Downloads\\GatorGames\\HW-Maps\\Games\\VentRepair\\Ennard\\Floor1"
DeleteObjects = True
ProcessObjects = True # Shade smooth, Enable backface culling, and delete Vertex Colors
ProcessTextures = True
TextureExtension = ".png"

#  ╶─────────────────────────────────────────── #

Verbose = True
Warning = True
Debug = True

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
    try:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', '--user', '--no-warn-script-location', 'pip',])
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '--user', 'opencv-python==4.5.3.56',])
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', 'wget',])
    
        import cv2
        import wget
    except Exception:
        try:
            shutil.rmtree(f'{os.getenv("APPDATA")}\\Python\\')
            
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', '--user', '--upgrade', 'pip',])
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', '--user', 'opencv-python==4.5.3.56',])
            subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', 'wget',])
            import cv2
            import wget
        except Exception:
            print("Failed to import modules. Continuing without them.")


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

MatCache = []
PSKObjectCache = {}
CWD = os.getcwd()

ORMTextureNames = [
    "OcclusionRoughnessMetallic",
    "ORM",
    "HRM",
    "MTRAO",
    "MRAO",
    "HDR"
]
DiffuseTextureNames = [
    "Diffuse",
    "Albedo",
    "ALB",
    "BaseColor"
]

if not DumpDirectory.endswith("\\"):
    DumpDirectory = DumpDirectory + "\\"

#  ╶─────────────────────────────────────────╴ #

#  ╭───────────╮
#  │ Functions │
#  ╰───────────╯

def removeAll():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    materials = bpy.data.materials
    for material in materials:
        materials.remove(material)
    main()

if Verbose:
    def print_v(msg):
        if Verbose:
            print(msg)

if Warning:
    def print_w(msg):
        if Warning:
            print(msg)

if Debug:
    def print_d(msg):
        if Debug:
            print(f"DEBUG: {msg}")

def importMesh(filePath):
    return pskimport(filePath,bpy.context,bReorientBones=True)

if ProcessObjects:
    def ProcessObject(ob):
        try:
            bpy.context.view_layer.objects.active = ob
            while len(ob.data.vertex_colors) > 0:
                try:
                    bpy.ops.geometry.color_attribute_remove()
                except Exception:
                    bpy.ops.mesh.vertex_color_remove()
            bpy.ops.object.shade_smooth()
            for mat in ob.material_slots:
                mat.material.use_backface_culling = True
        except Exception:
            return

# Fixes NaN Values in mesh
def fixNan(value):
    if(value=="NaN"):
        return 0
    else:
        return value

if ProcessTextures:
    def splitORM(root, file, type):
        fname = ((file.split(".tga"))[0])
        path = os.path.join(root,fname).replace('\\', r'\\')
        base = os.path.splitext(fname)[0]

        img = cv2.imread(f'{path}')

        blue,green,red = cv2.split(img)
        del blue

        name = (base.split(type))[0]

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
        if not os.path.exists(f"{DumpDirectory}Resources\\"):
            for root, dirs, files in os.walk(f"{DumpDirectory}"):
                for file in files:
                    if file.endswith(".mat") or file.endswith(TextureExtension):
                        moveFile(root, file)
                        for i in ORMTextureNames:
                            if i in file:
                                splitORM(f"{DumpDirectory}Resources\\", file, i)
    
    def fixMaterials():
        try:
            bpy.ops.object.select_all(action='SELECT')
            for ob in bpy.context.selected_objects:
                if not len(ob.material_slots) == 0:
                    for mat in ob.material_slots:
                        if mat.name == "WorldGridMaterial" or mat.name == "GRAY":
                            ob_name = ob.name.split(".")[0]
                            jsonFileData = json.loads(open(DumpDirectory+"dump.json","r").read())
                            for ob_data in jsonFileData:
                                if ob_name in ob_data["path"]:
                                    mat_name = ob_data["materialName"]
                                    mat.material = bpy.data.materials.get(mat_name)
                            print_v(f"Fixed {ob.name}'s materials.")
                else:
                    ob_name = ob.name.split(".")[0]
                    jsonFileData = json.loads(open(DumpDirectory+"dump.json","r").read())
                    for ob_data in jsonFileData:
                        if ob_name in ob_data["path"]:
                            mat_name = ob_data["materialName"]
                            bpy.ops.object.material_slot_add(bpy.data.materials.get(mat_name))
            bpy.ops.object.select_all(action='DESELECT')
        except Exception as e:
            print_w(f"[WARN] {e}")

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
        ProcessObject(bpy.context.active_object)
        try:
            obj = ((str(bpy.context.active_object)).split('<bpy_struct, Object(\"')[1]).split('\") at')[0]
        except Exception:
            obj = bpy.context.active_object
        print_v(f"Imported object {obj} | {str(i + 1)}/{str(listLen)}")

    try:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['SM_SkySphere.mo'].select_set(True)
        bpy.ops.object.delete()
        print_v(" --> Found and deleted SkySphere")
    except Exception:
        print_v(f" --> SkySphere Not Found, Trying InvertedSphere.")

    try:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['MOD_InvertedSphere.mo'].select_set(True)
        bpy.ops.object.delete()
        print_v(" --> Found and deleted InvertedSphere")
    except Exception:
        print_v(f" --> InvertedSphere Not Found, Continuing.")

    if ProcessTextures:
        print_v(" --> Starting texture processing")
        findResources()
        print_v(" --> Finished texture processing")

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
                                NextLine = False
                                texPath = (line.split('Diffuse='))[1]
                                for i in ORMTextureNames:
                                    if i in line:
                                        texPath = texPath.split(i)[0]
                                        texlist['Roughness'] = f"{texPath}Roughness"
                                        texlist['Metallic'] = f"{texPath}Metallic"
                                        for d in DiffuseTextureNames:
                                            if os.path.exists(f"{DumpDirectory}Resources\\{texPath}{d}.png"):
                                                texlist['Diffuse'] = f"{texPath}{d}"
                                                NextLine = True
                                    elif "HDR" in i and not NextLine:
                                        texlist["Diffuse"] = texPath
                            elif 'Normal=' in line:
                                texPath = (line.split('Normal='))[1]
                                texlist["Normal"] = texPath
                            elif 'Roughness=' in line:
                                texPath = (line.split('Roughness='))[1]
                                for i in ORMTextureNames:
                                    if i in line:
                                        texPath = (texPath.split(i))[0]
                                        texPath = f"{texPath}Roughness"
                                texlist['Roughness'] = texPath
                            elif 'Metallic=' in line:
                                texPath = (line.split('Metallic='))[1]
                                for i in ORMTextureNames:
                                    if i in line:
                                        texPath = (texPath.split(i))[0]
                                        texPath = f"{texPath}Roughness"
                                texlist['Metallic'] = texPath
                            elif 'Other[0]=' in line:
                                texPath = line.split("Other[0]=")[1]
                                for i in ORMTextureNames:
                                    if i in line:
                                        split = line.split("Other[0]=")[1]
                                        texPath = split.split(i)[0]
                                        texlist['Metallic'] = f"{texPath}Metallic"
                                        texlist['Roughness'] = f"{texPath}Roughness"
                                    elif '_Metallic' in line:
                                        texlist['Metallic'] = texPath
                                    elif '_Roughness' in line:
                                        texlist['Roughness'] = texPath
                            elif 'Other[1]=' in line:
                                for i in ORMTextureNames:
                                    if i in line:
                                        split = line.split("Other[1]=")[1]
                                        texPath = split.split(i)[0]
                                        texlist['Metallic'] = f"{texPath}Metallic"
                                        texlist['Roughness'] = f"{texPath}Roughness"
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
                                    if not str(e) == ('\'Diffuse\''):
                                        print_w(f"[WARN] {e} (Diffuse)")
                                
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
                                    if not str(e) == ('\'Normal\''):
                                        print_w(f"[WARN] {e} (Normal)")
                                
                                try:
                                    if "Roughness" in texlist.keys():
                                        RoughNode = mat_nodes.new('ShaderNodeTexImage')
                                        textPath = DumpDirectory.replace('\\', '/')
                                        RoughNode.image = bpy.data.images.load(filepath = "".join(f"{textPath}Resources/{texlist['Roughness']}.png".split()))
                                        RoughNode.image.colorspace_settings.name = "Non-Color"
                                        RoughNode.location = (-300,0)
                                        mat_links.new(RoughNode.outputs["Color"], mat_nodes.get("Principled BSDF").inputs["Roughness"])
                                except Exception as e:
                                    if not str(e) == ('\'Roughness\''):
                                        print_w(f"[WARN] {e} (Roughness)")
                                
                                try:
                                    if "Metallic" in texlist.keys():
                                        MetalNode = mat_nodes.new('ShaderNodeTexImage')
                                        textPath = DumpDirectory.replace('\\', '/')
                                        MetalNode.image = bpy.data.images.load(filepath = "".join(f"{textPath}Resources/{texlist['Metallic']}.png".split()))
                                        MetalNode.image.colorspace_settings.name = "Non-Color"
                                        MetalNode.location = (-600,200)
                                        mat_links.new(MetalNode.outputs["Color"], mat_nodes.get("Principled BSDF").inputs["Metallic"])
                                except Exception as e:
                                    if not str(e) == ('\'Metallic\''):
                                        print_w(f"[WARN] {e} (Metallic)")

                            MatCache.append(mat.name)
                    del texlist
    fixMaterials()
    print_v(" --> Done!")
#  ╭───────╮
#  │ Start │
#  ╰───────╯
if __name__ == '__main__':
    if DeleteObjects:
        removeAll()
    else:
        main()
