import os
import shutil
import sys
import subprocess
from concurrent.futures import ProcessPoolExecutor as PPE

try:   
    import cv2
    from PIL import Image
except Exception:
    subprocess.check_call(
        [sys.executable, '-m', 'pip', 'install', '--upgrade', '--user', '--no-warn-script-location', 'pip',])
    subprocess.check_call(
        [sys.executable, '-m', 'pip', 'install', '--user', 'opencv-python',])
    subprocess.check_call(
        [sys.executable, '-m', 'pip', 'install', '--upgrade', 'wget',])
    try:
        import cv2
    except Exception:
        shutil.rmtree(f'{os.getenv("APPDATA")}\\Python\\')
        
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '--user', '--upgrade', 'pip',])
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '--user', 'opencv-python',])
        subprocess.check_call(
        [sys.executable, '-m', 'pip', 'install', '--upgrade', 'wget',])

    subprocess.check_call(
        [sys.executable, '-m', 'pip', 'install', '--user', '--upgrade', 'Pillow',])
    
    import cv2
    from PIL import Image

# ARGUMENTS
DD = sys.argv[0]   #DumpDirectory
OTE = sys.argv[1]  #OldTextureExtension
NTE = sys.argv[2]  #NewTextureExtension

CWD = os.getcwd()


def convert(NTE, root, file):
    path = (os.path.join(root,file)).replace('\\', r'\\')
    root2 = root.replace('\\', r'\\') + r'\\'
    base = os.path.splitext(file)[0]

    os.chdir(root2)

    text = Image.open(file)
    text.save(f'{root2}{base}.{NTE}')
    os.remove(path)

    print(f' --> <-- Converted {file}!')

    os.chdir(CWD)

def moveTex(DD, root, file):
    path = (os.path.join(root,file)).replace('\\', r'\\')
    
    dest = f"{DD}Textures\\{file}"
    try:
        shutil.copyfile(path, dest)
    except Exception:
        try:
            path = path.replace('\\\\', r'\\')
            shutil.copyfile(path,dest)
        except Exception as e:
            print(f'[ERR] --> Error in moving textures to folder: {e}')

def splitORM(root, file):
    fname = ((file.split(".tga"))[0]) + ".png"
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

    cv2.imwrite(f"{root}{name}Roughness.png", red)
    cv2.imwrite(f"{root}{name}Metallic.png", green)
    os.remove(path)
    
    print(f" <-- --> Split {fname} into Roughness and Metallic textures!")

def main(DD, OTE, NTE):
    with PPE() as executor:
        for root, dirs, files in os.walk(DD):
            for file in files:
                if(file.endswith(f".{OTE}")):
                    executor.submit(moveTex, DD, root, file)
                if "Textures\\" in root:
                    executor.submit(convert, NTE, root, file)
                    if "OcclusionRoughnessMetallic" in file or "ORM" in file or "HRM" in file or "MTRAO" in file:
                        splitORM(root, file)

if __name__ == '__main__':
    main()
