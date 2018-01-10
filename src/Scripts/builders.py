from src.Scripts.trivial_build import File, Empty, depends_on, start_build
import os

BLENDER_COMMAND = 'blender'

def list_folder(folder, endswith=''):
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(endswith)]

class BlenderBase:
    '''This is used to invoke blender with the specified blend_path and script.
    It also handles execution of blender'''
    def __init__(self, blend_path, script, background=True):
        self.command = "{blender} {blend_path} {background} --python {render_script} --python-exit-code 1 -- ".format(
            blender=BLENDER_COMMAND,
            background='-b' if background else '',
            blend_path=blend_path,
            render_script=script,
        )

        depends_on(self, File(blend_path), File(script))

    def __call__(self):
        code = os.system(self.command)
        if code != 0:
            raise Exception("Blender script did not complete sucessfully")
        return True
        

class LevelExporter(BlenderBase):
    '''Exports a level'''
    def __init__(self, blend_path, output_folder):
        super().__init__(blend_path, "./src/Scripts/export_level.py")
        self.command += "--folder {output_folder}".format(
            output_folder=output_folder,
        )


class BlenderRender(BlenderBase):
    def __init__(self, blend_path, output_file, resolution=1.0, opengl=False):
        super().__init__(blend_path, "./src/Scripts/render.py")
        self.command += "--filename {output_file} --resolution {resolution} {opengl}".format(
            output_file=output_file,
            resolution=resolution,
            opengl='--opengl' if opengl else ''
        )

class BlenderTexData(BlenderBase):
    def __init__(self, blend_path, data_file):
        super().__init__(blend_path, "./src/Scripts/export_tex.py")
        self.command += "--filename {data_file}".format(
            data_file=data_file
        )

class ScriptPreprocessor:
    def __init__(self, input_file, output_file, base_path):
        self.input_file = input_file
        self.output_file = output_file
        self.base_path = base_path

        depends_on(self, File(input_file))

    def __call__(self):
        raw = open(self.input_file).read()

        found = get_between(raw, '#include "', '"', include=True)
        while found is not None:
            filename = get_between(raw, '#include "', '"', include=False)
            new_text = open(os.path.join(self.base_path, filename)).read()
            raw = raw.replace(found, new_text)
            found = get_between(raw, '#include "', '"', include=True)
            
        open(self.output_file, 'w').write(raw)
        

def get_between(text, start_text, end_text, index_from=0, include=False):
    '''Searches through text and finds the text between two tags, eg:
    >>> get_between("find [me]", '[', ']')
    "me"
    Good for ghetto parsing in a hurry
    '''
    start_index = text.find(start_text, index_from)
    if start_index == -1:
        return
    end_index = text.find(end_text, start_index + len(start_text))
    if end_index == -1:
        return

    if include:
        return text[start_index:end_index + len(end_text)]
    else:
        return text[start_index + len(start_text):end_index]
