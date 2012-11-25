import socket
import urllib2
import urlparse
import os
import os.path
import shutil
from hashlib import md5


def url2name(url):
    return os.path.basename(urlparse.urlsplit(url)[2])


def download(url,
            FileName=None,
            FileSize=None,
            path=None,
            skip=lambda x: False):
    """Saves file from url
        @param url        File url. Will use urllib2 to obtain it.
        @param FileName Force file name. If None file name will be detected.
        @param FileSize Size of previously downloaded file. Will skip url
            if file FileName exists and it's size equal to FileSize
        @param path        Where to put downloaded file
        @param skip        Will skip url if skip(name) returns True, where
            name is FileName or automaticly detected name
        @returns        tuple(ResultingFileName, DownloadedFileSize)
    """
    if path is None:
        path = ''
    if FileName is None:
        FileName = ''
    localName = ''

    # maybe there is nothing we should do:
    if FileName:
        if skip(FileName):
            return None
        if FileSize:
            name = os.path.join(path, FileName)
            if os.path.exists(name) and FileSize == os.path.getsize(name):
                return FileName, FileSize
    else:
        localName = url2name(url)
        if skip(localName):
            return None

    r = None

    # ok, we have to ask server...
    try:
        r = urllib2.urlopen(url)
    except urllib2.URLError:
        print('Error downloading file %s' % (FileName))
        return None

    if 'Content-Disposition' in r.info():
        # If the response has Content-Disposition, we take file name from it
        localName = r.info()['Content-Disposition'].split('filename=')[1]
        if localName[0] == '"' or localName[0] == "'":
            localName = localName[1:-1]
    elif r.url != url:
        # if we were redirected, the real file name we take from the final URL
        localName = url2name(r.url)
    localName = urllib2.unquote(localName).decode('utf8')

    # Trying to catch html-redirections and folder links
    if len(localName) == 0 and 'Content-Type' in r.info() \
        and r.info()['Content-Type'].startswith('text/html;'):
        return None

    if FileName:
        # we can force to save the file as specified name
        localName = FileName

    finalLocalName = os.path.join(path, localName)

    if skip(finalLocalName):
        return None

    folders = finalLocalName.split(os.path.sep)[:-1]
    folders = os.path.sep.join(folders)

    if not os.path.exists(folders):
            os.makedirs(folders)

    print(localName)
    rsize = int(r.info().get('content-length'))
    if os.path.exists(finalLocalName):
        if rsize == os.path.getsize(finalLocalName):
            r.close
            return localName, rsize
    try:
        # save to temp '*.part' file
        f = open(finalLocalName + '.part', 'wb')
    except IOError:
        # bad filename?
        ext = os.path.splitext(localName)[1]
        localName = md5(localName).hexdigest() + ext
        print 'Bad filename?', 'Using %s' % localName
        finalLocalName = os.path.join(path, localName)
        f = open(finalLocalName + '.part', 'wb')
    try:
        shutil.copyfileobj(r, f)
        os.rename(finalLocalName + '.part', finalLocalName)
    except socket.error:
        print('Error downloading %s' % finalLocalName)
        r.close()
        return None
    finally:
        f.close()
    r.close()
    return localName, os.path.getsize(finalLocalName)
