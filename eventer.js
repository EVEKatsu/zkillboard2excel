const fs = require("fs")
const path = require("path")

const zerorpc = require("zerorpc")

const SETTINGS_JSON_PATH = path.join(__dirname, "settings.json")

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

let client = new zerorpc.Client()
client.connect("tcp://127.0.0.1:4242")
client.invoke("echo", "server ready", (error, res) => {
  if(error || res !== 'server ready') {
    console.error(error)
  } else {
    console.log("server is ready")
  }
})

const consoleLog = (text) => {
  if (text) {
    const textarea = document.querySelector("#consoleLog")
    textarea.innerHTML += text + '&#13;'
    textarea.scrollTop = textarea.scrollHeight
  } 
}

setInterval(function() {
  client.invoke("log", (error, res) => {
    if(error) {
      console.error(error)
    } else {
      consoleLog(res)
    }
  })
}, 1000)

document.querySelector("#export").addEventListener("click", () => {
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

  client.invoke("export")
})

document.querySelector("#stop").addEventListener("click", () => {
  client.invoke("terminate")
})
