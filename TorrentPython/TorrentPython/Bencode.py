class Bencode(object):
    @staticmethod
    def decode(source: bytes):
        func = Bencode.get_decoder(source, 0)
        ret, npos = func(source, 0)
        return ret

    @staticmethod
    def decode_d(source: bytes, spos):
        if source[spos] != ord('d'):
            return None

        retdict = {}
        npos = spos + 1
        while spos < len(source) and source[npos] != ord('e'):
            func = Bencode.get_decoder(source, npos)
            key, npos = func(source, npos)            
            func = Bencode.get_decoder(source, npos)
            value, npos = func(source, npos)
            retdict[key] = value
            
        return retdict, npos + 1

    @staticmethod
    def decode_l(source: bytes, spos):
        if source[spos] != ord('l'):
            return None

        retlist = []
        npos = spos + 1
        while spos < len(source) and source[npos] != ord('e'):
            func = Bencode.get_decoder(source, npos)
            ret, npos = func(source, npos)
            retlist.append(ret)
            
        return retlist, npos + 1

    @staticmethod
    def decode_i(source: bytes, spos):
        if source[spos] != ord('i'):
            return None

        epos = spos
        while spos < len(source) and source[epos] != ord('e'):
            epos += 1

        return int(source[spos + 1:epos]), epos + 1

    @staticmethod
    def decode_s(source: bytes, spos):
        epos = spos
        while spos < len(source) and source[epos] != ord(':'):
            epos += 1

        strlen = int(source[spos:epos])
        npos = epos + 1

        return source[npos:npos + strlen], npos + strlen

    @staticmethod
    def get_decoder(source: bytes, spos):
        if source[spos] == ord('d'): # dictionary
            return Bencode.decode_d
               
        elif source[spos] == ord('l'): # list
            return Bencode.decode_l

        elif source[spos] == ord('i'): # int
            return Bencode.decode_i

        else: # string
            return Bencode.decode_s

    @staticmethod
    def get_info_dictionary(source: bytes):
        spos = source.find(b'4:infod') + 6
        ret, npos = Bencode.decode_d(source, spos)
        return source[spos:npos]

    @staticmethod
    def encode(source: dict):
        func = Bencode.get_encoder(source)
        return func(source)

    @staticmethod
    def encode_d(source: dict):
        retbytes = b'd'
        for k in sorted(source):
            v = source[k]
            func = Bencode.get_encoder(k)
            retbytes += func(k)
            func = Bencode.get_encoder(v)
            retbytes += func(v)

        retbytes += b'e'
        
        return retbytes

    @staticmethod
    def encode_l(source: list):
        retbytes = b'l'
        for item in source:
            func = Bencode.get_encoder(item)
            ret = func(item)
            retbytes += ret

        retbytes += b'e'
        
        return retbytes

    @staticmethod
    def encode_i(source: int):
        return b'i' + str(source).encode() + b'e'

    @staticmethod
    def encode_s(source: bytes):
        length = len(source)
        return str(length).encode() + b':' + source

    @staticmethod
    def get_encoder(source):
        if type(source) == dict:
            return Bencode.encode_d

        elif type(source) == list:
            return Bencode.encode_l

        elif type(source) == int:
            return Bencode.encode_i

        else:  # bytes
            return Bencode.encode_s
