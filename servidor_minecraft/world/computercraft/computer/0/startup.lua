---@diagnostic disable: undefined-field, undefined-global

-- ☺ CONFIGURAÇÃO ☺ -- 
local POP_UP_COUNT = 16
local MUSIC_FILE = "data/music/idiot_musiz.wav"

-- Modulos
local dfpwm = require("cc.audio.dfpwm")

-- Peripheals
local monitor = peripheral.find("monitor")
local speaker = peripheral.find("speaker")

-- Posições
local w, h = monitor.getSize()
w = math.max(4, w - 16)
h = h - 1

-- local position = vector.new(math.max(math.floor(w / 2), 1), math.floor(h / 2), 0)
-- local velocity = vector.new((math.random(2, 3) % 3) - 1, (math.random(2, 3) % 3) - 1, 0)
local idiots = {}
-- Gera idiotas
for i = 1, POP_UP_COUNT do
    idiots[i] = {}

    idiots[i]["pos"] = vector.new(math.random(2, w - 1),
        math.random(2, h - 1), 0)
    idiots[i]["vel"] = vector.new((math.random(2, 3) % 3) - 1, (math.random(2, 3) % 3) - 1, 0)
    idiots[i]["inv"] = math.random(0, 1) == 1
end

-- Outros
local audio_decoder = dfpwm.make_decoder()

local function playMusic()
    while true do
        for chunk in io.lines(MUSIC_FILE, 8 * 1024) do
            local audio_buffer = audio_decoder(chunk)

            while not speaker.playAudio(audio_buffer) do
                os.pullEvent("speaker_audio_empty")
            end
        end
    end
end

local function drawIdiot()
    while true do
        monitor.clear()

        for _, idiot in ipairs(idiots) do
            -- Desenha o idiota
            monitor.setCursorPos(idiot["pos"].x, idiot["pos"].y)
            monitor.blit("You are an idiot!", idiot["inv"] and "fffffffffffffffff" or "00000000000000000", idiot["inv"] and "00000000000000000" or "fffffffffffffffff")
            
            monitor.setCursorPos(idiot["pos"].x, idiot["pos"].y + 1)
            monitor.blit("  =D   =D   =D   ", idiot["inv"] and "fffffffffffffffff" or "00000000000000000", idiot["inv"] and "00000000000000000" or "fffffffffffffffff")
            
            -- Move X
            idiot["pos"].x = idiot["pos"].x + idiot["vel"].x
            if idiot["pos"].x <= 1 or idiot["pos"].x >= w then
                idiot["vel"].x = -idiot["vel"].x
                idiot["inv"] = not idiot["inv"]
            end

            -- Move Y
            idiot["pos"].y = idiot["pos"].y + idiot["vel"].y
            if idiot["pos"].y <= 1 or idiot["pos"].y >= h then
                idiot["vel"].y = -idiot["vel"].y
                idiot["inv"] = not idiot["inv"]
            end
        end

        sleep(0.1)
    end
end

parallel.waitForAll(drawIdiot, playMusic)
