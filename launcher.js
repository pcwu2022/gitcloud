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
let dirs = {key: "Home"};
for (let file of allFiles){
    filename = file.replaceAll("\\", "/");
    let filePath = filename.split("/");
    let current = dirs;
    while (filePath.length > 1){
        if (!current[filePath[0]]){
            current[filePath[0]] = {
                key: filePath[0]
            };
        }
        current = current[filePath[0]];
        filePath.shift();
    }
    if (!current.__files__){
        current.__files__ = []
    }
    current.__files__.push(filePath[0])
}

const Template = "./template.html";
const Card = "./components/card.html";
const Image = "./components/image.html";
const Link = "./components/link.html";
const Download = "./components/download.html";
const Video = "./components/video.html";
const Audio = "./components/audio.html";
const CSS = "./style.css";
const JS = "./script.js";

const render = async (templatePath, props) => {
    return new Promise((resolve, reject) => {
        fs.readFile(templatePath, "utf-8",  (err, data) => {
            let htmlArr = data.split("{{");
            let finalHTML = htmlArr[0];
            for (let i = 1; i < htmlArr.length; i++){
                let tempTuple = htmlArr[i].split("}}");
                let key = tempTuple[0];
                if (key in props){
                    finalHTML += props[key];
                }
                finalHTML += tempTuple[1];
            }
            resolve(finalHTML);
        });
    })
}

const fileType = (filePath) => {
    let types = {
        image: ["jpg", "jpeg", "png", "svg"],
        doc: ["pdf", "md", "html"],
        video: ["mp4"],
        audio: ["mp3", "wav"]
    }
    for (let type in types){
        for (let sub of types[type]){
            if (filePath.indexOf(sub) !== -1){
                return type;
            }
        }
    }
    return "download";
}

const fileName = (filePath) => {
    let pathArr = filePath.split(".");
    pathArr.splice(pathArr.length - 1, 1);
    let retPath = pathArr.join(".");
    if (fileType(filePath) === "download"){
        retPath = filePath;
    }
    if (retPath.length > 15){
        retPath = retPath.substring(0, 18) + "...";
    }
    return retPath;
}

// create indexing HTMLs
const createHTMLs = async (current, path) => {
    let props = {
        title: current.key,
        body: ""
    }
    props.CSS = await render(CSS, {});
    props.JS = await render(JS, {});

    for (let key in current){
        if (key === "__files__" || key === "key"){
            continue;
        }
        await createHTMLs(current[key], path + key + "/");
        props.body += "\n";
        props.body += await render(Link, {title: key, href: key + "/index.html"})
    }
    props.body += "<br />"
    if (current.__files__ !== undefined){
        for (file of current.__files__){
            if (file === "index.html"){
                continue;
            }
            props.body += "\n";
            if (fileType(file) === "doc"){
                props.body += await render(Card, {title: fileName(file), href: file});
            } else if (fileType(file) === "image"){
                props.body += await render(Image, {title: fileName(file), href: file});
            } else if (fileType(file) === "video"){
                props.body += await render(Video, {title: fileName(file), href: file});
            } else if (fileType(file) === "audio"){
                props.body += await render(Audio, {title: fileName(file), href: file});
            } else {
                props.body += await render(Download, {title: fileName(file), href: file});
            }
        }
    }
    
    let html = await render(Template, props);
    fs.writeFile(path + "index.html", html, (err) => {
        if (err){
            console.error(err);
        }
    });
}

createHTMLs(dirs, "./");

fs.writeFileSync("path.json", JSON.stringify(dirs, null, 4));