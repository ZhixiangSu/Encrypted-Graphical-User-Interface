# NaClProfile.py
# An encrypted version of the Profile class provided by the Profile.py module
# 
# for ICS 32
# by Mark S. Baldwin


# TODO: Install the pynacl library so that the following modules are available
# to your program.
import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box
import json, time, os
from pathlib import Path
import copy

from typing import List

# TODO: Import the Profile and Post classes
from Profile import Profile,Post,DsuProfileError,DsuFileError
# TODO: Import the NaClDSEncoder module
from NaClDSEncoder import NaClDSEncoder
# TODO: Subclass the Profile class
class NaClProfile(Profile):
    def __init__(self,keypair=None):
        """
        TODO: Complete the initializer method. Your initializer should create the follow three 
        public data attributes:

        public_key:str
        private_key:str
        keypair:str

        Whether you include them in your parameter list is up to you. Your decision will frame 
        how you expect your class to be used though, so think it through.
        """
        super(NaClProfile,self).__init__()
        self.keypair=keypair
        self.public_key=None
        self.private_key =None
        if self.keypair is None:
            self.generate_keypair()
        else:
            self.public_key,self.private_key=self.decode_keypair(self.keypair)



    def decode_keypair(self,keypair:str):
        public_key=keypair[:44]
        private_key=keypair[44:]
        return public_key,private_key

    def generate_keypair(self) -> str:
        """
        Generates a new public encryption key using NaClDSEncoder.

        TODO: Complete the generate_keypair method.

        This method should use the NaClDSEncoder module to generate a new keypair and populate
        the public data attributes created in the initializer.

        :return: str    
        """
        # create an NaClDSEncoder object
        nacl_enc = NaClDSEncoder()
        # generate new keys
        nacl_enc.generate()
        assert len(nacl_enc.keypair)==88
        assert nacl_enc.public_key==nacl_enc.keypair[:44]
        assert nacl_enc.private_key==nacl_enc.keypair[44:]
        self.keypair=nacl_enc.keypair
        self.public_key=nacl_enc.public_key
        self.private_key=nacl_enc.private_key
        return nacl_enc.keypair


    def import_keypair(self, keypair: str):
        """
        Imports an existing keypair. Useful when keeping encryption keys in a location other than the
        dsu file created by this class.

        TODO: Complete the import_keypair method.

        This method should use the keypair parameter to populate the public data attributes created by
        the initializer. 
        
        NOTE: you can determine how to split a keypair by comparing the associated data attributes generated
        by the NaClDSEncoder
        """
        self.keypair=keypair
        self.public_key,self.private_key=self.decode_keypair(keypair)

    """
    TODO: Override the add_post method to encrypt post entries.

    Before a post is added to the profile, it should be encrypted. Remember to take advantage of the
    code that is already written in the parent class.

    NOTE: To call the method you are overriding as it exists in the parent class, you can use the built-in super keyword:
    
    super().add_post(...)
    """

    def add_post(self, post: Post) -> None:
        nacl_enc = NaClDSEncoder()
        box = nacl_enc.create_box(nacl_enc.encode_private_key(self.private_key),
                                            nacl_enc.encode_public_key(self.public_key))

        post.entry=nacl_enc.encrypt_message(box,post.entry)
        super(NaClProfile, self).add_post(post)
    """
    TODO: Override the get_posts method to decrypt post entries.

    Since posts will be encrypted when the add_post method is used, you will need to ensure they are 
    decrypted before returning them to the calling code.

    :return: Post
    
    NOTE: To call the method you are overriding as it exists in the parent class you can use the built-in super keyword:
    super().get_posts()
    """
    def get_posts(self):
        nacl_enc = NaClDSEncoder()
        box = nacl_enc.create_box(nacl_enc.encode_private_key(self.private_key),
                                  nacl_enc.encode_public_key(self.public_key))
        posts=super(NaClProfile, self).get_posts()
        new_posts=copy.deepcopy(posts)
        for post in new_posts:
            post.entry=nacl_enc.decrypt_message(box,post.entry)
        return new_posts
    """
    TODO: Override the load_profile method to add support for storing a keypair.

    Since the DS Server is now making use of encryption keys rather than username/password attributes, you will 
    need to add support for storing a keypair in a dsu file. The best way to do this is to override the 
    load_profile module and add any new attributes you wish to support.

    NOTE: The Profile class implementation of load_profile contains everything you need to complete this TODO.
     Just copy the code here and add support for your new attributes.
    """
    def load_profile(self, path: str) -> None:
        p = Path(path)

        if os.path.exists(p) and p.suffix == '.dsu':
            try:
                f = open(p, 'r')
                obj = json.load(f)
                self.username = obj['username']
                self.password = obj['password']
                self.dsuserver = obj['dsuserver']
                self.private_key=obj['private_key']
                self.public_key = obj['public_key']
                self.keypair=self.public_key+self.private_key
                self.bio = obj['bio']
                for post_obj in obj['_posts']:
                    post = Post(post_obj['entry'], post_obj['timestamp'])
                    self._posts.append(post)
                f.close()
            except Exception as ex:
                raise DsuProfileError(ex)
        else:
            raise DsuFileError()
    def encrypt_entry(self, entry:str, public_key:str) -> bytes:
        """
        Used to encrypt messages using a 3rd party public key, such as the one that
        the DS server provides.
        
        TODO: Complete the encrypt_entry method.

        NOTE: A good design approach might be to create private encrypt and decrypt methods that your add_post, 
        get_posts and this method can call.
        
        :return: bytes 
        """
        nacl_enc = NaClDSEncoder()
        new_box = nacl_enc.create_box(nacl_enc.encode_private_key(self.private_key),
                                            nacl_enc.encode_public_key(public_key))
        encrypt_entry=nacl_enc.encrypt_message(new_box,entry)
        return encrypt_entry.encode(encoding='UTF-8')