const fs = require('fs');
var TurndownService = require('turndown')

var file_path = process.argv[2];
var str = fs.readFileSync(file_path,'utf-8');
var turndownService = new TurndownService({emDelimiter:"*"});

turndownService.addRule('img', {
    filter: ['img'],
    replacement: (content, node) => node.outerHTML
})

turndownService.keep(['pre']);
var markdown = turndownService.turndown(str);
console.log(markdown);
