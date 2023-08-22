import json
import httpx
import os
import zipfile
import hashlib
jsonurl='https://dl.google.com/dl/edgedl/chromeos/recovery/cloudready_recovery2.json'
print("getting available build info, please wait")
localjson=httpx.get(jsonurl).content
buildlist=json.loads(localjson)
info="Please select a build\n"
for build in buildlist:
    info=info+str(buildlist.index(build))
    for attrib in ['manufacturer','model','channel','version','chrome_version']:
        dispattr=json.dumps(build.get(attrib)).strip("\"")
        if (dispattr == "null"):
            dispattr="unknown"
        info=(info+"\t"+dispattr)
    info=info+"\n"
print(info)
dlindex=input()
dlurl=json.dumps(buildlist[int(dlindex)].get("url")).strip("\"")
filetoextract=json.dumps(buildlist[int(dlindex)].get("file")).strip("\"")
dlzipfile=dlurl.split("/")[-1]
md5=json.dumps(buildlist[int(dlindex)].get("md5")).strip("\"")
sha1=json.dumps(buildlist[int(dlindex)].get("sha1")).strip("\"")
zipfilesize=json.dumps(buildlist[int(dlindex)].get("zipfilesize")).strip("\"")
if os.path.exists(dlzipfile):
    print(dlzipfile+" already exists")
else:
    f=open(dlzipfile,"wb")
    print("Downloading "+dlzipfile+" from "+dlurl)
    with httpx.stream("GET",dlurl) as chunk:
        for writechunk in chunk.iter_bytes():
            f.write(writechunk)
            print(str(chunk.num_bytes_downloaded)+"/"+str(zipfilesize))
        f.close()
for checksumtype in ['md5','sha1']:
    f=open(dlzipfile,"rb")
    print("verifying "+dlzipfile+" "+checksumtype)
    match checksumtype:
        case "md5":
            hashconst=hashlib.md5
            comphash=md5
        case "sha1":
            hashconst=hashlib.sha1
            comphash=sha1
    filehash=hashlib.file_digest(f,hashconst).hexdigest()
    f.close()
    if(filehash==comphash):
        print("match! "+filehash)
    else:
        print("error! "+filehash+" does not match expected "+comphash)
        exit(128)
ziphandle=zipfile.ZipFile(dlzipfile)
for file in ziphandle.namelist():
    if os.path.exists(filetoextract):
        print(filetoextract+" already exists")
    else:
        if(file==filetoextract):
            print("Extracting "+filetoextract)
            ziphandle.extract(member=filetoextract)
ziphandle.close()
os.remove(dlzipfile)
