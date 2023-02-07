import os
import wave
import struct

def Interpolate(x0,x1,x2,x3,t): #This is an implementation of an Interpolation algorithm. InterpolateHermite4pt3oX
    c0 = x1
    c1 = 0.5 * (x2 - x0)
    c2 = x0 - (2.5 * x1) + (2 * x2) - (0.5 * x3)
    c3 = (0.5 * (x3 - x0)) + (1.5 * (x1 - x2))
    return (((((c3 * t) + c2) * t) + c1) * t) + c0

def Interpolate2(x0,x1,x2,x3,t): #This is an implementation of an Interpolation algorithm.
    a0 = x3 - x2 - x0 + x1
    a1 = x0 - x1 - a0
    a2 = x2 - x0
    a3 = x1
    return (a0 * (t * t * t)) + (a1 * (t * t)) + (a2 * t) + (a3)

def Interpolate3(x0,x1,x2,x3,t): #This is an implementation of an Interpolation although this one simply finds the average between two points and this isnt very accurate.
    return (x1*1-t)+(x2*(t))/2

def Indexer(k,wave): #Function to find the samples to feed the interpolation algorithms with.
    lenw = len(wave)
    indx = [0]*4 #Initialises array to return samples
    indx[1] = wave[k] #The sample at index 1 is never going to be outside of the range of the audio and therefore it can simply be set with no extra handling.
    if(k>0): #The sample at index 0 can be on the first iteration of the interpolation before the audio actually starts, so in this case the value is set to zero else it is the sample the sample at index 1.
        indx[0] = wave[k-1]
    else:
        indx[0] = 0
    try: #Similar to above this handles when the sample we want is non existant as it falls after the audio so this handles that eventuality
        indx[2] = wave[k+1]
    except:
        indx[2] = 0
    try: #Same as above except for the last sample.
        indx[3] = wave[k+2]
    except:
        indx[3] = 0
    return indx

def ReadWave(wav): #This function gets the audio from the wav file and takes the bytes like data returned from wav.readframes() and splits it into stereo int arrays
    chan = wav.getnchannels()
    sdep = wav.getsampwidth()
    sdpt = 4-sdep #As python uses 32 bit ints, this number is the number of empty bytes that need to be added to each frame of audio to convert from bytes to an int.
    n = wav.getnframes() 
    file = wav.readframes(n)
    audiol = [None]*n #Initialises left array for audio
    audior = [None]*n #Initaliases right array for audio
    counter = 0
    for i in range(n*2):
        temp = struct.unpack('<b',file[counter+sdep-1:counter+sdep])[0] #Gets the last byte of the corresponding frame of audio
        if(i%2 == 0): #If the sample number is even it is for the left channel of audio
            if(temp >> 7 == -1): #This sees if the signed bit is negative or positive to handle twos complement
                audiol[int(i/2)] = struct.unpack('<i',file[counter:counter+sdep]+b'\xff'*sdpt)[0] #If the signed bit is negative the padding bytes have to be inverted to represent the correct number in twos complement. Also the int(i/2) truncates the division so we get the right sample number for the channel, whilst the loop happens enough for every single audio frame in the stereo file.
            else:
                audiol[int(i/2)] = struct.unpack('<i',file[counter:counter+sdep]+b'\x00'*sdpt)[0] #The padding bytes here are simple zero as the number is positive.
        else: #This happens if 
            if(temp >> 7 == -1):
                audior[int(i/2)] = struct.unpack('<i',file[counter:counter+sdep]+b'\xff'*sdpt)[0] #Same as above for the right audio array
            else:
                audior[int(i/2)] = struct.unpack('<i',file[counter:counter+sdep]+b'\x00'*sdpt)[0] #Same as above for the right audio array
        counter += sdep #Increments with the number of actual bytes read from the bytes like data.
    return audiol, audior #Returns the two array of signed ints as a tuple.

def ConcatBinary(file,bitd): #Takes a single array of bytes like data and concatenates it to a single byte array to be written to the wav file.
    binaudio = bytearray() #Declares binaudio as a bytearray.
    for i in file:
        binaudio += bytes(struct.pack('<i',i))[0:bitd]#Removes the padding bytes added to retain the original bit depth.
    return binaudio

def Interlacing(file,k): #Takes two int arrays as a tuple to turn it into a single array of each sample alternating between left and right.
    output = [None]*len(file[0])*2 #Declares an array of the size of the finished array.
    counter = 0
    for i in range(len(file[0])): #Iterates through every sample in each array.
        output[counter] = file[0][i]
        counter += 1
        output[counter] = file[1][i]
        counter += 1
    return output #Returns a single array of alternating left and right samples

def WriteWave(wav,header,al): #Takes the concatenated binary file and writes it to a new wav file.
    wavf = wave.open(os.getcwd()+'/outputf'+str(al)+'.wav', mode='wb')
    wavf.setparams(header)
    wavf.writeframes(wav)
    wavf.close()

def InterpolatorAL0(audio,y,z): #Implementation of the interpolation algorithms, takes a single array
    newaudio = [0]*(len(audio)*y) #Declares a new array for the interpolated audio
    counter = 0 
    for i in range(len(audio)):
        for j in range(y):
            newaudio[counter] = audio[i] #This algortihm just duplicates the sample across a few more samples, sounds the worst.
            counter += 1
    return newaudio

def InterpolatorAL1(audio,y,z): #Implementation of the interpolation algorithms, takes a single array
    newaudio = [0]*len(audio)*y
    counter = 0
    for i in range(len(audio)):
        indx = Indexer(i, audio) #Get the samples that we require to interpolate.
        for j in range(y):
            newaudio[counter] = Interpolate(indx[0], indx[1], indx[2], indx[3],z*j) #Gives the function the required samples to calculte the values.
            counter += 1
    return newaudio

def InterpolatorAL2(audio,y,z): #Implementation of the interpolation algorithms, takes a single array
    newaudio = [0]*len(audio)*y
    counter = 0
    for i in range(len(audio)):
        indx = Indexer(i, audio) #Get the samples that we require to interpolate.
        for j in range(y):
            newaudio[counter] = Interpolate2(indx[0], indx[1], indx[2], indx[3],z*j) #Gives the function the required samples to calculte the values.
            counter += 1
    return newaudio

def InterpolatorAL3(audio,y,z):
    newaudio = [0]*len(audio)*y
    counter = 0
    y = y // 5 + (y % 5 > 0)
    for i in range(len(audio)):
        indx = Indexer(i,audio) #Get the samples that we require to interpolate.
        for j in range(y):
            newaudio[counter] = Interpolate3(indx[0], indx[1], indx[2], indx[3],z*j) #Gives the function the required samples to calculte the values even though this only requires 2 as its an average.
            counter += 1
    return newaudio

def WaveWriter(bitd): #Used for testing, generates a sweep of values from the minimum value the bitdepth allows for to the max
    peak = (2**(bitd*8))-1
    newaudio = [0]*peak
    for i in range(peak):
        newaudio[i] = i
    return newaudio

def NormaliseAudio(audio,bitd): #Simple nomalisation used to ensure that the values that were generated by the interpolation functions do not go beyond the max and min values.
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
