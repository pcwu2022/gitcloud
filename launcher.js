const fs = require('fs');
const path = require('path');

// Function to recursively find all files
function getAllFiles(dirPath, filesList = []) {
    const items = fs.readdirSync(dirPath); // Read the contents of the directory

    items.forEach((item) => {
        const fullPath = path.join(dirPath, item);
        const stat = fs.statSync(fullPath); // Get file or directory stats

        if (stat.isDirectory()) {
            // Recursively get files from subdirectories
            getAllFiles(fullPath, filesList);
        } else {
            // Add file path to the list
            filesList.push(fullPath);
        }
    });

    return filesList;
}

// Start directory
const startDir = './shared';

// Get the list of all files
const allFiles = getAllFiles(startDir);

// traverse all files
let dirs = {};
for (let file of allFiles){
    filename = file.replaceAll("\\", "/");
    let filePath = filename.split("/");
    let current = dirs;
    while (filePath.length > 1){
        if (!current[filePath[0]]){
            current[filePath[0]] = {};
        }
        current = current[filePath[0]];
        filePath.shift();
    }
    if (!current.__files__){
        current.__files__ = []
    }
    current.__files__.push(filePath[0])
}

const HTMLTemplate = [`
<!DOCTYPE html>
<html lang="en-us">
    <head>
        <meta charset="utf-8">
        <title>Git Cloud</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
    </head>
    <body>
        <h1>Git Cloud</h1>
`,`
    </body>
</html>
`];

const createLink = (href, text) => {
    return `        <a href="${href}">${text}</a><br />\n`;
}

// create indexing HTMLs
const createHTMLs = (current, path) => {
    let html = HTMLTemplate[0];
    if (current.__files__ !== undefined){
        for (file of current.__files__){
            if (file === "index.html"){
                continue;
            }
            html += createLink(file, file);
        }
    }
    for (let key in current){
        if (key === "__files__"){
            continue;
        }
        createHTMLs(current[key], path + key + "/");
        html += createLink(key + "/index.html", key);
    }
    html += HTMLTemplate[1];
    fs.writeFileSync(path + "index.html", html);
}

createHTMLs(dirs, "./");

fs.writeFileSync("path.json", JSON.stringify(dirs, null, 4));