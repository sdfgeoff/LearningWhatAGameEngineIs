function Resources(){
    "use strict"
    var self = this

    self._load_counter = 0
    self._load_counter_max = 0

    self.images_to_load = []
    self.images = {}

    self.text_to_load = []
    self.texts = {}

    self.start_load = function(){
        if (self.load_functions.length > 0){
            var funct = self.load_functions.shift()
            funct()
        }
    }

    self.load_resources = function(){
        self._load_counter = 0
        self._load_counter_max = 0
        for (var i=0; i<self.text_to_load.length;i++){
            self._load_counter_max += 1
            var url = self.text_to_load[i]
            var request = new XMLHttpRequest()
            request.addEventListener("load", TextResourceHelper(self, url, request))
            request.open("GET", url)
            request.send()
        }
        
        for (var i=0; i<self.images_to_load.length;i++){
            self._load_counter_max += 1
            var url = self.images_to_load[i]
            var image = new Image()
            self.images[url] = image
            image.onload = function() {
                self._load_counter += 1
                self._check_load_complete()
            }
            image.src = url;
        }
        self._check_load_complete() // In case of zero items
    }

    self._check_load_complete = function(){
        //Checks if the loading of this stage is complete
        if (self._load_counter == self._load_counter_max){
            self.start_load()
        }
        
    }

    self.svg_dom_to_image = function(dom){
        //Converts from svg text into a raster image
        var canvas = document.createElement('canvas')
        //var canvas = document.getElementById("TheCanvas");
        canvas.width = 2048
        canvas.height = 2048
        var context = canvas.getContext('2d')

        var img = document.createElement('img')
        img.innerHTML = dom.innerHTML
        console.log(img, dom)

        
        
    }

    self.text_to_dom = function(text_string){
        var div = document.createElement('div')
        div.innerHTML = text_string
        return div;
    }

    self.load_functions = [
        self.load_resources,
    ]

}

function TextResourceHelper(loader, url, request){
    var self = this
    self.url = url
    self.request = request
    self.loader = loader
    
    self.on_complete = function (e){
        self.loader.texts[self.url] = self.request.responseText
        self.loader._load_counter += 1
        self.loader._check_load_complete()
    }
    return self.on_complete
}