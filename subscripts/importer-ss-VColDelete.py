#####################################################################################
##                                                                                 ##
## UDump Export to FBX | Modified by M4X4#6494 at Gator Games | discord.gg/gator   ##
##                         Subscript: Remove Vertex Colors                         ##
##                                                                                 ##
#####################################################################################

# ================================================================================= #

#################
##   Imports   ##
#################
import bpy
import os

###################
##   Functions   ##
###################

# Main data handler
def main():
    bpy.ops.object.select_all(action='SELECT')
    for ob in bpy.context.selected_objects:
        bpy.context.view_layer.objects.active = ob
        while len(ob.data.vertex_colors) > 0:
            bpy.ops.mesh.vertex_color_remove()

###############
##   Start   ##
###############
if __name__ == '__main__':
    main()