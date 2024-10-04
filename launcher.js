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

// Output the result as JSON
fs.writeFileSync("path.json", JSON.stringify(allFiles, null, 4).replaceAll("\\\\", "/"));
