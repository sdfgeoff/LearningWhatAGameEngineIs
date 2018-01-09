
LEVEL = '/Levels/TestLevel.svg'

function Game(canvas){
    "use strict"
    var self = this
    
    self.canvas = canvas
    self.canvas.width = window.innerWidth
    self.canvas.height = window.innerHeight

    self.resources = new Resources()
    self.resources.images_to_load.push('ship.png')
    
    self.level = Level(self.resources, LEVEL)

    self.loaded = function(){
        //self.context = self.canvas.getContext('2d')
        //self.context.drawImage(self.resources.text[LEVEL], 0, 0)
    }

    /* Add a the start game function as the funal function to be run before
     * starting the game */
    self.resources.load_functions.push(self.loaded)
    self.resources.start_load()

}

function Level(resources, level_url){
    "use strict"
    /* Loads the level from the specified url */
    self.resources = resources
    self.url = level_url
    //self.resources.text_to_load.push(self.url)
    self.resources.images_to_load.push(self.url)

    self.process_level = function (){
        console.log(self.resources.images[self.url].innerHTML)
        // Run in the load stage and prepares the level for playing
        /*self.level_dom = self.resources.text_to_dom(self.resources.texts[LEVEL])
        var image_dom = self.resources.text_to_dom(self.resources.texts[LEVEL])
        var layers = image_dom.getElementsByTagName('g')
        var to_remove = []
        for (var i=0; i<layers.length; i++){
            var layer = layers[i]
            var layer_name = layer.getAttribute('inkscape:label')
            if (['PHYSICS', 'META', 'SPAWNS'].indexOf(layer_name) >= 0){
                to_remove.push(layer)
            }
        }
        for (var i=0; i<to_remove.length; i++){
            layer = to_remove[i]
            layer_name = layer.getAttribute('inkscape:label')
            console.log("Removing Layer", layer_name, "from level graphics")
            layer.remove()
        }

        self.level_texture = self.resources.svg_dom_to_image(image_dom)*/
        
    }

    
    self.resources.load_functions.push(self.process_level)
}

function start(){
    game = new Game(document.getElementById("TheCanvas"))
}

