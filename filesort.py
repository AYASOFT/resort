#
# The MIT License
#
# Copyright (c) 2009 Matthew Maravillas
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import sys
import os
import shutil
import fnmatch
from datetime import datetime
import exif
import optparse

def main(options, args):
    path = args[0]
    
    files = fnmatch.filter(os.listdir(path), options.pattern)
        
    for file in files:
        current_path = os.path.join(path, file)
        
        date = None
        
        if options.use_exif:
            try:
                exif = read_exif(current_path)        
            except:
                print "%s could not be read" % path
            else:
                if exif:
                    date = datetime.strptime(str(exif["Image DateTime"]), "%Y:%m:%d %H:%M:%S")
                
                elif options.verbose:
                    print "No EXIF information found: %s" % path
                
        if not date:
            date = get_modification_date(current_path)
        
        new_directory = os.path.join(os.path.split(path)[0],
                                     str(date.year), 
                                     "%02d" % date.month)
        
        if not os.access(new_directory, os.F_OK):
            os.makedirs(new_directory)
                
        if options.verbose:
            print "Moving", file , "to", new_directory
        
        shutil.move(current_path, os.path.join(new_directory, file))

def read_exif(path):
    file = open(path, 'rb')
    
    data = exif.process_file(file)
    
    return data
    
def get_modification_date(path):
    return datetime.fromtimestamp(os.stat(path).st_mtime)

def usage():
    print "Usage: %s <directory>" % (os.path.basename(sys.argv[0]))
    
if __name__ == "__main__":
    parser = optparse.OptionParser("Usage: %prog [options] path")
    
    parser.add_option("-x", "--ignore-exif", dest="use_exif",
                      action="store_false", help="ignore any EXIF dates found")
    parser.add_option("-p", "--pattern", dest="pattern",
                      help="file pattern to match")
    parser.add_option("-v", "--verbose", dest="verbose",
                      action="store_true", help="verbose output")
    
    parser.set_defaults(use_exif=True, pattern="*.*", verbose=False)
    
    (options, args) = parser.parse_args()
    
    if len(args) != 1:
        parser.error("Missing path argument")
    
    if options.verbose:
        if options.use_exif:
            print "Using EXIF dates"
        
        print "File pattern:", options.pattern
           
    main(options, args)
