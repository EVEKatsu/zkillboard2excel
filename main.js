const path = require("path")

const electron = require("electron")
const app = electron.app
const BrowserWindow = electron.BrowserWindow


//
// python process
//
const PYTHON_DIST_PATH = "dist"
const PYTHON_MODULE = "api"

let pythonProcess = null

const guessPackaged = () => {
  return require("fs").existsSync(path.join(__dirname, PYTHON_DIST_PATH))
}

const getScriptPath = () => {
  if (guessPackaged()) {
    if (process.platform === "win32") {
      return path.join(__dirname, PYTHON_DIST_PATH, PYTHON_MODULE, PYTHON_MODULE + ".exe")
    } else {
      return path.join(__dirname, PYTHON_DIST_PATH, PYTHON_MODULE, PYTHON_MODULE)
    }
  } else {
    return path.join(__dirname, PYTHON_MODULE + ".py")
  }
}

const createPythonProcess = () => {
  const scriptPath = getScriptPath()

  if (guessPackaged()) {
    pythonProcess = require("child_process").execFile(scriptPath, [__dirname])
  } else {
    pythonProcess = require("child_process").spawn("python", [scriptPath, __dirname])
  }

  if (pythonProcess != null) {
    console.log("child process success")
  }
}

const exitPythonProcess = () => {
  if (pythonProcess !== null) {
    pythonProcess.kill()
    pythonProcess = null
  }
}

app.on("ready", createPythonProcess)
app.on("will-quit", exitPythonProcess)

//
// window management
//
let mainWindow = null

const createWindow = () => {
  mainWindow = new BrowserWindow({width: 1024, height: 768})
  mainWindow.setTitle("zKillboard2Excel")
  mainWindow.setMenu(null)
  mainWindow.loadURL(require("url").format({
    pathname: path.join(__dirname, "index.html"),
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
