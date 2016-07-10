#!/usr/bin/env python
import sys
import os.path
import argparse
from Pytwcla import key

def main():    
    class MyParser(argparse.ArgumentParser):
        
        def print_help(self, file=None):
            if file is None:
                file = sys.stdout
            self._print_message('{0}\napi.ini is located at:\n{1}\n'.format(
                            self.format_help(),os.path.abspath(key._path_finder(
                            'userconfig','api.ini'))), file)
            
        
    parser = MyParser(prog='pytwcla')
    group = parser.add_mutually_exclusive_group()
    parser.add_argument("keyword", help="the search query")
    group.add_argument("-r", "--rest", 
                    help="search using the REST API",
                    action="store_true")
    group.add_argument("-s", "--stream", 
                    help="search using the Streaming API", 
                    action="store_true")
    group.add_argument("-j", "--join", help="join REST and Stream databases", 
                    action="store_true")
    group.add_argument("-c", "--csv", 
                    help="create csv files with daily keyword counts", 
                    action="store_true")
    args = parser.parse_args()
    kwd = key.query(args.keyword)
    if args.rest:
        kwd.rest_api()
        kwd.create_csv('rest')
    elif args.stream:
        try:
            kwd.stream_api()
        except KeyboardInterrupt:
            kwd.create_csv('stream')
    elif args.join:
        kwd.merge_db()
        kwd.create_csv('joined')    
    elif args.csv:
        kwd.create_csv('rest')
        kwd.create_csv('stream')
        kwd.create_csv('joined')
        
if __name__ == "__main__":
    main()