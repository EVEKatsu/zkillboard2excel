const fs = require("fs")
const path = require("path")

const zerorpc = require("zerorpc")


const PYTHON_DIST_PATH = "dist"
const PYTHON_MODULE = "api"

const SETTINGS_JSON_PATH = "settings.json"

let pythonProcess = null

const consoleLog = (text) => {
  const consoleLog = document.querySelector("#consoleLog")
  consoleLog.innerHTML += text + "&#13;"
  consoleLog.scrollTop = consoleLog.scrollHeight
}

const server = new zerorpc.Server({
  log: function(text, reply) {
    consoleLog(text)
    reply(null)
  },
  exit: function(reply) {
    exitPythonProcess()
    reply(null)
  }
})
server.bind("tcp://0.0.0.0:4242")

if (fs.existsSync(SETTINGS_JSON_PATH)) {
  const settings = JSON.parse(fs.readFileSync(SETTINGS_JSON_PATH, "utf8"))
  const e = (name) => {
    return document.querySelector("#" + name)
  }

  e("zKillboardUrl").value = settings["zkb_url"]
  e("lang").value = settings["lang"]
  e("filepath").value = settings["filepath"]
  e("format").value = settings["format"]
  e("clearCache").checked = settings["clear-cache"]
  e("updateSde").checked = settings["update-sde"]
  e("page").value = settings["page"]
  e("limit").value = settings["limit"]
}

const guessPackaged = () => {
  return fs.existsSync(path.join(__dirname, PYTHON_DIST_PATH))
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
    pythonProcess = require("child_process").execFile(scriptPath)
  } else {
    pythonProcess = require("child_process").spawn("python", [scriptPath])
  }

  if (pythonProcess != null) {
    console.log("child process success")
  }
}

const exitPythonProcess = () => {
  pythonProcess.kill()
  pythonProcess = null
}

document.querySelector("#export").addEventListener("click", () => {
  if (pythonProcess !== null) {
    consoleLog('The script is already running.')
    return
  }

  const value = (name) => {
    return document.querySelector("#" + name).value
  }
  const checked = (name) => {
    return document.querySelector("#" + name).checked
  }
  const number = (name) => {
    num = Number(value(name))
    return (num == 0 || isNaN(num)) ? 1 : num
  }

  fs.writeFileSync(
    SETTINGS_JSON_PATH,
    JSON.stringify({
      "zkb_url": value("zKillboardUrl"),
      "lang": value("lang"),
      "filepath": value("filepath"),
      "format": value("format"),
      "page": number("page"),
      "limit": number("limit"),
      "clear-cache": checked("clearCache"),
      "update-sde": checked("updateSde")
    }, undefined, "    ")
  )

  createPythonProcess()
})

document.querySelector("#stop").addEventListener("click", () => {
  exitPythonProcess()
  consoleLog("Stop")
})
