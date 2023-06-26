# secretsend
simple and secure service to send a password to someone
gone are the days of archaically sending passwords over plaintext email and hoping it doens't get stolen


## How does it work? 
Simply visit send.liem.zip and enter a password and select when you want it to expire.


## But can you see my passwords?
***NO! Never!!***
**tldr; three layers of security**
1. In browser, it will randomly generate a url-safe key
2. It will encrypt your password with that key (still in-browser).
3. It will send that encrypted password to my backend server (just a really basic rest api to an encrypted db).
4. Then, it'll spit out a URL with an id and the key encoded into it for easy sending

yes this is a monorepo because I hate making things simple for the sake of somewhat worthless organization
