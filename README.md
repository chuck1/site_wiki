# django markdown wiki

## TODO

- still need to protect against multiple users clicking edit at the same time and the
  server then trying to modify the same working directory at the same time from different threads
- handle relative and absolute paths differently
- detect trailing '/' in path name and navigate to an index file in that folder
- ~~create optional auto generated list of links to immediate child folders. the list shall go in a leftbar.
  also add a link somewhere to the parent folder.~~
- create cancel button on edit page
- when the entered path point to non-existant file, navigate to an edit page for the new file.
  maybe rename the submit button to "create" for this case
- create script to copy documentation of python modules into the wiki.
- move md files to source and html files to build.
- add info to Patch object
    - user
	- commit string
- add read and write permission options to Page objects
- add functionality to automatrically number headings in file and across multiple files and folders
  with a particular root folder
