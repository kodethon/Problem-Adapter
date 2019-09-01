const fs = require('fs');
var TurndownService = require('turndown')

var file_path = process.argv[2];
var str = fs.readFileSync(file_path,'binary');
var turndownService = new TurndownService({emDelimiter:"*"});
/*
turndownService.addRule('pre', {
    filter: ['pre'],
    replacement: function(content) {
        return '<pre>' + content + '</pre>'
    }
})
*/
turndownService.keep(['pre']);
var markdown = turndownService.turndown(str);
console.log(markdown);
