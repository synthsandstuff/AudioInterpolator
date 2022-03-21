import os
import wave
import struct

def Interpolate(x0,x1,x2,x3,t): #InterpolateHermite4pt3oX
    c0 = x1
    c1 = 0.5 * (x2 - x0)
    c2 = x0 - (2.5 * x1) + (2 * x2) - (0.5 * x3)
    c3 = (0.5 * (x3 - x0)) + (1.5 * (x1 - x2))
    return (((((c3 * t) + c2) * t) + c1) * t) + c0

def Interpolate2(x0,x1,x2,x3,t):
    a0 = x3 - x2 - x0 + x1
    a1 = x0 - x1 - a0
    a2 = x2 - x0
    a3 = x1
    return (a0 * (t * t * t)) + (a1 * (t * t)) + (a2 * t) + (a3)

def Interpolate3(x0,x1,x2,x3,t):
    return (x1*1-t)+(x2*(t))/2

def Indexer(k,wave):
    lenw = len(wave)
    indx = [0]*4
    indx[1] = wave[k]
    if(k>0):
        indx[0] = wave[k-1]
    else:
        indx[0] = 0
    try:
        indx[2] = wave[k+1]
    except:
        indx[2] = 0
    try:
        indx[3] = wave[k+2]
    except:
        indx[3] = 0
    return indx

def ReadWave(wav):
    chan = wav.getnchannels()
    sdep = wav.getsampwidth()
    sdpt = 4-sdep
    n = wav.getnframes()
    file = wav.readframes(n)
    audiol = [None]*n
    audior = [None]*n
    counter = 0
    for i in range(n*2):
        temp = struct.unpack('<b',file[counter+sdep-1:counter+sdep])[0]
        if(i%2 == 0):
            if(temp >> 7 == -1):
                audiol[int(i/2)] = struct.unpack('<i',file[counter:counter+sdep]+b'\xff'*sdpt)[0]
            else:
                audiol[int(i/2)] = struct.unpack('<i',file[counter:counter+sdep]+b'\x00'*sdpt)[0]
        else:
            if(temp >> 7 == -1):
                audior[int(i/2)] = struct.unpack('<i',file[counter:counter+sdep]+b'\xff'*sdpt)[0]
            else:
                audior[int(i/2)] = struct.unpack('<i',file[counter:counter+sdep]+b'\x00'*sdpt)[0]
        counter += sdep
    return audiol, audior

def ConcatBinary(file,bitd): #mono byte-like
    binaudio = bytearray()
    for i in file:
        binaudio += bytes(struct.pack('<i',i))[0:bitd]
    return binaudio

def Interlacing(file,k): #stereo int
    output = [None]*len(file[0])*2
    counter = 0
    for i in range(len(file[0])):
        output[counter] = file[0][i]
        counter += 1
        output[counter] = file[1][i]
        counter += 1
    return output

def WriteWave(wav,header,al): #stereo byte-like
    wavf = wave.open(os.getcwd()+'/outputf'+str(al)+'.wav', mode='wb')
    wavf.setparams(header)
    wavf.writeframes(wav)
    wavf.close()

def InterpolatorAL0(audio,y,z): #mono int
    newaudio = [0]*len(audio)
    counter = 0
    for i in range(len(audio)):
        for j in range(y):
            newaudio[counter] = audio[i]*5.427
            counter += 1
    return newaudio

def InterpolatorAL1(audio,y,z): #mono int
    newaudio = [0]*len(audio)*y
    counter = 0
    for i in range(len(audio)):
        indx = Indexer(i, audio)
        for j in range(y):
            newaudio[counter] = Interpolate(indx[0], indx[1], indx[2], indx[3],z*j)
            counter += 1
    return newaudio

def InterpolatorAL2(audio,y,z): #mono int
    newaudio = [0]*len(audio)*y
    counter = 0
    for i in range(len(audio)):
        indx = Indexer(i, audio)
        for j in range(y):
            newaudio[counter] = Interpolate2(indx[0], indx[1], indx[2], indx[3],z*j)
            counter += 1
    return newaudio

def InterpolatorAL3(audio,y,z):
    newaudio = [0]*len(audio)*y
    counter = 0
    for i in range(len(audio)):
        indx = Indexer(i,audio)
        for j in range(y):
            newaudio[counter] = Interpolate3(indx[0], indx[1], indx[2], indx[3],z*j)
            counter += 1
    return newaudio

def WaveWriter(bitd):
    peak = (2**(bitd*8))-1
    newaudio = [0]*peak
    for i in range(peak):
        newaudio[i] = i
    return newaudio

def NormaliseAudio(audio,bitd):
    maxw = ((2**(bitd*8)))/2
    mina = min(audio)
    maxa = max(audio)
    ofst = (mina+maxa)/2
    if(ofst != 0):
        for i in range(len(audio)):
            audio[i] = int(audio[i] - ofst)
    else:
        for i in range(len(audio)):
            audio[i] = int(audio[i])
    if(maxa > maxw-1 or mina < maxw*-1):
        if(maxa > mina*-1):
            divf = maxa/(maxw-1)
        else:
            divf = mina/maxw
        for i in range(len(audio)):
            audio[i] = round((audio[i]/divf))
    return audio

wav = wave.open(str(input("File: ")), mode='rb')

y = int(input("Upscale factor: "))

alg = int(input("Algorithm (0,1,2,3): "))

audio = ReadWave(wav)

header = wav.getparams()

wav.close()

header = header[0],header[1],header[2]*y,header[3]*y,header[4],header[5]

z = 1/y

if(alg == 0):
    audiol = InterpolatorAL0(audio[0],y,z)
    audior = InterpolatorAL0(audio[1],y,z)
elif(alg == 1):
    audiol = InterpolatorAL1(audio[0],y,z)
    audior = InterpolatorAL1(audio[1],y,z)
elif(alg == 2):
    audiol = InterpolatorAL2(audio[0],y,z)
    audior = InterpolatorAL2(audio[1],y,z)
elif(alg == 3):
    audiol = InterpolatorAL3(audio[0],y,z)
    audior = InterpolatorAL3(audio[1],y,z)
elif(alg == 4):
    audiol = WaveWriter(header[1])
    audior = WaveWriter(header[1])
else:
    print("No such algorithm")

audiol = NormaliseAudio(audiol,header[1])
audior = NormaliseAudio(audior,header[1])
audio = audiol, audior   

audio = Interlacing(audio,y)

audio = ConcatBinary(audio,header[1])

WriteWave(audio,header,alg)

print("Processing Complete")
