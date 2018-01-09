#!/usr/bin/python3
import json
from distutils import dir_util
from src.Scripts import trivial_build as tb
from src.Scripts import builders as bd
import os


D = os.path.dirname(os.path.abspath(__file__))+'/'
OUT = D + 'bin/'
TMP = OUT + 'tmp/'
GAME = OUT + 'game/'
if not os.path.exists(OUT):
    os.mkdir(OUT)
    os.mkdir(TMP)
    os.mkdir(GAME)

ship_texture_image = bd.BlenderRender(D+'src/Blends/ShipTex.blend', GAME+'Resources/shiptex.png')
ship_texture_data = bd.BlenderTexData(D+'src/Blends/ShipTex.blend', TMP+'shiptex.json')

levels_raw = [bd.LevelExporter(l, GAME + 'Levels/') for l in bd.list_folder(D+"src/Levels", ".blend")]
levels = tb.Empty(*levels_raw)

def level_list():
    json.dump({'levels':os.listdir(GAME + 'Levels/')}, open(TMP+'level_list.json', 'w'))
tb.depends_on(level_list, levels)

def html():
    dir_util.copy_tree(D+'src/Html', GAME)
tb.depends_on(html, *[tb.File(f) for f in bd.list_folder('src/Html')])

scripts = bd.ScriptPreprocessor(D+'src/Javascript/game.js', GAME+'game.js', D+'/src')
print(scripts)


def start_test_server():
    import subprocess
    subprocess.Popen(["python3","-m","http.server"])
    import webbrowser
    webbrowser.open_new_tab('0.0.0.0:8000/bin/game')

if __name__ == "__main__":
    tb.start_build(globals())