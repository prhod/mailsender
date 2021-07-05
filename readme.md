# mailsender

This component aims to ease sending mail.  
To use it using docker, first build the image:
```bash
docker build . -t mailsender
```  
then run using ENV parameters:
```bash
docker run  \
  -e HOST='smtp.host.com' \
  -e USERNAME='smtp_user' \
  -e PASSWORD='smtp_pwd'
  -e FROM='User Sending <sender@example.com>' \
  -e TO='User Receiving1 <user1@example.com>, User Receiving2 <user2@example.com>' \
  -e SUBJECT="My mail subject" \
  -e BODY_PLAIN="Plain text content" \
  -e BODY_HTML="HTML <b>text</b> content with image <img src=\"cid:image2.png\">" \
  -e ATTACHMENTS="/path/to/file1,/path/to/file2" \
  -e IMAGE_ATTACHMENTS="/path/to/image1.png,/path/to/image2.png" \
  mailsender
```

`IMAGE_ATTACHMENTS` is to be used for images included in the HTML body (using the file name). If you only want to attach the image file, use the `ATTACHMENTS` variable. 
As an early version, there may be unexpected behaviour if 2 files with the same name are added.

It is possible to provide HTML as a file with `BODY_HTML_FILE`. If the file does not exists, `BODY_HTML` will be used.