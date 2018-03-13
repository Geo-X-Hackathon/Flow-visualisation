# Flow-visualisation
Visualising flows from LEMs using leaflet-velocity


## Instructions to run the demo

An example of input is given with the files `velocity_field.hdr` and
`velocity_field.txt`. The former contains grid metadata (ESRI ASCII
grid format + an additional entry that specifies the projection system
used), and the latter contains velocity data (two columns, i.e., for
`u` and `v` components)

Run the python script to convert the input data into a
leaflet-velocity compatible (json) format (you need Python 3, Pandas,
PyProj and pyresample installed in your system):

```
$ python velocity2json.py velocity_field
```

Then open the file `demo/demo.html` in your browser.
