import os
import sys
import zipfile
import os.path

if sys.version[0] == "3": 
    raw_input=input


def getfillclass(jarfile):
    zf = zipfile.ZipFile(jarfile, 'r')
    modclasses = []
    try:
        lst = zf.infolist()
        for zi in lst:
            fn = zi.filename
            if fn.endswith('.class'):
                bytecode = zf.read(fn)
                p1 = bytecode.find(b'\x00\x15commands.fill.success')
                p2 = bytecode.find(b'\x00\x16commands.clone.success')
                if any(p > 0 for p in [p1, p2]):
                    modclasses += [fn]
    finally:
        zf.close()
    #print (modclasses)
    return modclasses


def isrelease(jsonfile):
    with open(jsonfile,'r') as fin:
        if any(['"type": "snapshot"' in l for l in fin.readlines()]):
            return False
    return True


def usesnewjson(jsonfile):
    with open(jsonfile,'r') as fin:
        if any(['"arguments":' in l for l in fin.readlines()]):
            return True
    return False
    

def install(jarfile, jarnew, jsonfile, jsonnew, versionnew, modclasses):
    
    with zipfile.ZipFile(jarfile, 'r') as zin:
        with zipfile.ZipFile(jarnew, 'w') as zout:
            zout.comment = zin.comment
            for item in zin.infolist():
                if jsonfile is not None and 'META-INF' in item.filename:
                    continue
                if any(fn == item.filename for fn in modclasses):
                    # replace limit 32768 with max integer
                    bytecode = zin.read(item.filename)
                    bytecode = bytecode.replace(b'\x00\x00\x80\x00', b'\x7f\xff\xff\xff')
                    zout.writestr(item, bytecode)
                else:
                    zout.writestr(item, zin.read(item.filename))
    
    if jsonfile is not None and jsonnew is not None:
        # json fix
        legacymcarg = '  "minecraftArguments": "--username ${auth_player_name}'+\
            ' --version ${version_name} --gameDir ${game_directory}'+\
            ' --assetsDir ${assets_root} --assetIndex ${assets_index_name}'+\
            ' --uuid ${auth_uuid} --accessToken ${auth_access_token}'+\
            ' --userType ${user_type} --versionType ${version_type}",\n'
        
        makerelease = False
        if not isrelease(jsonfile):
            line = raw_input('This version is a snapshot. Change it to a release? [Y/n]: ')
            if line.startswith('y') or line.startswith('Y'):
                makerelease = True
        
        fixMCL8475 = False
        if usesnewjson(jsonfile):
            line = raw_input('This version uses the new json format which can cause problems because of MCL8475. Use old json format? [Y/n]: ')
            if line.startswith('y') or line.startswith('Y'):
                fixMCL8475 = True

        with open(jsonnew,'w') as fout:
            with open(jsonfile,'r') as fin:
                for line in fin:
                    if '"id":' in line:
                        line = '"id": "'+versionnew+'",'
                    if '"assets":' in line:
                        fout.write(line)
                        line = next(fin)
                        fout.write(line)
                        bracketCnt = 1
                        while bracketCnt > 0:
                            line = next(fin)
                            if line is None:
                                break
                            if '{' in line:
                                bracketCnt += 1
                            if '}' in line:
                                bracketCnt -= 1
                    if makerelease and ('"type": "snapshot"' in line):
                        line = line.replace('snapshot','release')
                    if fixMCL8475:
                        if '"libraries":' in line:
                            fout.write(legacymcarg)
                        if '"assetIndex":' in line:
                            nextline = next(fin)
                            while '"arguments":' not in nextline:
                                fout.write(line)
                                line = nextline
                                nextline = next(fin)
                            bracketCnt = 1
                            while bracketCnt > 0:
                                line = next(fin)
                                if line is None:
                                    break
                                if '{' in line:
                                    bracketCnt += 1
                                if '}' in line:
                                    bracketCnt -= 1
                    fout.write(line)


def main(jarfile, jsonfile, destdir, versnew):
    
    if not os.path.isfile(jarfile):
        print('Error: File "'+jarfile+'" does not exist.')
        return 
    
    if destdir is None:
        print('Error: Destination dirctory is required. Try: '+os.path.basename(__file__)+' --help')
        return
    
    if versnew is None:
        print('Error: New version name is required. Try: '+os.path.basename(__file__)+' --help')
        return
    
    jarnew = os.path.join(destdir, versnew+'.jar')
    jsonnew = os.path.join(destdir, versnew+'.json')
    
    if os.path.isdir(destdir):
        line = raw_input('Warning: Destination "'+destdir+'" already exists. Continue? [Y/n]: ')
        if not line.startswith('y') and not line.startswith('Y'):
            return
    else:
        os.mkdir(os.path.join(destdir))
    
    if jsonfile is not None:
        
        if not os.path.isfile(jsonfile):
            print('Error: File "'+jsonfile+'" does not exist.')
            return
    
    modclasses = getfillclass(jarfile)
    if modclasses == []:
        print('Error: There does not appear to be a CommandFill class in this version.')
        return
    if len(modclasses) > 2:
        print('Warning: The jar has too many classes that match the fill/clone commands.')
    
    install(jarfile, jarnew, jsonfile, jsonnew, versnew, modclasses)


if __name__ == '__main__':
    if any(s in sys.argv for s in ['-h', '-help', '--help']):
        print('Usage:\n'+\
              '    no_fill_limit.py [dest_dir] [modded_basename] [mc_jar_file] [mc_json_file]\n'+
              'Example:\n'+\
              '    python no_fill_limit.py ~/.minecraft/versions/1.13-nolimit "1.13-nolimit" ~/.minecraft/versions/1.13/1.13.jar ~/.minecraft/versions/1.13/1.13.json')
        sys.exit(1)
    elif len(sys.argv) <= 3:
        destdir = raw_input('Enter destination directory: ').strip('"')
        versnew = raw_input('New basename for modded version: ').strip('"')
        jarfile = raw_input('Location of input minecraft version jar: ').strip('"')
        jsonfile = raw_input('(Optional) Location of input json: ').strip('"')
        if jsonfile is "":
            jsonfile = None
    else:
        destdir = sys.argv[1]
        versnew = sys.argv[2]
        jarfile = sys.argv[3]
        if len(sys.argv) <= 4:
            jsonfile = None
        else:
            jsonfile = sys.argv[4]
    main(jarfile, jsonfile, destdir, versnew) 

