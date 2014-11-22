#!/usr/bin/env python
import os.path
import base64


class CovertChannel(object):

    #-------------------------------------------
    # Initializer
    #-------------------------------------------
    def __init__(self):
        self.div_tag = '<div id="bottom-tag" style="display:none;">'
        self.encode_status = True
        self.html_file = None
        self.secret_file = None
        self.html_clean = None
        self.html_encoded = None
        self.binary_encoded = None
        self.binary_decoded = None
        self.body_tag = None
        self.secret_tag = None
        self.files_path = os.path.join((os.path.dirname(os.path.abspath(__file__))),
                                       '..','files')
    
    #-------------------------------------------
    # Get encoding status: encode or decode
    #-------------------------------------------    
    def get_encoding_status(self, encode=True):
        self.encode_status = encode
    
    #-------------------------------------------
    # Set secret file to write binary
    #-------------------------------------------    
    def set_secret_file(self, secret_file):
        self.secret_file = secret_file
    
    #-------------------------------------------
    # Check if file exists
    #-------------------------------------------    
    def file_exists(self, file_path):
        path = os.path.join(self.files_path,file_path)
        return os.path.isfile(path)       
    
    #-------------------------------------------
    # Read HTML file
    #-------------------------------------------    
    def _read_html_file(self, file_name, clean=True):
        lines = []
        with open(file_name, 'r') as f:
            lines = f.readlines()           
        stripped = []
        for line in lines:
            stripped.append(line.rstrip())  
        if clean:
            self.html_clean = stripped
        else:
            self.html_encoded = stripped

    #-------------------------------------------
    # Get HTML file
    #-------------------------------------------
    def get_html_file(self, file_name, clean=True):
        self.html_file = os.path.join(self.files_path, file_name)
        self._read_html_file(self.html_file, clean=clean)

    #-------------------------------------------
    # Read binary file
    #-------------------------------------------        
    def _read_file(self, file_name):
        lines = []
        data = None
        with open(file_name, 'rb') as f:
            data = f.read()  
        encoded_string = base64.urlsafe_b64encode(data)
        self.binary_encoded = encoded_string
     
    #-------------------------------------------
    # Decode binary file
    #-------------------------------------------   
    def _decode_binary(self):
        encoded_key = self.binary_encoded
        encoded_key += "=" * ((4 - len(encoded_key) % 4) % 4)
        try:
            self.binary_decoded = base64.urlsafe_b64decode(str(encoded_key))
        except Exception,e:
            print e
            self.binary_decoded = None
        return self.binary_decoded
    
    #-------------------------------------------
    # Write binary to file
    #-------------------------------------------
    def _write_binary_to_file(self):
        secret_file = os.path.join(self.files_path, self.secret_file)
        with open(secret_file, 'wb') as f:
            f.write(self.binary_decoded)
    
    #-------------------------------------------
    # Get secret file - file to be encrypted
    #-------------------------------------------        
    def get_secret_file(self, file_name):
        self.secret_file = os.path.join(self.files_path, file_name)
        self._read_file(self.secret_file)
    
    #-------------------------------------------
    # Get body tag </body>
    #-------------------------------------------    
    def _get_body_tag(self):
        tag = None        
        if not self.html_clean:
            self.body_tag = -1
            return -1
        else:
            count = 0
            for line in self.html_clean:
                if '</body>' in line:
                    self.body_tag = count 
                    return count
                count += 1
            self.body_tag = -1
            return self.body_tag
  
    #-------------------------------------------
    # Secret tag - where to insert the secret message
    # Add secret to index 2
    #-------------------------------------------
    def _secret_tag(self):
        tag_list = [] 
        tag_list.append(self.div_tag) 
        tag_list.append('<p>')
        tag_list.append('')
        tag_list.append('</p>')
        tag_list.append('</div>')
        return tag_list
    
    #-------------------------------------------
    # Add base64 encoded binary to secret tag
    #-------------------------------------------
    def _add_encoded_to_secret_tag(self):
        tag = self._secret_tag()
        tag[2] = self.binary_encoded
        return tag
    
    #-------------------------------------------
    # Append HTML tag to HTML file
    #-------------------------------------------
    def _append_to_html(self, location, tag_list):
        self.html_encoded = self.html_clean
        self.html_encoded[location:location] = tag_list
    
    #-------------------------------------------
    # Write encoded HTML to file
    #-------------------------------------------    
    def _write_encoded_html_to_file(self):
        html_file = os.path.join(self.files_path, self.html_file)
        with open(html_file, 'w') as f:
            for line in self.html_encoded:
                f.write('{}\n'.format(line))
    
    #-------------------------------------------
    # Find secret tag <div id="...">
    #-------------------------------------------            
    def _find_secret_tag(self):
        count = 0
        for line in self.html_encoded:
            if self.div_tag in line:
                self.secret_tag = count
                return count
            count += 1
        self.secret_tag = -1
        return self.secret_tag
    
    #-------------------------------------------
    # Remove encodings from HTML file
    #-------------------------------------------            
    def _clean_html(self):
        self.html_encoded[self.secret_tag] = '</body>'
        self.html_encoded[self.secret_tag+1] = '</html>'
        self.html_clean = self.html_encoded[0:self.secret_tag+2]
        html_file = os.path.join(self.files_path, self.html_file)
        with open(html_file, 'w') as f:
            for line in self.html_clean:
                f.write('{}\n'.format(line))
               
    #-------------------------------------------
    # Print list to console
    #-------------------------------------------            
    def print_file_list(self, file_list):
        for line in file_list:
            print '[{}]'.format(line)

    #-------------------------------------------
    # RUN - main run method
    #-------------------------------------------
    def run(self):
        if self.encode_status:
            print 'Encoding into HTML...'
            tag_index = self._get_body_tag()
            extra_tag = self._add_encoded_to_secret_tag()
            self._append_to_html(tag_index, extra_tag)
            self._write_encoded_html_to_file()
            print 'Done'
        else:
            print 'Decoding from HTML...'
            tag_index = self._find_secret_tag()
            self.binary_encoded = self.html_encoded[tag_index+2]
            self._decode_binary()
            self._write_binary_to_file()
            self._clean_html()
            print 'Done'
            
#-------------------------------------------
# MAIN
#-------------------------------------------    
def main(): 
    menu="""-------- Menu --------:
1) Encode covert channel (encode file into HTML)
2) Decode covert channel (decode HTML)
3) Exit"""

    print menu

    input = 0
    while not 0 < input < 4:
        try:
            input = int(raw_input("> "))
        except ValueError:
            print "Invalid entry!"
            continue
    
    channel = CovertChannel()
        
    print 'NOTE: Put files into files directory and enter only file name'
    if input == 1:
        channel.get_encoding_status(True)
        html_file = raw_input("Enter HTML file name > ")
        secret_file = raw_input("Enter secret file name > ")
        while not (channel.file_exists(html_file) and channel.file_exists(secret_file)):
            print 'Make sure both file names are correct!'
            html_file = raw_input("Enter HTML file name > ")
            secret_file = raw_input("Enter secret file name > ")
        channel.get_html_file(html_file)
        channel.get_secret_file(secret_file)

    elif input == 2:
        channel.get_encoding_status(False)
        encoded_html_file = raw_input("Enter encoded HTML file name > ")
        secret_file = raw_input("Enter output file name > ")
        while not channel.file_exists(encoded_html_file):
            print 'Make sure HTML file name is correct!'
            encoded_html_file = raw_input("Enter HTML file name > ")
            secret_file = raw_input("Enter output file name > ")
        channel.get_html_file(encoded_html_file, clean=False)
        channel.set_secret_file(secret_file)
    elif input ==3:
        return

    channel.run()  

if __name__=="__main__":
    main()
    
