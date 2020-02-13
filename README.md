# ceril

- Assumes [SMILE](https://github.com/dwhuang/SMILE/releases/tag/v1.1.0) installed separately in _smiledir_, and soft-links from _smiledir_`/tablesetup` XML files to `ceril/tablesetup` XML files.  From within _smiledir_`/tablesetup`, create soft-links with a command like:

`ln -s ../../ceril/tablesetup/* ./`
`ln -s ../../ceril/tablesetup/stl/* ./stl/`

but be careful that files with the same names don't already exist in _smiledir_`/tablesetup`.  And omit the trailing `/` when removing soft-links to directories.

- With Intel graphics drivers, be sure to disable antialiasing in SMILE to avoid a null pointer crash.
