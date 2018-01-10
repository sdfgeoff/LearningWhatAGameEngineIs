Game.Resources.Text = function(url, callback){
    var self = this
    self.request = new XMLHttpRequest()
    self.request.addEventListener("load", callback)
    self.request.open("GET", url)
    self.request.send()
}
Game.Resources.Image = function(url, callback){
    var self = this
    self.image = new Image()
    self.image.onload = callback
    self.image.src = url
}
Game.Resources.Counter = function(num, callback){
    var self = this
    self.target = num
    self.check = function(){
        self.target -= 1
        if (self.target <= 0){
            callback()
        }
    }
}

Game.partial = function(funct, args){
    var self = this
    self.funct = funct
    self.args = args
    self.run = function(more_args){
        self.funct.apply(this, args+more_args)
    }
}