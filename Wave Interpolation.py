import os
import wave
import struct

def Interpolate(x0,x1,x2,x3,t): #InterpolateHermite4pt3oX
    c0 = x1
    c1 = 0.5 * (x2 - x0)
    c2 = x0 - (2.5 * x1) + (2 * x2) - (0.5 * x3)
    c3 = (0.5 * (x3 - x0)) + (1.5 * (x1 - x2))
    return int((((((c3 * t) + c2) * t) + c1) * t) + c0)

def Interpolate2(x0,x1,x2,x3,t):
    a0 = x3 - x2 - x0 + x1
    a1 = x0 - x1 - a0
    a2 = x2 - x0
    a3 = x1
    return int((a0 * (t * t * t)) + (a1 * (t * t)) + (a2 * t) + (a3))

def Indexer(k,wave):
    lenw = len(wave)
    indx = [0]*4
    if(k == 0):
        indx[0] = 0
        indx[1] = int(wave[k])
        indx[2] = int(wave[k+1])
        indx[3] = int(wave[k+2])
    elif(k+1 == lenw):
        indx[0] = int(wave[k-1])
        indx[1] = int(wave[k])
        indx[2] = 0
        indx[3] = 0
    elif(k+2 == lenw):
        indx[0] = int(wave[k-1])
        indx[1] = int(wave[k])
        indx[2] = int(wave[k+1])
        indx[3] = 0
    else:
        indx[0] = int(wave[k-1])
        indx[1] = int(wave[k])
        indx[2] = int(wave[k+1])
        indx[3] = int(wave[k+2])
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
        if(i%2 == 0):
            audiol[int(i/2)] = struct.unpack('<i',file[counter:counter+sdep]+b'\00'*sdpt)[0]
        else:
            audior[int(i/2)] = struct.unpack('<i',file[counter:counter+sdep]+b'\00'*sdpt)[0]
        counter +=3
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
    newaudio = [0]*len(audio)*y
    counter = 0
    for i in range(len(audio)):
        for j in range(y):
            newaudio[counter] = (audio[i]*2)
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

"""
def NormaliseAudio(audio,header): #mono int
    maxw = (2**(header[1]*8)/2)-1
    print("CHANNEL_START")
    sorteda = [0]*len(audio)
    for i in range(len(audio)):
        sorteda[i] = audio[i]
    sorteda.sort()
    print(audio[-1])
    print(audio[0])
    print(sorteda[-1])
    print(sorteda[0])
    if(sorteda[-1] >= maxw or sorteda[0] <= maxw*-1):
        if(sorteda[-1] > sorteda[0]*-1):
            divf = sorteda[-1]/maxw
        else:
            divf = (sorteda[0]*-1)/maxw
        print(divf)
        for i in range(len(audio)):
            audio[i] = int(audio[i]/divf)
    print(audio[-1])
    print(audio[0])
    for i in range(len(audio)):
        sorteda[i] = audio[i]
    sorteda.sort()
    print(sorteda[-1])
    print(sorteda[0])
    print("CHANNEL_END")
    return audio
"""

def NormaliseAudio(audio,header):
    maxw = ((2**(header[1]*8))/2)-1
    maxa = max(audio)
    mina = min(audio)
    print(maxa)
    print(mina)
    if(maxa > maxw or mina < maxw*-1 or 1 == 1):
        if(maxa > mina*-1):
            divf = maxa/(maxw)
        else:
            divf = mina/(maxw*-1)
        for i in range(len(audio)):
            audio[i] = int(audio[i]/divf)
    return audio

wav = wave.open(str(input("File: ")), mode='rb')

y = int(input("Upscale factor: "))

alg = int(input("Algorithm (0,1,2,3): "))

z = 1/y

audio = ReadWave(wav)

header = wav.getparams()

wav.close()

header = header[0], 4,header[2]*y,header[3]*y,header[4],header[5]

if(alg == int(0)):
    audiol = InterpolatorAL0(audio[0],y,z)
    audior = InterpolatorAL0(audio[1],y,z)
    #audiol = NormaliseAudio(audiol,header)
    #audior = NormaliseAudio(audior,header)
    audio = audiol, audior
    al = 0
elif(alg == int(1)):
    audiol = InterpolatorAL1(audio[0],y,z)
    audior = InterpolatorAL1(audio[1],y,z)
    #audiol = NormaliseAudio(audiol,header)
    #audior = NormaliseAudio(audior,header)
    audio = audiol, audior
    al = 1
elif(alg == int(2)):
    audiol = InterpolatorAL2(audio[0],y,z)
    audior = InterpolatorAL2(audio[1],y,z)
    audiol = NormaliseAudio(audiol,header)
    audior = NormaliseAudio(audior,header)
    audio = audiol, audior
    al = 2
else:
    al = 3
    
audio = Interlacing(audio,y)

audio = ConcatBinary(audio,header[1])

WriteWave(audio,header,al)

print("Processing Complete")
