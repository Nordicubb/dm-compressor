import array as arr
import math
import wave as wav
import struct
import librosa
import soundfile as sf
import os
from pydub import AudioSegment as Am
import sys

a = 0
b = 0
buffer = ""
current = 0

usage = "Nordicub's NES-Style DPCM Compressor v1.0.0 USAGE:\ndpcmcomp [Input audio filename with extension] [output wav filename]\ndpcmcomp [Input audio filename with extension] -- Output filename is output.wav.\ndpcmcomp -- Opens Usage."

if len(sys.argv) > 3 or len(sys.argv) < 2:
    print(usage)
    sys.exit()

sys.argv[0] = sys.argv[1]
if len(sys.argv) == 3:
    sys.argv[1] = sys.argv[2]

if sys.argv[0] == "?" or sys.argv[0] == "help":
    print(usage)
    sys.exit()

if len(sys.argv) == 3:
    if sys.argv[1].lower().endswith(".wav"):
        outname = sys.argv[1]
    else:
        outname = sys.argv[1] + ".wav"
else:
    outname = "output.wav"

if os.path.isfile(outname):
    exists = input(f"File named {outname} already exists. Continue? (y/n) ")
    if exists.lower() != "y":
        sys.exit()

try:
    print("Reading input file...")
    file = Am.from_file(sys.argv[0])
    print("Successfully read input file.")
    print("Converting to mono...")
    monofile = file.set_channels(1)
    monofile.export("tempwavdpcmcomp.wav", format="wav")
    print("Successfully converted to mono.")
    print("Resampling to 44.1kHz...")
    with wav.open("tempwavdpcmcomp.wav", "r") as wavf:
        file, sr = librosa.load("tempwavdpcmcomp.wav", sr=44100)
        sf.write("tempsrdpcmcomp.wav", file, sr)
    print("Successfully resampled to 44.1kHz.")
    print("Removing temp mono file...")
    os.remove("tempwavdpcmcomp.wav")
    print("Successfully removed temp mono file.")
except FileNotFoundError:
    print(f"ERROR: File {sys.argv[0]} not found.")
    sys.exit()
except PermissionError:
    print("ERROR: Insufficient permissions to create/remove files.")
    sys.exit()
except TypeError as e:
    print(usage)
    sys.exit()
except Exception:
    print(usage)
    sys.exit()

try:
    with wav.open("tempsrdpcmcomp.wav", "r") as wavff:
        for i, v in enumerate(arr.array("h", wavff.readframes(wavff.getnframes()))):
            print("Building output file... " + str(math.floor(len(buffer) / wavff.getnframes() * 100)) + "%", end="\r")
            if i == 0:
                a = v
                b = v
            else:
                a = b
                b = v
            if a < b:
                current = 1
            elif a == b:
                current = int(not current)
            else:
                current = 0
            if buffer == "":
                buffer = str(current)
            else:
                buffer = buffer + str(current)
except FileNotFoundError:
    print(f"ERROR: File tempsrdpcmcomp.wav not found.")
    sys.exit()
except PermissionError:
    print("ERROR: Unable to read file.")
    sys.exit()
except Exception:
    print(usage)
    sys.exit()
try:
    print("Output file built successfully.")
    print("Removing temp resampled file...")
    os.remove("tempsrdpcmcomp.wav")
    print("Successfully removed temp resampled file.")
except FileNotFoundError:
    print(f"ERROR: File tempsrdpcmcomp.wav not found.")
    sys.exit()
except PermissionError:
    print("ERROR: Insufficient permissions to delete files.")
    sys.exit()
except Exception:
    print(usage)
    sys.exit()

try:
    print("Creating output file...")
    with wav.open(outname, "w") as f:
        print("Output file created successfully.")
        f.setnchannels(1)
        f.setsampwidth(1)
        f.setframerate(44100)
        h = 128
        g = 192
        counter = 0
        for s in buffer:
            print("Encoding output file... " + str(math.floor(counter / len(buffer) * 100)) + "%", end="\r")
            h += 64
            g = h
            if int(s) == 0:
                h -= 1
            else:
                h += 1
            if h > 255:
                if g == 255:
                    h = 254
                else:
                    h = 255
            elif h < 128:
                if g == 128:
                    h = 129
                else:
                    h = 128
            h -= 64
            for j in range(0, 1):
                f.writeframes(struct.pack("<B", h))
            counter += 1
    print("Output file encoded successfully.")
    print("Finished!")
except PermissionError:
    print(f"ERROR: Insufficient permissions to create files.")
    sys.exit()
except Exception:
    print(usage)
    sys.exit()
