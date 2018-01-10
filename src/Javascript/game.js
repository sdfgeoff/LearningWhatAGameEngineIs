function Game(canvas){
    "use strict"
    var self = this
    self.begin = function(canvas, levelname){
        console.log(self)
        var loader = new Game.Resources.Counter(2, self.resources_loaded)
        Game.Data.ship_image = new Game.Resources.Image('Resources/shiptex.png', loader.check)
        Game.Data.level_data = new Game.Resources.Text('Levels/'+levelname+'.json', loader.check)
    }
    self.resources_loaded = function(){
        console.log(Game.Data)
    }
}
Game.Resources = {}
Game.Data = {
    'model_data':#include "../bin/tmp/shiptex.json",
    'ship_frag':#include "Shaders/ship.frag"
}

#include "Javascript/resources.js"


function start(){
    game = new Game()
    levelname = location.search.substring(1)
    console.log(levelname)
    game.begin(document.getElementById("TheCanvas"), levelname)
}

