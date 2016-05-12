from collections import OrderedDict


class Bencode(object):
    @staticmethod
    def decode(source):
        func = Bencode.getDecoder(source, 0)
        ret, npos = func(source, 0)
        return ret

    @staticmethod
    def decode_d(source, spos):
        if source[spos] != ord('d'):
            return None

        retDict = {}
        npos = spos + 1
        while spos < len(source) and source[npos] != ord('e'):
            func = Bencode.getDecoder(source, npos)
            key, npos = func(source, npos)            
            func = Bencode.getDecoder(source, npos)
            value, npos = func(source, npos)
            retDict[key] = value
            
        return retDict, npos + 1

    @staticmethod
    def decode_l(source, spos):
        if source[spos] != ord('l'):
            return None

        retList = []
        npos = spos + 1
        while spos < len(source) and source[npos] != ord('e'):
            func = Bencode.getDecoder(source, npos)
            ret, npos = func(source, npos)
            retList.append(ret)
            
        return retList, npos + 1

    @staticmethod
    def decode_i(source, spos):
        if source[spos] != ord('i'):
            return None

        epos = spos
        while spos < len(source) and source[epos] != ord('e'):
            epos += 1

        return int(source[spos + 1:epos]), epos + 1

    @staticmethod
    def decode_s(source, spos):
        epos = spos
        while spos < len(source) and source[epos] != ord(':'):
            epos += 1

        strLen = int(source[spos:epos])        
        npos = epos + 1

        return source[npos:npos + strLen], npos + strLen

    @staticmethod
    def getDecoder(source, spos):        
        if source[spos] == ord('d'): # dictionary
            return Bencode.decode_d
               
        elif source[spos] == ord('l'): # list
            return Bencode.decode_l

        elif source[spos] == ord('i'): # int
            return Bencode.decode_i

        else: # string
            return Bencode.decode_s

    @staticmethod
    def getBencode_Info(source):
        spos = source.find(b'4:infod') + 6
        ret, npos = Bencode.decode_d(source, spos)
        return source[spos:npos]

    @staticmethod
    def encode(source):
        func = Bencode.getEncoder(source)
        return func(source)

    @staticmethod
    def encode_d(source):
        if type(source) != dict:
            print("encode_d : type error")
            return None

        source = OrderedDict(source)
        retBytes = b'd'
        for k, v in source.items():
            func = Bencode.getEncoder(k)
            retBytes += func(k)
            func = Bencode.getEncoder(v)
            retBytes += func(v)            

        retBytes += b'e'
        
        return retBytes

    @staticmethod
    def encode_l(source):
        if type(source) != list:
            print("encode_l : type error")
            return None

        retBytes = b'l'
        for item in source:
            func = Bencode.getEncoder(item)
            ret = func(item)
            retBytes += ret

        retBytes += b'e'
        
        return retBytes

    @staticmethod
    def encode_i(source):
        if type(source) != int:
            print("encode_i : type error")
            return None

        return b'i' + str(source).encode() + b'e'

    @staticmethod
    def encode_s(source):
        if type(source) != bytes:
            print("encode_s : type error")
            return None

        tLen = len(source)
        return str(tLen).encode() + b':' + source

    @staticmethod
    def getEncoder(source):
        if type(source) == dict:
            return Bencode.encode_d

        elif type(source) == list:
            return Bencode.encode_l

        elif type(source) == int:
            return Bencode.encode_i

        else: # bytes
            return Bencode.encode_s
