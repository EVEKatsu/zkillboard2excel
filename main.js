const path = require("path")

const electron = require("electron")
const app = electron.app
const BrowserWindow = electron.BrowserWindow

let mainWindow = null

const createWindow = () => {
  mainWindow = new BrowserWindow({width: 800, height: 600})
  mainWindow.loadURL(require("url").format({
    pathname: path.join(__dirname, "index.html"),
    icon: path.join(__dirname, "icon.png"),
    protocol: "file:",
    slashes: true
  }))

  mainWindow.webContents.on("new-window", (event, url) => {
    event.preventDefault();
    electron.shell.openExternal(url);
  })
  //mainWindow.webContents.openDevTools()

  mainWindow.on("closed", () => {
    mainWindow = null
  })
}

app.on("ready", createWindow)

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit()
  }
})

app.on("activate", () => {
  if (mainWindow === null) {
    createWindow()
  }
})
