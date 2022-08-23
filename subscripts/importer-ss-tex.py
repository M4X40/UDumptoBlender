########################################################################################
##                                                                                    ##
##   UModel Export to FBX | Modified by M4X4#6494 at Gator Games | discord.gg/gator   ##
##                           Subscript: Texture Conversion                            ##
##                                                                                    ##
########################################################################################

# ==================================================================================== #

##################
##   Settings   ##
##################
workingDir = "D:\\umodel\\Dump\\"
# Change to your dump (DO NOT set inside of UModelExport).
texConvert = True
# Change to true if you want your textures to be converted to a different format.
# NOTE: THIS WILL TAKE TIME DEPENDING ON YOUR DUMP (a small map took around 1.5 minutes)
texExt = "tga"
# Change to your texture extension if your dump uses anything other than Targa for textures.
# NOTE: REQUIRED texConvert TO BE SET TO True.
texExtNew = "png"
# Change to the texture extension you want your textures to become.
# NOTE: REQUIRED texConvert TO BE SET TO True.

#################
##   Imports   ##
#################
# import bpy
# from bpy import *
from PIL import Image
import os

###################
##   Variables   ##
###################

CWD = os.getcwd()
###################
##   Functions   ##
###################

# Main handler
def main():
    # texConvert
    for root, dirs, files in os.walk(workingDir):
            for file in files:
                if(file.endswith(f".{texExt}")):
                    path = os.path.join(root,file)

                    path = path.replace('\\', r'\\')
                    root2 = root.replace('\\', r'\\') + r'\\'
                    base = os.path.splitext(file)[0]

                    print(f'Found texture: {path}')

                    os.chdir(root2)

                    text = Image.open(file)
                    text.save(f'{root2}{base}.{texExtNew}')
                    os.remove(path)

                    print(f'Converted {path} to a .{texExtNew}!')

                    os.chdir(CWD)

###############
##   Start   ##
###############
if __name__ == '__main__':
        main()
